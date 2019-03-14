import os  # isort:skip

os.environ["DJANGO_SETTINGS_MODULE"] = "ncdr.settings"  # isort:skip  # noqa: E402

from rq import Connection, Queue, Worker

from services.redis import conn as redis_conn

DEFAULT_QUEUES = ["default"]


def main():
    # Initialise Django before booting the worker
    import django

    django.setup()

    with Connection(redis_conn):
        worker = Worker(Queue("default"))
        worker.work()


if __name__ == "__main__":
    main()
