from app.config import get_settings
from celery import Celery

settings = get_settings()

celery = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


@celery.task(name="add")
def add(x: int, y: int) -> int:
    return x + y
