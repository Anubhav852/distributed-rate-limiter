import asyncio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import redis_client, rate_limit_script
from src.api.routes import notify_audit_trail

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only apply rate limiting to the actual API resources
        if not request.url.path.startswith("/api/resource"):
            return await call_next(request)

        user_id = request.client.host
        # Fetch current dynamic limit from Redis
        limit = int(redis_client.get("global_limit") or 10)
        
        # Lua Script execution (Atomic check-and-decrement)
        allowed = rate_limit_script(keys=[user_id], args=[limit, 60])
        
        if not allowed:
            # Trigger the Audit Trail UI log
            await notify_audit_trail(f"429: Rate Limit Hit by {user_id} at {request.url.path}")
            return Response(status_code=429, content="Rate Limit Exceeded")
            
        return await call_next(request)