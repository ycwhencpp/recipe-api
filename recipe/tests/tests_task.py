import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from ..models import Recipe, RecipeLikeNotifications, MailQueue, RecipeCategory
from recipe.tasks import create_or_update_recipe_like_notification_for_mail, process_daily_recipe_like_notifications, process_mail_queue
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from datetime import time

User = get_user_model()

class TasksTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.category = RecipeCategory.objects.create(name='category')
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')

        self.recipe = Recipe.objects.create(
            author=self.user,
            category=self.category,
            title='test',
            desc='test',
            cook_time=time(1, 30),
            ingredients='test',
            procedure='test',
            picture= SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        )

    @patch('recipe.tasks.logger.info')
    def test_create_or_update_recipe_like_notification_for_mail(self, mock_logger):
        create_or_update_recipe_like_notification_for_mail(self.recipe.id)

        notification = RecipeLikeNotifications.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(notification.recipe_likes_today, 1)
        self.assertEqual(notification.recipe_likes_weekly, 1)

        mock_logger.assert_called_with(f"First like for {self.user.email} on recipe {self.recipe.title}")

        create_or_update_recipe_like_notification_for_mail(self.recipe.id)
        notification.refresh_from_db()
        self.assertEqual(notification.recipe_likes_today, 2)
        self.assertEqual(notification.recipe_likes_weekly, 2)

    @patch('recipe.tasks.MailQueue.objects.create')
    def test_process_daily_recipe_like_notifications(self, mock_create_mail):
        RecipeLikeNotifications.objects.create(
            user=self.user,
            recipe=self.recipe,
            recipe_likes_today=5,
            recipe_likes_weekly=10
        )

        process_daily_recipe_like_notifications()

        mock_create_mail.assert_called_once()
        notification = RecipeLikeNotifications.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(notification.recipe_likes_today, 0)

    @patch('recipe.tasks.send_mail')
    @patch('recipe.tasks.MailStat.objects.create')
    def test_process_mail_queue(self, mock_create_mail_stat, mock_send_mail):
        MailQueue.objects.create(
            recipient=self.user.email,
            sender='noreply@example.com',
            subject='Test Subject',
            body='Test Body',
            mail_type='test_type',
            is_sent=False
        )

        process_mail_queue()

        mock_send_mail.assert_called_once()
        mock_create_mail_stat.assert_called_once()
        self.assertEqual(MailQueue.objects.filter(is_sent=True).count(), 1)