from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

from managers.audio_manager import audio_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

@router.websocket("/api/ws/stream/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str):
    """WebSocket 流式音频接口"""
    await websocket.accept()
    
    # 创建流式会话
    session = audio_manager.create_stream_session()
    
    try:
        # 启动播放器
        from utils.audio_utils import start_stream_player
        import asyncio
        await asyncio.get_event_loop().run_in_executor(
            None, start_stream_player, session.session_id, audio_manager
        )
        
        await websocket.send_text(json.dumps({
            "status": "connected",
            "session_id": session.session_id
        }))
        
        while True:
            data = await websocket.receive_bytes()
            if data:
                session.input_queue.put(data)
                await websocket.send_text(json.dumps({
                    "status": "data_received",
                    "bytes": len(data)
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session.session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        audio_manager.cleanup_stream_session(session.session_id)