from fastapi import APIRouter, HTTPException
from typing import List

from models import TTSSessionStatus, MusicSessionStatus
from managers import audio_manager

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("/tts_session", response_model=List[TTSSessionStatus])
async def list_tts_sessions():
    """获取所有会话状态"""
    sessions = []
    
    # 普通播放会话
    for session in audio_manager.get_all_tts_sessions():
        sessions.append(session.get_status())
    return sessions

@router.get("/music_session", response_model=MusicSessionStatus)
async def get_music_sessions():
    """获取音乐播放会话状态"""
    session = audio_manager.get_muisc_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.get_status()

@router.get("/tts_session/{session_id}", response_model=TTSSessionStatus)
async def get_tts_session_status(session_id: str):
    # 先检查普通会话
    session = audio_manager.get_tts_session(session_id)
    if session:
        return session.get_status()
        
    raise HTTPException(status_code=404, detail="Session not found")

@router.post("/tts_session/{session_id}/stop")
async def stop_tts_session(session_id: str):
    """停止特定会话的播放"""
    session = audio_manager.get_tts_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.stop(session_id)
    return {"status": "stopped", "session_id": session_id}

@router.delete("/tts_session/{session_id}")
async def delete_tts_session(session_id: str):
    """删除会话并清理资源"""
    audio_manager.clean_up_tts_session(session_id)
    return {"status": "deleted", "session_id": session_id}

@router.post("/music_session/stop")
async def stop_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_muisc_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.stop()
    return {"status": "stopped", "session_id": session.session_id}

@router.post("/music_session/pause")
async def stop_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_muisc_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.pause()
    return {"status": "paused", "session_id": session.session_id}

@router.post("/music_session/resume")
async def stop_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_muisc_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.resume()
    return {"status": "playing", "session_id": session.session_id}