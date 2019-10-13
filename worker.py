import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://h:p7cccf3c208d2383a7edaec3139ea735f184c6ba778de1b66a1e71c130692e6c4'
                                       '@ec2-34-241-111-4.eu-west-1.compute.amazonaws.com:10349')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()