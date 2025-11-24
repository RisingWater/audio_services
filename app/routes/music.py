from fastapi import APIRouter, HTTPException, UploadFile, File
import logging
import uuid
from models import MusicRequest, MusicResponse
from managers import audio_manager
from models import PlaylistElement

router = APIRouter(prefix="/api/music", tags=["play-music"])
logger = logging.getLogger(__name__)

@router.post("/play_url", response_model=MusicResponse)
async def play_url(request: MusicRequest):
    """播放url"""
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="url不能为空")
        
    try:
        # 创建播放会话
        session = audio_manager.create_playlist_session()
        session.add_songs([PlaylistElement(id="manual_url", name="", url=request.url)])

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
