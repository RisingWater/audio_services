import os
import logging
import threading
import queue
from typing import Optional
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

def play_audio_file(session_id: str, file_path: str, audio_manager, delete_file=True):
    """使用 playsound 播放音频文件（支持 MP3、WAV）"""
    session = audio_manager.get_session(session_id)
    if not session:
        return
    
    try:
        session.status = "playing"
        session.start_time = datetime.now()
        
        from playsound import playsound
        
        # 播放音频（阻塞式）
        playsound(file_path)
        
        session.end_time = datetime.now()
        session.status = "completed"
        logger.info(f"Playback completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Playback error for session {session_id}: {e}")
        session.status = "error"
        session.end_time = datetime.now()
    finally:
        # 清理文件
        try:
            if delete_file and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Could not delete temp file {file_path}: {e}")

def start_stream_player(session_id: str, audio_manager):
    """使用 pyaudio 启动流式音频播放器"""
    session = audio_manager.get_stream_session(session_id)
    if not session:
        return
    
    try:
        session.status = "playing"
        session.start_time = datetime.now()
        
        import pyaudio
        
        # 初始化 pyaudio
        p = pyaudio.PyAudio()
        
        # 打开音频流
        stream = p.open(format=pyaudio.paInt16,
                       channels=settings.CHANNELS,
                       rate=settings.SAMPLE_RATE,
                       output=True)
        
        def stream_processor():
            try:
                while session.status == "playing":
                    try:
                        data = session.input_queue.get(timeout=1.0)
                        if not data:
                            break
                        stream.write(data)
                    except queue.Empty:
                        continue
                
                # 清理资源
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                session.end_time = datetime.now()
                session.status = "completed"
                
            except Exception as e:
                logger.error(f"Stream playback error: {e}")
                session.status = "error"
                session.end_time = datetime.now()
        
        # 在后台线程中处理流式播放
        thread = threading.Thread(target=stream_processor, daemon=True)
        thread.start()
        
    except Exception as e:
        logger.error(f"Stream setup error for session {session_id}: {e}")
        session.status = "error"
        session.end_time = datetime.now()