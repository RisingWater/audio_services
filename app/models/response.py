from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PlayResponse(BaseModel):
    session_id: str
    status: str
    filename: str
    message: str

class StreamResponse(BaseModel):
    session_id: str
    status: str
    message: str

class SessionStatus(BaseModel):
    session_id: str
    status: str
    filename: Optional[str] = None
    format: Optional[str] = None
    start_time: Optional[str] = None
    duration: Optional[float] = None
    volume: float = 1.0
    is_stream: bool = False

class VolumeControl(BaseModel):
    volume: float = 1.0