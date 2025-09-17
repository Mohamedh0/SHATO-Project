from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    orchestrator_port: int = 8500  
    stt_url: str
    llm_url: str
    validator_url: str
    tts_url: str
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
