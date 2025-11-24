from fastapi import APIRouter, HTTPException, UploadFile, File
import logging
import uuid
from config import settings
from models import MusicRequest, MusicResponse
from managers import audio_manager

router = APIRouter(prefix="/api/music", tags=["play-music"])
logger = logging.getLogger(__name__)

@router.post("/play_url", response_model=MusicResponse)
async def play_url(request: MusicRequest):
    """播放url"""
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="url不能为空")
        
    try:
        # 创建播放会话
        session = audio_manager.create_music_session_by_url(request.url, request.volume)

        if not session.play():
            raise HTTPException(status_code=500, detail="播放失败")
        
        return MusicResponse(
            session_id=session.session_id,
            status="playing",
            message="语音即将播放"
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"语音转换失败: {e}")

@router.post("/play_file", response_model=MusicResponse)
async def play_audio(file: UploadFile = File(...), volume: float = 1.0):
    """播放文件"""
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {file_ext}")
    
    temp_file = settings.AUDIO_DIR / f"audio_{str(uuid.uuid4())}.{file_ext}"

    async with open(temp_file, 'wb') as f:
        content = await file.read()
        await f.write(content)

    session = audio_manager.create_music_session_by_filepath(temp_file, volume)

    if not session.play():
        raise HTTPException(status_code=500, detail="Failed to play audio")
    
    return MusicResponse(
        session_id=session.session_id,
        status="created",
        message="Audio playback scheduled"
    )