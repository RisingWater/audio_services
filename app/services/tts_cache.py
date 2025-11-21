import hashlib
from pathlib import Path
from typing import Optional
import shutil

class TTSCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_hash(self, text: str) -> str:
        """生成文本的MD5作为文件名"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_cache_file(self, text: str) -> Optional[Path]:
        """获取缓存的音频文件"""
        file_hash = self._get_file_hash(text)
        cache_file = self.cache_dir / f"{file_hash}.mp3"
        
        if cache_file.exists():
            return cache_file
        return None
    
    def save_cache(self, text: str, source_file: Path) -> Path:
        """保存音频到缓存"""
        file_hash = self._get_file_hash(text)
        cache_file = self.cache_dir / f"{file_hash}.mp3"
        
        # 复制文件到缓存
        shutil.copy2(source_file, cache_file)
        return cache_file