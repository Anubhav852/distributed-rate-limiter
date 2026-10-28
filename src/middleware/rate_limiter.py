import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import redis_client, rate_limit_script
from src.api.routes import record_event


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only apply rate limiting to the actual API resources
        if not request.url.path.startswith("/api/resource"):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        start = time.perf_counter()

        # Current dynamic limit from Redis
        limit = int(redis_client.get("global_limit") or 10)

        # Atomic check-and-decrement in Lua
        allowed = rate_limit_script(keys=[ip], args=[limit, 60])

        remaining = int(redis_client.get(ip) or 0)
        ttl = max(redis_client.ttl(ip), 1)
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
        }

        if not allowed:
            latency = (time.perf_counter() - start) * 1000
            record_event(ip, request.url.path, 429, True, latency, 0, limit)
            return Response(
                status_code=429,
                content="Rate Limit Exceeded",
                headers={**headers, "Retry-After": str(ttl)},
            )

        response = await call_next(request)
        for k, v in headers.items():
            response.headers[k] = v
        latency = (time.perf_counter() - start) * 1000
        record_event(ip, request.url.path, response.status_code, False, latency, remaining, limit)
        return response