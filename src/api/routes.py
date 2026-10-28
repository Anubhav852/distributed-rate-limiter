import asyncio
import json
import logging
import time

import psutil
import redis.asyncio as aioredis
from fastapi import APIRouter, Query, Request, WebSocket

from src.core.config import redis_client, REDIS_URL

router = APIRouter()
log = logging.getLogger("enterprise_logger")

CHANNEL = "rl:events"


def record_event(ip, path, status, blocked, latency_ms, remaining, limit):
    """Store counters + recent events in Redis and publish to all dashboards."""
    evt = {
        "ts": round(time.time(), 3),
        "ip": ip,
        "path": path[:80],
        "status": status,
        "blocked": blocked,
        "latency_ms": round(latency_ms, 2),
        "remaining": remaining,
        "limit": limit,
    }
    try:
        pipe = redis_client.pipeline(transaction=False)
        pipe.incr("rl_stats:total")
        pipe.incr("rl_stats:blocked" if blocked else "rl_stats:allowed")
        pipe.lpush("rl_stats:recent", json.dumps(evt))
        pipe.ltrim("rl_stats:recent", 0, 49)
        if blocked:
            pipe.zincrby("rl_stats:offenders", 1, ip)
        pipe.publish(CHANNEL, json.dumps({"type": "request", "data": evt}))
        pipe.execute()
    except Exception as exc:
        log.warning(f"record_event failed: {exc}")


@router.get("/resource")
async def resource(request: Request):
    """The protected endpoint. Rate limiting happens in the middleware."""
    return {
        "message": "Resource served",
        "client_ip": request.client.host if request.client else "unknown",
        "server_time": time.time(),
    }


@router.post("/config/limit")
def update_limit(limit: int = Query(..., ge=1, le=1000)):
    redis_client.set("global_limit", limit)
    return {"status": "success", "limit": limit}


@router.post("/demo/reset")
def reset_my_quota(request: Request):
    """Clears only the caller's own counter so the demo can be repeated."""
    ip = request.client.host if request.client else "unknown"
    redis_client.delete(ip)
    return {"status": "reset", "ip": ip}


@router.get("/stats")
def get_stats():
    """Initial dashboard state (totals + recent events survive page reloads)."""
    total = int(redis_client.get("rl_stats:total") or 0)
    allowed = int(redis_client.get("rl_stats:allowed") or 0)
    blocked = int(redis_client.get("rl_stats:blocked") or 0)
    recent = [json.loads(x) for x in redis_client.lrange("rl_stats:recent", 0, 49)]
    offenders = [
        {"ip": ip, "count": int(score)}
        for ip, score in redis_client.zrevrange("rl_stats:offenders", 0, 4, withscores=True)
    ]
    return {
        "total": total,
        "allowed": allowed,
        "blocked": blocked,
        "limit": int(redis_client.get("global_limit") or 10),
        "recent": recent,  # newest first
        "offenders": offenders,
    }


@router.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL)
    last_stats = 0.0
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.25)
            if msg and msg.get("data"):
                await websocket.send_text(msg["data"])
            now = time.time()
            if now - last_stats >= 1:
                await websocket.send_json({
                    "type": "stats",
                    "data": {
                        "cpu": psutil.cpu_percent(),
                        "mem": psutil.virtual_memory().percent,
                    },
                })
                last_stats = now
    except Exception:
        pass
    finally:
        try:
            await pubsub.unsubscribe(CHANNEL)
            await pubsub.aclose()
            await r.aclose()
        except Exception:
            pass