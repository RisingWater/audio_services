from fastapi import APIRouter, HTTPException
import logging

from models import TTSRequest, TTSResponse, VoiceInfo
from services import tts_service
from managers import audio_manager

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
async def text_to_speech(request: TTSRequest):
    """文字转语音并播放"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="文本内容不能为空")
    
    # 限制文本长度
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="文本过长，请限制在5000字符以内")
    
    try:
        # 创建播放会话
        session = audio_manager.create_tts_session(request.text, request.voice, request.volume)

        if not session.play():
            raise HTTPException(status_code=500, detail="语音生成失败")
        
        return TTSResponse(
            session_id=session.session_id,
            status="playing",
            message="语音即将播放"
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"语音转换失败: {e}")
