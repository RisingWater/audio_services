from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uuid
import subprocess
import queue

class PlaybackSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.process: Optional[subprocess.Popen] = None
        self.filename: Optional[str] = None
        self.format: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.volume: float = 1.0
        self.status: str = "created"
        self.is_stream: bool = False

class StreamSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.process: Optional[subprocess.Popen] = None
        self.input_queue: queue.Queue = queue.Queue()
        self.status: str = "created"
        self.start_time: Optional[datetime] = None
        self.volume: float = 1.0