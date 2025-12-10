import os
import logging
import requests
import json
from typing import Optional
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
    
    def text_to_speech(self, text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> Optional[str]:
        return self.text_to_speech_easyvoice(text, voice)

    def text_to_speech_easyvoice(
        self, 
        text: str, 
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "0%",
        pitch: str = "0Hz",
        volume: str = "0%"
    ) -> Optional[str]:
        """使用 EasyVoice 将文字转换为语音文件（带缓存）"""
        try:
            # 创建临时文件
            temp_file = self.audio_dir / f"tts_{os.urandom(4).hex()}.mp3"
            
            # 先检查缓存
            cached_file = self.tts_cache.get_cache_file(text)
            if cached_file:
                logger.info(f"使用缓存语音: {cached_file}")
                return str(cached_file)
            
            # 构建请求数据
            payload = {
                "data": [
                    {
                        "text": text,
                        "voice": voice,
                        "rate": rate,
                        "pitch": pitch,
                        "volume": volume
                    }
                ]
            }
            
            # EasyVoice API 地址（根据你的实际配置修改）
            easyvoice_url = "http://192.168.1.180:6019/api/v1/tts/generateJson"
            
            logger.info(f"请求 EasyVoice: {text[:50]}... (voice: {voice})")
            
            # 发送请求
            response = requests.post(
                easyvoice_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30  # 30秒超时
            )
            
            if response.status_code != 200:
                logger.error(f"EasyVoice API 错误: {response.status_code}, {response.text}")
                return None
            
            # 保存文件
            with open(temp_file, 'wb') as f:
                f.write(response.content)
                
            # 保存到缓存
            cached_file = self.tts_cache.save_cache(text, temp_file)
            logger.info(f"EasyVoice 生成成功: {cached_file}, 大小: {cached_file.stat().st_size} 字节")
            
            return str(cached_file)
            
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到 EasyVoice 服务，请确保服务已启动")
            return None
        except requests.exceptions.Timeout:
            logger.error("EasyVoice 请求超时")
            return None
        except Exception as e:
            logger.error(f"EasyVoice TTS 错误: {e}")
            return None      


# 全局 TTS 服务实例
tts_service = TTSService()