from pydantic import BaseModel

class TTSSessionStatus(BaseModel):
    session_id: str
    status: str
    text: str
    voice: str
    volume: float = 1.0
