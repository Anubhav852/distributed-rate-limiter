# src/dependencies.py
import redis
import os

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

script_path = os.path.join("src", "scripts", "rate_limit.lua")
with open(script_path, "r") as f:
    lua_script = f.read()

rate_limit_script = redis_client.register_script(lua_script)