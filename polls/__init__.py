from rq import Queue
from worker import conn

q = Queue('default', connection=conn)