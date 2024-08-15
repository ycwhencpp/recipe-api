import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('recipe_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'process-daily-recipe-likes': {
        'task': 'recipe.tasks.process_daily_recipe_like_notifications',
        'schedule': crontab(hour=0, minute=00),  # Runs daily at 12:00 AM
    },
    'process-mail-queue': {
        'task': 'recipe.tasks.process_mail_queue',
        'schedule':crontab(minute='*/10'),  # Runs every 10 minute
    },
}

# command to run celery 

# celery -A config.settings.celery worker --loglevel=debug
# redis-server
#python manage.py migrate django_celery_beat
# celery -A your_project_name beat --loglevel=info
