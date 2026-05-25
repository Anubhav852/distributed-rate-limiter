from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
import asyncio
from src.core.config import redis_client

router = APIRouter()

@router.get("/resource")
async def get_resource():
    return {"status": "success", "data": "Protected Resource Accessed"}

@router.get("/status")
async def get_status(request: Request):
    user_id = request.client.host if request.client else "127.0.0.1"
    count = redis_client.get(user_id)
    return {"user_id": user_id, "remaining": int(count) if count is not None else 10}

@router.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send current status every 0.5 seconds
            user_id = "127.0.0.1" 
            count = redis_client.get(user_id)
            remaining = int(count) if count is not None else 10
            await websocket.send_json({"remaining": remaining})
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass