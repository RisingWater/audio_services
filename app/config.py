import os
from pathlib import Path
import platform
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    # 基础配置
    APP_NAME = os.getenv("APP_NAME", "Audio Web Player")
    VERSION = os.getenv("VERSION", "0.0.1")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "6018"))
    
    # 音频配置
    if platform.system() == "Windows":
        AUDIO_DIR = Path(os.getenv("AUDIO_DIR", "D:\\"))
        CACHE_DIR = Path(os.getenv("CACHE_DIR", "D:\\"))
    else:
        AUDIO_DIR = Path(os.getenv("AUDIO_DIR", "/tmp/audio"))
        CACHE_DIR = Path(os.getenv("CACHE_DIR", "tmp"))
    
    # 支持的音频格式
    SUPPORTED_FORMATS = set(os.getenv("SUPPORTED_FORMATS", "wav,mp3,ogg,flac").split(','))
    
    # 音频参数
    DEFAULT_VOLUME = float(os.getenv("DEFAULT_VOLUME", "1.0"))
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "44100"))
    CHANNELS = int(os.getenv("CHANNELS", "2"))
    
    # 会话配置
    SESSION_CLEANUP_INTERVAL = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))
    SESSION_EXPIRE_TIME = int(os.getenv("SESSION_EXPIRE_TIME", "600"))
    
    def __str__(self):
        """返回配置信息（隐藏敏感信息）"""
        return f"""
{self.APP_NAME} v{self.VERSION}
监听地址: {self.HOST}:{self.PORT}
音频目录: {self.AUDIO_DIR}
支持格式: {', '.join(self.SUPPORTED_FORMATS)}
默认音量: {self.DEFAULT_VOLUME}
采样率: {self.SAMPLE_RATE}
声道数: {self.CHANNELS}
        """.strip()

settings = Settings()