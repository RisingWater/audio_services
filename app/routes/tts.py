from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import logging

from models.tts import TTSRequest, TTSResponse, VoiceInfo
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
        background_tasks.add_task(play_audio_file, session.session_id, audio_file, audio_manager, False)
        
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
