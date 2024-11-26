# from celery import Celery

# celery_app = Celery(
#     "worker",
#     broker="redis://redis:6379/0",
#     backend="redis://redis:6379/0"
# )

# # Укажите настройки Celery (например, автодетект задач)
# celery_app.conf.update(
#     task_routes={
#         "app.tasks.*": {"queue": "default"}
#     },
#     timezone="UTC",
#     enable_utc=True,
# )

# # Автоматически ищите задачи в модуле tasks
# celery_app.autodiscover_tasks(["services.stt_service"])
