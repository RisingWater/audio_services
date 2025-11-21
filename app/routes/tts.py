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

@router.post("/speak-stream", response_model=StreamResponse)
async def text_to_speech_stream(request: TTSRequest):
    """流式文字转语音（边转换边播放）"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="文本内容不能为空")
    
    # 对于流式播放，限制更长的文本
    if len(request.text) > 10000:
        raise HTTPException(status_code=400, detail="文本过长，请限制在10000字符以内")
    
    try:
        # 创建流式会话
        session = audio_manager.create_stream_session()
        session.volume = request.volume_level
        
        # 在后台启动流式 TTS
        background_tasks = BackgroundTasks()
        background_tasks.add_task(stream_tts_playback, session.session_id, request, audio_manager)
        
        return StreamResponse(
            session_id=session.session_id,
            status="streaming",
            message="流式语音生成中"
        )
        
    except Exception as e:
        logger.error(f"Stream TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"流式语音转换失败: {e}")

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

async def stream_tts_playback(session_id: str, request: TTSRequest, audio_manager):
    """流式 TTS 播放"""
    try:
        from utils import start_stream_player
        import queue
        
        session = audio_manager.get_stream_session(session_id)
        if not session:
            return
        
        # 启动流式播放器
        await start_stream_player(session_id, audio_manager)
        
        # 流式生成语音并发送到播放器
        async for audio_data in tts_service.text_to_speech_stream(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume
        ):
            if session.status != "playing":
                break
            session.input_queue.put(audio_data)
        
        # 标记流结束
        session.input_queue.put(b"")
        
    except Exception as e:
        logger.error(f"Stream TTS playback error: {e}")
        session.status = "error"