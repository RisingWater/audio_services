import aiofiles
import os
from pathlib import Path
from config import settings

async def save_upload_file(file_content: bytes, filename: str) -> str:
    """保存上传的文件"""
    settings.AUDIO_DIR.mkdir(exist_ok=True)
    file_path = settings.AUDIO_DIR / filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return str(file_path)

async def delete_file(file_path: str):
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass