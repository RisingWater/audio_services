import platform

from .file_utils import save_upload_file, delete_file

# 根据系统导入不同的音频工具
if platform.system() == "Windows":
    from .audio_utils_windows import (
        play_audio_file, 
        start_stream_player, 
    )
else:
    from .audio_utils_linux import (
        play_audio_file, 
        start_stream_player, 
    )

__all__ = [
    "play_audio_file",
    "start_stream_player", 
    "save_upload_file",
    "delete_file"
]