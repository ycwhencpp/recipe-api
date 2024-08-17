import logging
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import F
from django.db import transaction
from django.conf import settings
from .models import RecipeLikeNotifications, Recipe, MailQueue, MailStat
from decouple import config


logger = logging.getLogger('recipe')
User = get_user_model()

@shared_task
def create_or_update_recipe_like_notification_for_mail(recipe_id):
    """
    Create or update a RecipeLikeNotifications entry for a recipe like.
    """
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        author = recipe.author

        notification, created = RecipeLikeNotifications.objects.get_or_create(
            user=author, 
            recipe=recipe,
            defaults={'recipe_likes_today': 0, 'recipe_likes_weekly': 0}
        )
        notification.recipe_likes_today = F('recipe_likes_today') + 1
        notification.recipe_likes_weekly = F('recipe_likes_weekly') + 1
        notification.save()

        logger.info(f"{'First' if created else 'New'} like for {author.email} on recipe {recipe.title}")

    except Recipe.DoesNotExist:
        logger.error(f"Recipe with id {recipe_id} does not exist")
    except Exception as e:
        logger.error(f"Error in create_or_update_recipe_like_notification_for_mail: {str(e)}")

@shared_task
def process_daily_recipe_like_notifications(limit=100):
    """
    Process daily recipe like notifications and create mail queue entries.
    """
    offset = 0
    sender_email = config('EMAIL_USER')
    while True:
        notifications = RecipeLikeNotifications.objects.filter(recipe_likes_today__gt=0, id__gt=offset).order_by('id')[:limit]

        if not notifications.exists():
            break  

        for notification in notifications:
            try:
                with transaction.atomic():
                    offset = notification.id
                    
                    MailQueue.objects.create(
                        recipient=notification.user.email,
                        sender=sender_email,
                        subject=f"You got {notification.recipe_likes_today} likes today on your {notification.recipe.title}",
                        body=f"You got {notification.recipe_likes_today} likes today on your {notification.recipe.title}",
                        mail_type='daily_recipe_like',
                        is_sent=False
                    )
                    
                    notification.recipe_likes_today = 0
                    notification.save()
            except Exception as e:
                logger.error(f"Error processing item {notification.id}: {str(e)}")


@shared_task
def process_mail_queue(limit=100):
    """
    Process mail queue and send emails.
    """
    offset = 0
    while True:
        mails = MailQueue.objects.filter(is_sent=False, id__gt=offset).order_by('id')[:limit]
        if not mails.exists():
            break  

        for mail in mails:
            try:
                with transaction.atomic():
                    offset = mail.id
                    send_mail(
                        subject=mail.subject,
                        message=mail.body,
                        from_email=mail.sender,
                        recipient_list=[mail.recipient],
                    )

                    mail.is_sent = True
                    mail.save()

                    MailStat.objects.create(
                        sender =mail.sender ,
                        recipient = mail.recipient,
                        subject=mail.subject,
                        body=mail.body,
                        mail_type = mail.mail_type,
                        sent_at =timezone.now()
                    )
            except Exception as e:
                logger.error(f"Error processing item {mail.id}: {str(e)}")