from celery import Celery
from app.core.config import settings

celery = Celery(
    "medical_ai_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.services.inference_service"]
)

# Celery全局配置
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)