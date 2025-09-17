from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    orchestrator_port: int = 8500  
    stt_url: str = "http://stt-service:8002/transcribe"
    llm_url: str = "http://llm-service:8000/command"
    validator_url: str = "http://robot-validator:8001/execute_command"
    tts_url: str = "http://tts-service:8003/speak"
    service_name: str = "orchestrator"
    log_level: str = "INFO"
    enable_tracing: bool = False
    otlp_endpoint: str | None = None
    enable_metrics: bool = True
    correlation_header: str = "X-Correlation-ID"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
