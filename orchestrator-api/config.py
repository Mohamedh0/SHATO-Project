from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    orchestrator_port: int = 8500  # ✅ default value added
    stt_url: str
    llm_url: str
    validator_url: str
    tts_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
