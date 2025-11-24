from fastapi import APIRouter, HTTPException
from typing import List

from models import TTSSessionStatus, PlayListSessionStatus, PlaylistElement, SetPlaylistRequest
from managers import audio_manager
from utils import get_song_name_by_id, get_song_url_by_id

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("/tts_session", response_model=List[TTSSessionStatus])
async def list_tts_sessions():
    """获取所有会话状态"""
    sessions = []
    
    # 普通播放会话
    for session in audio_manager.get_all_tts_sessions():
        sessions.append(session.get_status())
    return sessions

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

@router.get("/music_session", response_model=PlayListSessionStatus)
async def get_music_sessions():
    """获取音乐播放会话状态"""
    session = audio_manager.get_playlist_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.get_status()

@router.post("/music_session/stop")
async def stop_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_playlist_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.stop()
    return {"status": "stopped", "session_id": session.session_id}

@router.post("/music_session/pause")
async def stop_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_playlist_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.pause()
    return {"status": "paused", "session_id": session.session_id}

@router.post("/music_session/resume")
async def stop_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_playlist_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.resume()
    return {"status": "playing", "session_id": session.session_id}

@router.post("/music_session/next")
async def next_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_playlist_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.next()
    return {"status": "playing", "session_id": session.session_id}

@router.post("/music_session/prev")
async def prev_music_sessions():
    """停止特定会话的播放"""
    session = audio_manager.get_playlist_session()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.prev()
    return {"status": "playing", "session_id": session.session_id}

@router.post("/music_session/playlist")
async def set_playlist(request: SetPlaylistRequest):
    """
    设置播放队列
    - 只存储歌曲ID和名称，播放时再获取实时URL
    """
    try:
        if not request.song_ids:
            raise HTTPException(status_code=400, detail="歌曲ID列表不能为空")

        # 构建播放列表元素（只有ID和名称，没有URL）
        playlist = []
        for song_id in request.song_ids:
            # 只获取歌曲名称
            song_id_str = str(song_id)
            song_name = get_song_name_by_id(song_id_str)
            
            # 创建播放列表元素（URL为空）
            playlist_element = PlaylistElement(
                url="",  # 播放时再获取
                name=song_name,
                id=song_id_str
            )
            playlist.append(playlist_element)

        # 设置播放队列
        session = audio_manager.create_playlist_session(str(request.id), request.volume)
        session.add_songs(playlist)
        
        return {
            "status": "success",
            "session_id": session.session_id,
            "id": str(request.id),
            "message": f"播放队列已设置，共{len(playlist)}首歌曲",
            "playlist_length": len(playlist)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置播放队列失败: {e}")
        
@router.post("/music_session/playlist/play/{song_id}")
async def play_songid(song_id: str):
    """
    设置播放歌曲
    """
    try:
        sessions = audio_manager.get_playlist_session()

        index = -1
        # 检查每个歌曲元素的有效性
        for song in sessions.playlist:
            if song.id == song_id:
                index = sessions.playlist.index(song)

        if index < 0:
            raise HTTPException(status_code=400, detail=f"歌曲不存在")

        sessions.play_index(index)

        return {
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置播放失败: {e}")