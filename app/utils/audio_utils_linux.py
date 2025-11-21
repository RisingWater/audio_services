import os
import logging
import subprocess
import threading
import queue
from typing import Optional
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

def play_audio_file(session_id: str, file_path: str, audio_manager):
    """使用 PulseAudio 播放音频文件"""
    session = audio_manager.get_session(session_id)
    if not session:
        return
    
    try:
        session.status = "playing"
        session.start_time = datetime.now()
        
        # 使用 mplayer 通过 PulseAudio 播放
        process = subprocess.Popen([
            'mplayer', 
            '-ao', 'pulse',  # 使用 PulseAudio 输出
            '-novideo',
            '-volume', str(int(session.volume * 100)),
            file_path
        ], env={
            **os.environ,
            'PULSE_RUNTIME_PATH': '/var/run/pulse'
        })
        
        session.process = process
        return_code = process.wait()
        
        session.end_time = datetime.now()
        session.status = "completed" if return_code == 0 else "error"
        
    except Exception as e:
        logger.error(f"Playback error for session {session_id}: {e}")
        session.status = "error"
        session.end_time = datetime.now()
    finally:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Could not delete temp file {file_path}: {e}")

def start_stream_player(session_id: str, audio_manager):
    """使用 PulseAudio 启动流式音频播放器"""
    session = audio_manager.get_stream_session(session_id)
    if not session:
        return
    
    try:
        session.status = "playing"
        session.start_time = datetime.now()
        
        # 使用 ffmpeg 进行流式解码，输出到 PulseAudio
        ffmpeg_process = subprocess.Popen([
            'ffmpeg',
            '-i', 'pipe:0',           # 从标准输入读取
            '-f', 'wav',              # 输出 WAV 格式
            '-ac', str(settings.CHANNELS),
            '-ar', str(settings.SAMPLE_RATE),
            '-',                      # 输出到标准输出
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        # 使用 mplayer 通过 PulseAudio 播放
        mplayer_process = subprocess.Popen([
            'mplayer',
            '-ao', 'pulse',           # 使用 PulseAudio 输出
            '-novideo',
            '-volume', str(int(session.volume * 100)),
            '-cache', '1024',
            '-'                       # 从标准输入读取
        ], stdin=ffmpeg_process.stdout, env={
            **os.environ,
            'PULSE_RUNTIME_PATH': '/var/run/pulse'
        })
        
        session.process = mplayer_process
        
        # 在后台线程中处理数据输入
        def feed_data():
            try:
                while (session.status == "playing" and 
                       ffmpeg_process.poll() is None and 
                       mplayer_process.poll() is None):
                    try:
                        # 从队列获取数据（非阻塞）
                        data = session.input_queue.get(timeout=1.0)
                        if data:
                            ffmpeg_process.stdin.write(data)
                            ffmpeg_process.stdin.flush()
                    except queue.Empty:
                        continue
                    except BrokenPipeError:
                        break
            except Exception as e:
                logger.error(f"Stream data feeding error: {e}")
            finally:
                try:
                    ffmpeg_process.stdin.close()
                except:
                    pass
        
        # 启动数据输入线程
        feed_thread = threading.Thread(target=feed_data, daemon=True)
        feed_thread.start()
        
        # 等待播放结束
        mplayer_process.wait()
        ffmpeg_process.wait()
        
        session.status = "completed"
        
    except Exception as e:
        logger.error(f"Stream playback error for session {session_id}: {e}")
        session.status = "error"
    finally:
        session.end_time = datetime.now()
