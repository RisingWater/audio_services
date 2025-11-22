import os
import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, AsyncGenerator
from services.tts_cache import TTSCache
import edge_tts

from config import settings

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.tts_cache = TTSCache(settings.CACHE_DIR)
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
        """将文字转换为语音文件（带缓存）"""
        try:
            # 创建临时文件
            temp_file = self.audio_dir / f"tts_{os.urandom(4).hex()}.mp3"
            
            # 先检查缓存
            cached_file = self.tts_cache.get_cache_file(text)
            if cached_file:
                logger.info(f"使用缓存语音: {cached_file}")
                return str(cached_file)
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(temp_file))
            
            # 检查文件是否生成成功
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                logger.error("TTS generated empty file")
                return None
                
            logger.info(f"TTS generated: {temp_file}, size: {os.path.getsize(temp_file)} bytes, text length: {len(text)}")
            
            # 保存到缓存
            cached_file = self.tts_cache.save_cache(text, temp_file)
            logger.info(f"语音已缓存: {cached_file}")
            
            return str(cached_file)
            
        except Exception as e:
            logger.error(f"TTS conversion error: {e}")
            return None
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.debug(f"已清理临时文件: {temp_file}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")


# 全局 TTS 服务实例
tts_service = TTSService()