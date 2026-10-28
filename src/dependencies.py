import os
import redis

# Local default; on Render/Upstash set REDIS_URL (redis:// or rediss://)
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

# Connection pool for thread-safety
pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    decode_responses=True,
    max_connections=20,
)
redis_client = redis.Redis(connection_pool=pool)

# Load Lua script relative to this file (works from any working directory)
script_path = os.path.join(os.path.dirname(__file__), "scripts", "rate_limit.lua")
try:
    with open(script_path, "r") as f:
        lua_script = f.read()
    rate_limit_script = redis_client.register_script(lua_script)
except Exception as e:
    print(f"CRITICAL: Could not load Lua script: {e}")
    rate_limit_script = None