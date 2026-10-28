import os
import json
import logging
from datetime import datetime

import redis

# Setup JSON Logger
logging.basicConfig(level=logging.INFO)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("enterprise_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Redis config: local default, override with REDIS_URL on Render/Upstash
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True, max_connections=20)
redis_client = redis.Redis(connection_pool=pool)

# Lua script path relative to this file (works from any working directory)
script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "rate_limit.lua")
with open(script_path, "r") as f:
    lua_script = f.read()
rate_limit_script = redis_client.register_script(lua_script)