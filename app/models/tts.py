from pydantic import BaseModel
from typing import Optional, List

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "zh-CN-XiaoxiaoNeural"  # 默认中文女声
    rate: Optional[str] = "+0%"                    # 语速
    volume: Optional[str] = "+0%"                  # 音量
    volume_level: Optional[float] = 0.8           # 播放音量
    stream: Optional[bool] = False                # 是否流式播放

class TTSResponse(BaseModel):
    session_id: str
    status: str
    text_length: int
    voice: str
    message: str

class VoiceInfo(BaseModel):
    name: str
    short_name: str
    gender: str
    locale: str