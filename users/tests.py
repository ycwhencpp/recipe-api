from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from recipe.models import Recipe, RecipeCategory
from .models import Profile
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from datetime import time

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser10@example.com', password='testpassword', username='testuser10')


    def test_user_registration(self):
        url = reverse('users:create-user')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)

    def test_user_login(self):
        url = reverse('users:login-user')
        data = {
            'email': 'testuser10@example.com',
            'password': 'testpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_user_logout(self):
        refresh_token = RefreshToken.for_user(self.user)
        url = reverse('users:logout-user')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
        data = {'refresh': str(refresh_token)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_user_get(self):
        url = reverse('users:user-info')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update(self):
        url = reverse('users:user-info')
        self.client.force_authenticate(user=self.user)
        data = {'email': 'updateduser@example.com'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updateduser@example.com')

    def test_user_profile_get(self):
        url = reverse('users:user-profile')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_update(self):
        url = reverse('users:user-profile')
        self.client.force_authenticate(user=self.user)
        data = {'bio': 'Updated bio'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')

    def test_user_avatar_get(self):
        url = reverse('users:user-avatar')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_avatar_update(self):
        url = reverse('users:user-avatar')
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        avatar = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        self.client.force_authenticate(user=self.user)
        data = {'avatar': avatar}
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_bookmark_list(self):
        url = reverse('users:user-bookmark', kwargs={'pk': self.user.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_bookmark_create(self):
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        category = RecipeCategory.objects.create(name='Test Category')

        recipe = Recipe.objects.create(
            author=self.user,
            category=category,
            title='Test Recipe',
            desc='Test Description',
            cook_time=time(1, 30),
            ingredients='Test Ingredients',
            procedure='Test Procedure',
            picture= SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        )
        url = reverse('users:user-bookmark', kwargs={'pk': self.user.id})
        self.client.force_authenticate(user=self.user)
        data = {'id': recipe.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_bookmark_delete(self):
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        category = RecipeCategory.objects.create(name='Test Category')
        recipe = Recipe.objects.create(
            author=self.user,
            category=category,
            title='Test Recipe',
            desc='Test Description',
            cook_time=time(1, 30),
            ingredients='Test Ingredients',
            procedure='Test Procedure',
            picture= SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        )

        self.user.profile.bookmarks.add(recipe)
        url = reverse('users:user-bookmark', kwargs={'pk': self.user.id})
        self.client.force_authenticate(user=self.user)
        data = {'id': recipe.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change(self):
        url = reverse('users:change-password')
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword@newpassword',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        Profile.objects.all().delete()
        User.objects.all().delete()
