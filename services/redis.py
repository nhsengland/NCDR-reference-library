import environ
from redis import StrictRedis

env = environ.Env()

conn = StrictRedis.from_url(env("REDIS_URL", default="redis://localhost/"))
