import os
from pathlib import Path

# 基础配置
class Settings:
    APP_NAME = "Audio Web Player"
    VERSION = "0.0.1"
    HOST = "0.0.0.0"
    PORT = 6018
    
    # 音频配置
    AUDIO_DIR = Path("/tmp/audio")
    SUPPORTED_FORMATS = {'wav', 'mp3', 'ogg', 'flac'}
    DEFAULT_VOLUME = 1.0
    SAMPLE_RATE = 44100
    CHANNELS = 2
    
    # 会话配置
    SESSION_CLEANUP_INTERVAL = 300  # 5分钟
    SESSION_EXPIRE_TIME = 600       # 10分钟

settings = Settings()