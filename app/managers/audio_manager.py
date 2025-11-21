import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
import subprocess

from models.session import PlaybackSession, StreamSession
from config import settings

logger = logging.getLogger(__name__)

class AudioManager:
    def __init__(self):
        self.sessions: Dict[str, PlaybackSession] = {}
        self.stream_sessions: Dict[str, StreamSession] = {}
    
    def create_session(self) -> PlaybackSession:
        import uuid
        session_id = str(uuid.uuid4())
        session = PlaybackSession(session_id)
        self.sessions[session_id] = session
        return session
    
    def create_stream_session(self) -> StreamSession:
        import uuid
        session_id = str(uuid.uuid4())
        session = StreamSession(session_id)
        self.stream_sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[PlaybackSession]:
        return self.sessions.get(session_id)
    
    def get_stream_session(self, session_id: str) -> Optional[StreamSession]:
        return self.stream_sessions.get(session_id)
    
    def stop_session(self, session_id: str):
        session = self.get_session(session_id)
        if session and session.process and session.process.poll() is None:
            try:
                session.process.terminate()
                session.process.wait(timeout=5)
                session.status = "stopped"
                session.end_time = datetime.now()
            except subprocess.TimeoutExpired:
                session.process.kill()
                session.status = "killed"
    
    def stop_stream_session(self, session_id: str):
        session = self.get_stream_session(session_id)
        if session and session.process and session.process.poll() is None:
            try:
                session.process.terminate()
                session.process.wait(timeout=5)
                session.status = "stopped"
            except subprocess.TimeoutExpired:
                session.process.kill()
                session.status = "killed"
    
    def cleanup_session(self, session_id: str):
        session = self.get_session(session_id)
        if session:
            self.stop_session(session_id)
            if session.filename and os.path.exists(session.filename):
                try:
                    os.unlink(session.filename)
                except:
                    pass
            self.sessions.pop(session_id, None)
    
    def cleanup_stream_session(self, session_id: str):
        session = self.get_stream_session(session_id)
        if session:
            self.stop_stream_session(session_id)
            self.stream_sessions.pop(session_id, None)
    
    def get_all_sessions(self) -> List[PlaybackSession]:
        return list(self.sessions.values())
    
    def get_all_stream_sessions(self) -> List[StreamSession]:
        return list(self.stream_sessions.values())
    
    def cleanup_old_sessions(self):
        """清理过期的会话"""
        current_time = datetime.now()
        
        # 清理普通会话
        sessions_to_cleanup = []
        for session_id, session in self.sessions.items():
            if session.end_time and (current_time - session.end_time).total_seconds() > settings.SESSION_EXPIRE_TIME:
                sessions_to_cleanup.append(session_id)
        
        for session_id in sessions_to_cleanup:
            self.cleanup_session(session_id)
        
        # 清理流式会话
        streams_to_cleanup = []
        for session_id, session in self.stream_sessions.items():
            if session.end_time and (current_time - session.end_time).total_seconds() > settings.SESSION_EXPIRE_TIME:
                streams_to_cleanup.append(session_id)
        
        for session_id in streams_to_cleanup:
            self.cleanup_stream_session(session_id)
        
        if sessions_to_cleanup or streams_to_cleanup:
            logger.info(f"Cleaned up {len(sessions_to_cleanup)} sessions and {len(streams_to_cleanup)} streams")

# 全局音频管理器实例
audio_manager = AudioManager()