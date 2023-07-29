from celery import Celery

app = Celery('my_project', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y
