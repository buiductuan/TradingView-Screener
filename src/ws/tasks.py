from celery import shared_task
from tradingview import Query

@shared_task
def realtime_data():
    print("------ Get realtime data --------")
    return "Task completed"
