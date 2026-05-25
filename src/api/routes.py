import asyncio, psutil
from fastapi import APIRouter, WebSocket
from src.core.config import redis_client

router = APIRouter()
connected_clients = []

# Global function to push logs to the UI
async def notify_audit_trail(message: str):
    for client in connected_clients:
        await client.send_json({"type": "log", "data": message})

@router.post("/config/limit")
async def update_limit(limit: int):
    redis_client.set("global_limit", limit)
    return {"status": "success"}

@router.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Stream system telemetry to the chart
            stats = {"type": "stats", "data": {"cpu": psutil.cpu_percent()}}
            await websocket.send_json(stats)
            await asyncio.sleep(1)
    except:
        connected_clients.remove(websocket)