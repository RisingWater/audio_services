import os
import logging
from typing import Dict, Optional, List

from managers.tts_session import TTSSession

logger = logging.getLogger(__name__)

class AudioManager:
    def __init__(self):
        self.tts_sessions: Dict[str, TTSSession] = {}
        self.playlist_session: Optional[PlaylistSession] = None
    
    def create_tts_session(self, text: str, voice: str, volume: float = 1.0) -> TTSSession:
        session = TTSSession(text, voice, volume)
        self.tts_sessions[session.session_id] = session
        return session
    
    def get_all_tts_sessions(self) -> List[TTSSession]:
        return list(self.tts_sessions.values())

    def get_tts_session(self, session_id: str) -> Optional[TTSSession]:
        return self.tts_sessions.get(session_id)
    
    def cleanup_old_sessions(self):
        for session_id, session in self.tts_sessions.items():
            if session.is_finished():
                self.tts_sessions.pop(session_id, None)

# 全局音频管理器实例
audio_manager = AudioManager()