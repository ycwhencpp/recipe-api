from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import RecipeLikeNotifications, Recipe, MailQueue, MailStat
from django.db.models import F
from django.db import transaction


User = get_user_model()

@shared_task
def create_or_update_recipe_like_notification_for_mail(recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    author = recipe.author

    try:
        recipe_like_notification = RecipeLikeNotifications.objects.get(user=author, recipe=recipe)
        print(f"${recipe_like_notification.recipe_likes_today} like for ${author.email}")

        recipe_like_notification.recipe_likes_today = F('recipe_likes_today') + 1
        recipe_like_notification.recipe_likes_weekly = F('recipe_likes_weekly') + 1
        recipe_like_notification.save()

    except RecipeLikeNotifications.DoesNotExist:
        print(f"first like for ${author.email}")

        recipe_like_notification = RecipeLikeNotifications.objects.create(
            user=author,
            recipe=recipe,
            recipe_likes_today=1,
            recipe_likes_weekly=1
        )

@shared_task
def process_daily_recipe_like_notifications(limit=100):
    offset = 0
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
                        sender='noreply@example.com',
                        subject=f"You got {notification.recipe_likes_today} likes today on your {notification.recipe.title}",
                        body=f"You got {notification.recipe_likes_today} likes today on your {notification.recipe.title}",
                        mail_type='daily_recipe_like',
                        is_sent=False
                    )
                    
                    notification.recipe_likes_today = 0
                    notification.save()
            except Exception as e:
                pass


@shared_task
def process_mail_queue(limit=100):
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
                pass








