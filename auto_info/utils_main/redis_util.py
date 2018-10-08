import redis
from django.conf import settings


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class RedisUtil(Singleton):
    def __init__(self):
        self.redis_ip = settings.REDIS_IP
        self.redis_port = settings.REDIS_PORT
        self.redis_password = settings.REDIS_PASSWORD

    def get_connection(self):
        sr = redis.StrictRedis(host=self.redis_ip, port=int(self.redis_port), password=self.redis_password)
        return sr

