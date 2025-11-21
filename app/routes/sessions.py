from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List

from models import PlayResponse, SessionStatus, VolumeControl
from managers import audio_manager
from utils import play_audio_file
from utils import save_upload_file
from config import settings

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("/", response_model=List[SessionStatus])
async def list_sessions():
    """获取所有会话状态"""
    from datetime import datetime
    sessions = []
    
    # 普通播放会话
    for session in audio_manager.get_all_sessions():
        duration = None
        if session.start_time:
            if session.end_time:
                duration = (session.end_time - session.start_time).total_seconds()
            elif session.status == "playing":
                duration = (datetime.now() - session.start_time).total_seconds()
        
        sessions.append(SessionStatus(
            session_id=session.session_id,
            status=session.status,
            filename=session.filename,
            format=session.format,
            start_time=session.start_time.isoformat() if session.start_time else None,
            duration=duration,
            volume=session.volume,
            is_stream=session.is_stream
        ))
    
    # 流式播放会话
    for session in audio_manager.get_all_stream_sessions():
        duration = None
        if session.start_time:
            duration = (datetime.now() - session.start_time).total_seconds()
        
        sessions.append(SessionStatus(
            session_id=session.session_id,
            status=session.status,
            filename="stream",
            format="stream",
            start_time=session.start_time.isoformat() if session.start_time else None,
            duration=duration,
            volume=session.volume,
            is_stream=True
        ))
    
    return sessions

@router.get("/{session_id}", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """获取特定会话状态"""
    from datetime import datetime
    
    # 先检查普通会话
    session = audio_manager.get_session(session_id)
    if session:
        duration = None
        if session.start_time:
            if session.end_time:
                duration = (session.end_time - session.start_time).total_seconds()
            elif session.status == "playing":
                duration = (datetime.now() - session.start_time).total_seconds()
        
        return SessionStatus(
            session_id=session.session_id,
            status=session.status,
            filename=session.filename,
            format=session.format,
            start_time=session.start_time.isoformat() if session.start_time else None,
            duration=duration,
            volume=session.volume,
            is_stream=session.is_stream
        )
    
    # 检查流式会话
    stream_session = audio_manager.get_stream_session(session_id)
    if stream_session:
        duration = None
        if stream_session.start_time:
            duration = (datetime.now() - stream_session.start_time).total_seconds()
        
        return SessionStatus(
            session_id=stream_session.session_id,
            status=stream_session.status,
            filename="stream",
            format="stream",
            start_time=stream_session.start_time.isoformat() if stream_session.start_time else None,
            duration=duration,
            volume=stream_session.volume,
            is_stream=True
        )
    
    raise HTTPException(status_code=404, detail="Session not found")

@router.post("/{session_id}/stop")
async def stop_session(session_id: str):
    """停止特定会话的播放"""
    session = audio_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    audio_manager.stop_session(session_id)
    return {"status": "stopped", "session_id": session_id}

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话并清理资源"""
    audio_manager.cleanup_session(session_id)
    audio_manager.cleanup_stream_session(session_id)
    return {"status": "deleted", "session_id": session_id}