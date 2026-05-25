import redis
import os

# Connection pool for thread-safety
pool = redis.ConnectionPool(
    host='127.0.0.1', 
    port=6379, 
    db=0, 
    decode_responses=True,
    max_connections=20
)
redis_client = redis.Redis(connection_pool=pool)

# Load Lua script safely
script_path = os.path.join("src", "scripts", "rate_limit.lua")
try:
    with open(script_path, "r") as f:
        lua_script = f.read()
    rate_limit_script = redis_client.register_script(lua_script)
except Exception as e:
    print(f"CRITICAL: Could not load Lua script: {e}")
    rate_limit_script = None