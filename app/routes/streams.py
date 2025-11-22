from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import aiofiles
import os

from models import StreamResponse, VolumeControl
from managers import audio_manager
from utils import start_stream_player
from utils import save_upload_file
from config import settings

router = APIRouter(prefix="/api/stream", tags=["streams"])

@router.post("/start", response_model=StreamResponse)
async def start_stream_session(volume: float = settings.DEFAULT_VOLUME):
    """创建新的流式播放会话"""
    session = audio_manager.create_stream_session()
    session.volume = max(0.0, min(1.0, volume))
    
    # 在后台启动流式播放器
    background_tasks = BackgroundTasks()
    background_tasks.add_task(start_stream_player, session.session_id, audio_manager)
    
    return StreamResponse(
        session_id=session.session_id,
        status="created",
        message="Stream session created, use /api/stream/{session_id}/feed to send audio data"
    )

@router.post("/{session_id}/feed")
async def feed_stream_data(session_id: str, file: UploadFile = File(...)):
    """向流式会话发送音频数据"""
    session = audio_manager.get_stream_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Stream session not found")
    
    if session.status != "playing":
        raise HTTPException(status_code=400, detail="Stream session is not active")
    
    content = await file.read()
    if content:
        session.input_queue.put(content)
        logger.info(f"Fed {len(content)} bytes to stream session {session_id}")
    
    return {"status": "data_accepted", "bytes_received": len(content)}

@router.post("/{session_id}/stop")
async def stop_stream_session(session_id: str):
    """停止流式播放会话"""
    session = audio_manager.get_stream_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Stream session not found")
    
    audio_manager.stop_stream_session(session_id)
    return {"status": "stopped", "session_id": session_id}

@router.post("/direct")
async def stream_audio_direct(file: UploadFile = File(...), volume: float = settings.DEFAULT_VOLUME):
    """直接流式播放音频数据（一次性接口）"""
    from utils import play_audio_file
    
    # 创建临时会话
    session = audio_manager.create_session()
    session.volume = max(0.0, min(1.0, volume))
    session.is_stream = True
    
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="No audio data received")
    
    # 创建临时文件并播放
    import uuid
    temp_file = settings.AUDIO_DIR / f"stream_direct_{session.session_id}.wav"
    
    async with aiofiles.open(temp_file, 'wb') as f:
        await f.write(content)
    
    # 播放临时文件
    background_tasks = BackgroundTasks()
    background_tasks.add_task(play_audio_file, session.session_id, str(temp_file), audio_manager, True)
    
    return StreamResponse(
        session_id=session.session_id,
        status="playing",
        message="Direct stream playback started"
    )