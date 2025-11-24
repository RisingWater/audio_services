from pydantic import BaseModel
from typing import Optional

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "zh-CN-XiaoxiaoNeural"  # 默认中文女声
    volume: Optional[float] = 1.0                  # 音量

class TTSResponse(BaseModel):
    session_id: str
    status: str
    message: str

class VoiceInfo(BaseModel):
    name: str
    short_name: str
    gender: str
    locale: str