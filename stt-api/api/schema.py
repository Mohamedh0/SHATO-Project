from pydantic import BaseModel

class HealthResponse(BaseModel):
    message: str

class TranscribeResponse(BaseModel):
    id_correlation: str
    text: str
