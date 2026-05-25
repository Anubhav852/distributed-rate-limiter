local key = KEYS[1]
local limit = tonumber(ARGV[1])

local current = redis.call("GET", key)

if not current then
    redis.call("SET", key, limit - 1, "EX", 60)
    return 1
else
    local val = tonumber(current)
    if val <= 0 then
        return 0
    else
        redis.call("DECR", key)
        return 1
    end
end