from fastapi import FastAPI
import asyncio
import logging

from config import settings
from managers import audio_manager
from routes import tts
from routes import sessions
from routes import music

from fastapi.middleware.cors import CORSMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# 包含路由
app.include_router(sessions.router)
app.include_router(tts.router)
app.include_router(music.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:20201"],  # 你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Audio Web Player API", 
        "version": settings.VERSION
    }

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