import os
import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, AsyncGenerator
import edge_tts

from config import settings

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.audio_dir = settings.AUDIO_DIR
        self.audio_dir.mkdir(exist_ok=True)
    
    async def get_available_voices(self):
        """获取可用的语音列表"""
        try:
            voices = await edge_tts.list_voices()
            return voices
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    async def text_to_speech(self, text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> Optional[str]:
        """将文字转换为语音文件"""
        try:
            # 创建临时文件
            temp_file = self.audio_dir / f"tts_{os.urandom(4).hex()}.mp3"

            communicate = edge_tts.Communicate(text, voice)
            communicate.save_sync(str(temp_file))
            
            # 检查文件是否生成成功
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                logger.error("TTS generated empty file")
                return None
                
            logger.info(f"TTS generated: {temp_file}, size: {os.path.getsize(temp_file)} bytes, text length: {len(text)}")
            return str(temp_file)
            
        except Exception as e:
            logger.error(f"TTS conversion error: {e}")
            return None

    async def cleanup_file(self, file_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up TTS file: {file_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up file {file_path}: {e}")

# 全局 TTS 服务实例
tts_service = TTSService()