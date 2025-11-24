import uuid
import logging
import subprocess
import os
import threading
from models import MusicSessionStatus

logger = logging.getLogger(__name__)

class MusicSession:
    def __init__(self, url: str, file_path: str = None, volume: float = 1.0):
        session_id = str(uuid.uuid4())
        self.session_id = session_id
        self.volume: float = volume
        self.status: str = "created"
        self.type: str = "music_url"
        
        self._url = url
        self._file_path = file_path
        self._process = None
        self._play_thread = None
        self._is_paused = False

    def _send_command(self, command: str) -> bool:
        """向 mplayer 发送命令"""
        if not self._process or self._process.poll() is not None:
            logger.warning(f"Session {self.session_id} is not playing")
            return False
        
        try:
            self._process.stdin.write(command + "\n")
            self._process.stdin.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to send command '{command}' to session {self.session_id}: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """设置音量 (0.0 - 1.0)"""
        if not 0.0 <= volume <= 1.0:
            logger.error(f"Volume {volume} is out of range (0.0-1.0)")
            return False
        
        self.volume = volume
        volume_percent = int(volume * 100)
        
        # 使用正确的音量命令格式
        return self._send_command(f"volume {volume_percent} 1")

    def pause(self) -> bool:
        """暂停播放"""
        if self._is_paused:
            logger.warning(f"Session {self.session_id} is already paused")
            return False
        
        if self._send_command("pause"):
            self._is_paused = True
            self.status = "paused"
            logger.info(f"Session {self.session_id} paused")
            return True
        return False

    def resume(self) -> bool:
        """恢复播放"""
        if not self._is_paused:
            logger.warning(f"Session {self.session_id} is not paused")
            return False
        
        if self._send_command("pause"):
            self._is_paused = False
            self.status = "playing"
            logger.info(f"Session {self.session_id} resumed")
            return True
        return False

    def seek(self, seconds: float, seek_type: int = 0) -> bool:
        """
        跳转到指定位置
        type 0: 相对跳转 +/- 秒
        type 1: 百分比跳转 (0-100)
        type 2: 绝对跳转 (秒)
        """
        if seek_type not in [0, 1, 2]:
            logger.error(f"Invalid seek type: {seek_type}")
            return False
        
        return self._send_command(f"seek {seconds} {seek_type}")

    def seek_absolute(self, seconds: float) -> bool:
        """绝对跳转到指定秒数"""
        return self.seek(seconds, seek_type=2)

    def seek_percentage(self, percentage: float) -> bool:
        """跳转到百分比位置"""
        return self.seek(percentage, seek_type=1)

    def play(self) -> bool:
        # 检查是否正在播放
        if self._play_thread and self._play_thread.is_alive():
            logger.warning(f"Session {self.session_id} is already playing.")
            return False

        self.status = "playing"
        self._is_paused = False

        # 检查播放源
        if self._url:
            url_play = True
        elif self._file_path and os.path.exists(self._file_path):
            url_play = False
        else:
            logger.error(f"Session {self.session_id} has no valid URL or file path.")
            self.status = "error"
            return False
        
        def _play_in_thread():
            try:
                play_source = self._url if url_play else self._file_path
                
                # 使用 slave 模式，启用 stdin/stdout 管道
                process = subprocess.Popen([
                    'mplayer', 
                    '-ao', 'pulse',
                    '-novideo',
                    '-volume', str(int(self.volume * 100)),
                    '-slave',           # 启用 slave 模式
                    '-quiet',           # 减少输出
                    play_source
                ], 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=1,
                universal_newlines=True,
                env={
                    **os.environ,
                    'PULSE_RUNTIME_PATH': '/var/run/pulse'
                })
                
                self._process = process
                
                # 读取输出的线程（用于获取播放状态）
                def read_output():
                    while process.poll() is None:
                        try:
                            line = process.stdout.readline()
                            if line:
                                # 可以在这里解析 mplayer 的输出
                                # 例如：ANS_TIME_POSITION=12.34
                                if 'ANS_' in line:
                                    logger.debug(f"mplayer status: {line.strip()}")
                        except Exception as e:
                            if process.poll() is None:  # 如果进程还在运行
                                logger.error(f"Error reading mplayer output: {e}")
                            break
                
                output_thread = threading.Thread(target=read_output)
                output_thread.daemon = True
                output_thread.start()
                
                return_code = process.wait()
                
                if return_code == 0:
                    self.status = "completed"
                else:
                    self.status = "error"
                    logger.error(f"Playback process exited with code {return_code}")
                
            except Exception as e:
                logger.error(f"Playback error for session {self.session_id}: {e}")
                self.status = "error"
            finally:
                self._process = None
                self._play_thread = None
                self._is_paused = False
        
        self._play_thread = threading.Thread(target=_play_in_thread)
        self._play_thread.daemon = True
        self._play_thread.start()
        
        return True

    def stop(self) -> bool:
        """停止播放"""
        if not self._process:
            logger.warning(f"Session {self.session_id} is not playing")
            return False
        
        try:
            # 使用 quit 命令正常退出
            if self._send_command("quit"):
                # 等待进程结束
                self._process.wait(timeout=5)
                self.status = "stopped"
                logger.info(f"Session {self.session_id} stopped normally")
                return True
            return False
            
        except subprocess.TimeoutExpired:
            # 如果正常退出超时，强制终止
            self._process.kill()
            self._process.wait()
            self.status = "killed"
            logger.warning(f"Session {self.session_id} was killed forcibly")
            return True
        except Exception as e:
            logger.error(f"Failed to stop session {self.session_id}: {e}")
            return False
        finally:
            self._process = None
            self._play_thread = None
            self._is_paused = False

    def get_status(self) -> MusicSessionStatus:
        """获取会话状态"""
        return MusicSessionStatus(
            session_id=self.session_id,
            status=self.status,
            url=self.url,
            file_path=self.file_path,
            volume=self.volume)
    