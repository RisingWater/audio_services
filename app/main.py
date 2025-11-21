from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
import asyncio
import logging
from datetime import datetime

from config import settings
from managers.audio_manager import AudioManager
from models.response import PlayResponse
from utils.audio_utils import play_audio_file
from utils.file_utils import save_upload_file

# 导入路由
from routes import sessions, streams, websocket

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# 包含路由
app.include_router(sessions.router)
app.include_router(streams.router)
app.include_router(websocket.router)

# 全局音频管理器
audio_manager = AudioManager()

@app.get("/")
async def root():
    """根路径"""
    active_sessions = len([s for s in audio_manager.get_all_sessions() if s.status == "playing"])
    active_streams = len([s for s in audio_manager.get_all_stream_sessions() if s.status == "playing"])
    return {
        "message": "Multi-track Audio Web Player API", 
        "version": settings.VERSION,
        "active_sessions": active_sessions,
        "active_streams": active_streams,
        "total_sessions": len(audio_manager.get_all_sessions()) + len(audio_manager.get_all_stream_sessions())
    }

@app.post("/api/play", response_model=PlayResponse)
async def play_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...), volume: float = settings.DEFAULT_VOLUME):
    """播放上传的音频文件"""
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {file_ext}")
    
    session = audio_manager.create_session()
    session.filename = file.filename
    session.format = file_ext
    session.volume = max(0.0, min(1.0, volume))
    
    temp_file = settings.AUDIO_DIR / f"audio_{session.session_id}.{file_ext}"
    
    async with open(temp_file, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    background_tasks.add_task(play_audio_file, session.session_id, str(temp_file), audio_manager)
    
    return PlayResponse(
        session_id=session.session_id,
        status="created",
        filename=file.filename,
        message="Audio playback scheduled"
    )

@app.post("/api/stop-all")
async def stop_all_sessions():
    """停止所有会话"""
    session_ids = [s.session_id for s in audio_manager.get_all_sessions()]
    stream_ids = [s.session_id for s in audio_manager.get_all_stream_sessions()]
    
    for session_id in session_ids:
        audio_manager.stop_session(session_id)
    for stream_id in stream_ids:
        audio_manager.stop_stream_session(stream_id)
    
    return {"status": "all_stopped", "stopped_sessions": len(session_ids) + len(stream_ids)}

# 清理任务
async def cleanup_task():
    """定期清理旧的会话"""
    while True:
        await asyncio.sleep(settings.SESSION_CLEANUP_INTERVAL)
        try:
            audio_manager.cleanup_old_sessions()
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")

@app.on_event("startup")
async def startup_event():
    """应用启动时启动清理任务"""
    asyncio.create_task(cleanup_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)