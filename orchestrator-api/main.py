# orchestrator.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from typing import Optional, Callable
import httpx
import uuid
import time
import contextvars
import structlog
import logging

from config import settings


# ---------- Logging / Observability Setup ----------

correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")

def configure_logging() -> None:
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger(settings.service_name)


def get_correlation_id(request: Request) -> str:
    header_name = settings.correlation_header
    cid = request.headers.get(header_name) or str(uuid.uuid4())
    correlation_id_ctx.set(cid)
    structlog.contextvars.bind_contextvars(correlation_id=cid)
    return cid


def correlation_header() -> tuple[str, str]:
    cid = correlation_id_ctx.get() or str(uuid.uuid4())
    return settings.correlation_header, cid


def init_tracing(app: FastAPI) -> None:
    if not settings.enable_tracing:
        return
    try:
        from opentelemetry import trace  # type: ignore
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore
        from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource  # type: ignore
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore

        resource = Resource.create({SERVICE_NAME: settings.service_name})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint) if settings.otlp_endpoint else OTLPSpanExporter()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        FastAPIInstrumentor.instrument_app(app)
        HTTPXClientInstrumentor().instrument()
        logger.info("tracing_initialized", endpoint=settings.otlp_endpoint)
    except Exception as e:
        logger.warning("tracing_init_failed", error=str(e))


def init_metrics(app: FastAPI) -> None:
    if not settings.enable_metrics:
        return
    try:
        from prometheus_fastapi_instrumentator import Instrumentator  # type: ignore

        Instrumentator().instrument(app).expose(app, include_in_schema=False)
        logger.info("metrics_initialized")
    except Exception as e:
        logger.warning("metrics_init_failed", error=str(e))


app = FastAPI(title="Orchestrator Service", version="1.0.0")


# ---------- Middleware ----------

@app.middleware("http")
async def correlation_and_logging_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    cid = get_correlation_id(request)
    structlog.contextvars.bind_contextvars(path=str(request.url.path), method=request.method)
    logger.info("request_start")
    try:
        response = await call_next(request)
    except Exception as exc:  # Let global handlers manage it, but log timing and context
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error("request_exception", duration_ms=duration_ms, error=str(exc))
        raise
    duration_ms = int((time.time() - start_time) * 1000)
    # Ensure header is set on the response (some responses may not have headers object)
    try:
        response.headers[settings.correlation_header] = cid
    except Exception:
        # if response doesn't allow header mutation, ignore but keep logging
        logger.warning("response_headers_not_mutable")
    logger.info("request_end", status_code=response.status_code, duration_ms=duration_ms)
    return response


# ---------- Request / Response Schemas (Pydantic v2) ----------

class InferRequest(BaseModel):
    text: str
    correlation_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")  # forbid unexpected extras


class ExecuteRequest(BaseModel):
    command: str
    command_params: dict
    correlation_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class SpeakRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = None
    correlation_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


# ---------- Utility ----------

async def call_service(method: str, url: str, **kwargs):
    """
    Generic helper to call downstream services using httpx.AsyncClient.
    Raises HTTPException if service call fails.
    """
    header_key, header_val = correlation_header()
    headers = kwargs.pop("headers", {}) or {}
    headers.setdefault(header_key, header_val)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        try:
            resp = await client.request(method, url, **kwargs)
            resp.raise_for_status()
            # attempt to decode json; if not JSON, return text
            try:
                data = resp.json()
            except ValueError:
                data = {"text": resp.text}
            logger.info("service_call_success", method=method, url=url, status=resp.status_code)
            return data
        except httpx.RequestError as e:
            logger.error("service_call_request_error", method=method, url=url, error=str(e))
            raise HTTPException(status_code=503, detail=f"Service unreachable: {url} ({e})")
        except httpx.HTTPStatusError as e:
            # prefer using the response on the exception
            resp = getattr(e, "response", None)
            body = None
            status_code = None
            if resp is not None:
                status_code = resp.status_code
                try:
                    body = resp.text
                except Exception:
                    body = "<unreadable response body>"
            logger.error(
                "service_call_http_error",
                method=method,
                url=url,
                status=status_code,
                body=body,
            )
            # surface the service's error text when available
            raise HTTPException(status_code=status_code or 502, detail=f"Service returned error: {body or str(e)}")


# ---------- Endpoints ----------

@app.get("/")
async def root():
    """Basic health check."""
    return {"message": "Orchestrator service is running"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Send audio to STT service and return transcription."""
    files = {"audio": (audio.filename, await audio.read(), audio.content_type)}
    result = await call_service("POST", settings.stt_url, files=files)
    return result


@app.post("/infer")
async def infer(request: InferRequest):
    """Send text to LLM service to get command + params."""
    payload = request.model_dump(exclude_none=True)
    result = await call_service("POST", settings.llm_url, json=payload)
    return result


@app.post("/execute")
async def execute(request: ExecuteRequest):
    """Send command to validator service to check if it's valid."""
    payload = request.model_dump(exclude_none=True)
    # Remove correlation_id if present so validator with extra="forbid" won't reject
    payload.pop("correlation_id", None)
    result = await call_service("POST", settings.validator_url, json=payload)
    return result


@app.post("/speak")
async def speak(request: SpeakRequest):
    """Send text to TTS service and get back audio."""
    payload = request.model_dump(exclude_none=True)
    # keep correlation header at HTTP header level (call_service already adds it)
    payload.pop("correlation_id", None)
    result = await call_service("POST", settings.tts_url, json=payload)
    return result


@app.post("/voice_flow")
async def voice_flow(audio: UploadFile = File(...)):
    """
    Full pipeline:
    1. Transcribe audio -> text
    2. Send text to LLM -> command
    3. Validate command
    4. Synthesize response to speech
    """
    # Step 1: Transcribe
    files = {"audio": (audio.filename, await audio.read(), audio.content_type)}
    stt_result = await call_service("POST", settings.stt_url, files=files)

    text = stt_result.get("text")
    if not text:
        raise HTTPException(status_code=500, detail="STT service did not return text")

    # Step 2: LLM inference
    current_cid = correlation_id_ctx.get() or str(uuid.uuid4())
    llm_payload = {"text": text, "correlation_id": current_cid}
    llm_result = await call_service("POST", settings.llm_url, json=llm_payload)

    # Step 3: Validation
    validator_payload = llm_result.copy() if isinstance(llm_result, dict) else {}
    validator_payload.pop("correlation_id", None)
    validator_result = await call_service("POST", settings.validator_url, json=validator_payload)

    # Step 4: TTS
    tts_payload = {"text": text}
    tts_result = await call_service("POST", settings.tts_url, json=tts_payload)

    return {
        "stt": stt_result,
        "llm": llm_result,
        "validator": validator_result,
        "tts": tts_result,
    }


# ---------- Global Error Handlers ----------

def error_response(message: str, status_code: int, error_type: str = "Error") -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": error_type,
                "message": message,
                "correlation_id": correlation_id_ctx.get() or "",
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("http_exception", status_code=exc.status_code, detail=str(exc.detail))
    return error_response(str(exc.detail), exc.status_code, error_type="HTTPException")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", error=str(exc))
    return error_response("Internal server error", 500, error_type="InternalServerError")


# ---------- Startup Hooks ----------

@app.on_event("startup")
async def on_startup():
    configure_logging()
    init_tracing(app)
    init_metrics(app)
    logger.info("startup_complete")
