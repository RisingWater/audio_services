from pydantic import BaseModel
from typing import List, Dict, Optional

class TTSSessionStatus(BaseModel):
    session_id: str
    status: str
    text: str
    voice: str
    volume: float = 1.0
