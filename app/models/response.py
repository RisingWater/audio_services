from pydantic import BaseModel
from typing import List, Dict, Optional

class TTSSessionStatus(BaseModel):
    session_id: str
    status: str
    text: str
    voice: str
    volume: float = 1.0

class PlaylistElement(BaseModel):
    url: str
    name: str
    id: str

class MusicSessionStatus(BaseModel):
    session_id: str
    status: str
    url: str
    volume: float = 1.0
    current_time: float = 0.0      # 当前播放时间（秒）
    duration: float = 0.0          # 总时长（秒）
    progress: float = 0.0          # 播放进度百分比 (0.0-1.0)
    is_paused: bool = False

class PlayListSessionStatus(BaseModel):
    session_id: str
    id: str
    status: str
    playlist: List[PlaylistElement]  # 使用 PlaylistElement 列表
    current_index: int = 0           # 当前播放的歌曲索引
    current_song_status: Optional[MusicSessionStatus] = None  # 当前歌曲的播放状态
    volume: float = 1.0
    is_playing: bool = False
    playlist_length: int = 0         # 播放列表长度