from pydantic import BaseModel
from typing import Optional

class TTSSessionStatus(BaseModel):
    session_id: str
    status: str
    text: str
    voice: str
    volume: float = 1.0

class MusicSessionStatus(BaseModel):
    session_id: str
    status: str
    url: Optional[str] = ""
    file_path: Optional[str] = ""
    volume: float = 1.0
