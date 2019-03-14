import rq

from .redis import conn

FIVE_MINUTES = 5 * 60
queue = rq.Queue(connection=conn, default_timeout=FIVE_MINUTES)
