import redis

class RealTimeMemory:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def store_context(self, key, value):
        self.redis_client.set(key, value)

    def get_context(self, key):
        return self.redis_client.get(key)

    def clear_context(self):
        self.redis_client.flushdb()  # Clears Redis memory
