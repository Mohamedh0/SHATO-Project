from pydantic import BaseModel

class HealthResponse(BaseModel):
    message:str

class TranscribeResponse(BaseModel):
    text:str