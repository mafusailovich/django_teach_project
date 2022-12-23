from celery import shared_task
import time
from .func import user_notification



@shared_task
def hello():
    for i in range(10):
        time.sleep(10)
        print("Hello, world!")

@shared_task
def notification(post_id, post_head, post_text):
    user_notification(post_id, post_head, post_text)
