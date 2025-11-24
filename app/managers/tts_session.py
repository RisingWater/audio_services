import os
import logging
import subprocess
import threading
import uuid

from models import TTSSessionStatus
from services import tts_service
logger = logging.getLogger(__name__)

class TTSSession:
    def __init__(self, text: str, voice: str = "zh-CN-XiaoxiaoNeural", volume: float = 1.0):
        session_id = str(uuid.uuid4())
        self.session_id = session_id
        self.volume: float = volume
        self.status: str = "created"
        self.type: str = "tts"
        self.text = text
        self.voice = voice

        self._process = None
        self._file_path = None
        self._play_thread = None

    def play(self) -> bool:
        # 检查是否正在播放
        if self._play_thread and self._play_thread.is_alive():
            logger.warning(f"Session {self.session_id} is already playing.")
            return False

        self.status = "playing"

        self._file_path = tts_service.text_to_speech(self.text, self.voice)

        if not self._file_path or not os.path.exists(self._file_path):
            self.status = "error"
            return False
        
        def _play_in_thread():
            try:
                # 使用 mplayer 通过 PulseAudio 播放
                process = subprocess.Popen([
                    'mplayer', 
                    '-ao', 'pulse',  # 使用 PulseAudio 输出
                    '-novideo',
                    '-volume', str(int(self.volume * 100)),
                    self._file_path
                ], env={
                    **os.environ,
                    'PULSE_RUNTIME_PATH': '/var/run/pulse'
                })
                
                self._process = process
                return_code = self._process.wait()
                
                self.status = "completed" if return_code == 0 else "error"
                self._play_thread = None
                
            except Exception as e:
                logger.error(f"Playback error for session {self.session_id}: {e}")
                self.status = "error"
        
        # 启动线程
        self._play_thread = threading.Thread(target=_play_in_thread)
        self._play_thread.daemon = True
        self._play_thread.start()
        
        return True

    def stop(self):
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
                self._process = None
                self.status = "stopped"
            except subprocess.TimeoutExpired:
                self._process.kill()
                self.status = "killed"
            finally:
                self._process = None
                self._play_thread = None  # 清理线程引用

    def is_finished(self):
        return self.status in ["completed", "stopped", "killed"]
    
    def get_status(self) -> TTSSessionStatus:
        return TTSSessionStatus(
            session_id=self.session_id,
            status=self.status, 
            text=self.text, 
            voice=self.voice, 
            volume=self.volume)
        
