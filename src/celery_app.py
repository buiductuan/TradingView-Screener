from celery import Celery
from celery.schedules import crontab, schedule
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    imports=['ws.tasks'],
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "realtime-data": {
        "task": "ws.tasks.realtime_data",
        "schedule": schedule(run_every=30),  # Runs every minute
    },
}

celery_app.autodiscover_tasks()
