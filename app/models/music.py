from pydantic import BaseModel
from typing import Optional

class MusicRequest(BaseModel):
    url: str
    volume: Optional[float] = 1.0

class MusicResponse(BaseModel):
    session_id: str
    status: str
    message: str
