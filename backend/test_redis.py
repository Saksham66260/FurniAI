from app.cache.redis import redis_client

redis_client.set("python_test", "hello_from_python", ex=30)

print("GET:", redis_client.get("python_test"))
print("TTL:", redis_client.ttl("python_test"))