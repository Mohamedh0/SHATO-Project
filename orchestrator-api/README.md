# Orchestrator Service

Orchestrates the STT -> LLM -> Validator -> TTS pipeline.

## Observability & Logging

- Structured JSON logs via `structlog` with correlation IDs.
- Correlation ID header: `X-Correlation-ID` (configurable via `correlation_header`).
- Each incoming request is assigned/propagates a correlation ID. Downstream calls include this header.
- Global error handlers return consistent error schema:

```json
{
  "error": {
    "type": "HTTPException",
    "message": "...",
    "correlation_id": "..."
  }
}
```

## Metrics

- Prometheus metrics exposed at `/metrics` (not in OpenAPI schema).
- Toggle with `enable_metrics` setting (default: true).

## Tracing (optional)

- Enable with `enable_tracing=true`. Configure OTLP endpoint via `otlp_endpoint`.
- Auto-instrumentation for FastAPI and httpx when enabled.

## Configuration (.env)

```
stt_url=http://stt:8001/transcribe
llm_url=http://llm:8002/infer
validator_url=http://validator:8003/execute
tts_url=http://tts:8004/speak
service_name=orchestrator
log_level=INFO
enable_tracing=false
otlp_endpoint=http://otel-collector:4318/v1/traces
enable_metrics=true
correlation_header=X-Correlation-ID
```

## Orchestration Conventions

- Always forward the correlation header from inbound request to all downstream requests.
- Log `request_start`, `request_end`, and downstream `service_call_*` events.
- All inter-service failures are converted to structured errors with the correlation ID for traceability.


