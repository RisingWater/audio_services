from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import logging

from models.tts import TTSRequest, TTSResponse, VoiceInfo
from models import StreamResponse
from services.tts_service import tts_service
from managers import audio_manager
from utils import play_audio_file

router = APIRouter(prefix="/api/tts", tags=["text-to-speech"])
logger = logging.getLogger(__name__)

@router.get("/voices", response_model=list[VoiceInfo])
async def get_available_voices():
    """获取可用的语音列表"""
    try:
        voices = await tts_service.get_available_voices()
        voice_list = []

        for voice in voices:
            if voice["Locale"] == "zh-CN":
                voice_list.append(VoiceInfo(
                    name=voice["Name"],
                    short_name=voice["ShortName"],
                    gender=voice["Gender"],
                    locale=voice["Locale"]
                ))
        
        return voice_list
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=f"获取语音列表失败: {e}")

@router.post("/speak", response_model=TTSResponse)
async def text_to_speech(background_tasks: BackgroundTasks, request: TTSRequest):
    """文字转语音并播放"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="文本内容不能为空")
    
    # 限制文本长度
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="文本过长，请限制在5000字符以内")
    
    try:
        # 创建播放会话
        session = audio_manager.create_session()
        session.filename = f"tts_{session.session_id}.mp3"
        session.format = "mp3"
        session.volume = request.volume_level
        
        # 生成语音文件
        audio_file = await tts_service.text_to_speech(
            text=request.text,
            voice=request.voice
        )
        
        if not audio_file:
            raise HTTPException(status_code=500, detail="语音生成失败")
        
        # 在后台播放并清理文件
        background_tasks.add_task(play_and_cleanup, session.session_id, audio_file, audio_manager)
        
        return TTSResponse(
            session_id=session.session_id,
            status="generating",
            text_length=len(request.text),
            voice=request.voice,
            message="语音生成中，即将播放"
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"语音转换失败: {e}")

@router.post("/speak-direct")
async def text_to_speech_direct(background_tasks: BackgroundTasks, request: TTSRequest):
    """直接播放文字转语音（不保存会话）"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="文本内容不能为空")
    
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="文本过长，请限制在5000字符以内")
    
    try:
        # 生成语音文件
        audio_file = await tts_service.text_to_speech(
            text=request.text,
            voice=request.voice
        )
        
        if not audio_file:
            raise HTTPException(status_code=500, detail="语音生成失败")
        
        # 创建临时会话用于播放
        session = audio_manager.create_session()
        session.filename = f"tts_direct_{session.session_id}.mp3"
        session.format = "mp3"
        session.volume = request.volume_level
        
        # 播放并清理
        background_tasks.add_task(play_and_cleanup, session.session_id, audio_file, audio_manager)
        
        return {
            "status": "playing",
            "text_length": len(request.text),
            "voice": request.voice,
            "message": "语音播放中"
        }
        
    except Exception as e:
        logger.error(f"Direct TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"语音播放失败: {e}")

async def play_and_cleanup(session_id: str, audio_file: str, audio_manager):
    """播放音频并清理文件"""
    try:
        # 播放音频
        from utils import play_audio_file
        await play_audio_file(session_id, audio_file, audio_manager)
        
        # 清理文件
        await tts_service.cleanup_file(audio_file)
        
    except Exception as e:
        logger.error(f"Play and cleanup error: {e}")
        # 确保文件被清理
        await tts_service.cleanup_file(audio_file)
