import redis
import os
import json
from typing import Optional, Any

class Cache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            cls._instance.client = cls._instance._get_redis_client()
        return cls._instance

    def _get_redis_client(self):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        try:
            client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
            client.ping()
            print(f"Connected to Redis at {redis_host}:{redis_port}")
            return client
        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis: {e}")
            return None

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        if not self.client:
            return
        self.client.set(key, json.dumps(value), ex=ex)

    def delete(self, key: str):
        if not self.client:
            return
        self.client.delete(key)

    def clear(self):
        if not self.client:
            return
        self.client.flushdb()

cache = Cache()
