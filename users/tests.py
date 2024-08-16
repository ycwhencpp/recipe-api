from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from recipe.models import Recipe, RecipeCategory
from .models import Profile
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from datetime import time

User = get_user_model()

class BaseTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser10@example.com', password='testpassword', username='testuser10')
    def tearDown(self):
        Profile.objects.all().delete()
        User.objects.all().delete()

class UserRegisterationAPIViewTest(BaseTestCase):
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

class UserLoginAPIViewTest(BaseTestCase):
    def test_user_login(self):
        url = reverse('users:login-user')
        data = {
            'email': 'testuser10@example.com',
            'password': 'testpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

class UserLogoutAPIViewTest(BaseTestCase):
    def test_user_logout(self):
        refresh_token = RefreshToken.for_user(self.user)
        url = reverse('users:logout-user')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
        data = {'refresh': str(refresh_token)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

class UserAPIViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_user_get(self):
        url = reverse('users:user-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update(self):
        url = reverse('users:user-info')
        data = {'email': 'updateduser@example.com'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updateduser@example.com')

class UserProfileAPIViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_user_profile_get(self):
        url = reverse('users:user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile_update(self):
        url = reverse('users:user-profile')
        data = {'bio': 'Updated bio'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')

class UserAvatarAPIViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_user_avatar_get(self):
        url = reverse('users:user-avatar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_avatar_update(self):
        url = reverse('users:user-avatar')
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        avatar = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        data = {'avatar': avatar}
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserBookmarkAPIViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.category = RecipeCategory.objects.create(name='test')
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        self.recipe = Recipe.objects.create(
            author=self.user,
            category=self.category,
            title='test',
            desc='test',
            cook_time=time(1, 30),
            ingredients='test',
            procedure='test',
            picture=SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        )

    def test_user_bookmark_list(self):
        url = reverse('users:user-bookmark', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_bookmark_create(self):
        url = reverse('users:user-bookmark', kwargs={'pk': self.user.id})
        data = {'id': self.recipe.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_bookmark_delete(self):
        self.user.profile.bookmarks.add(self.recipe)
        url = reverse('users:user-bookmark', kwargs={'pk': self.user.id})
        data = {'id': self.recipe.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PasswordChangeAPIViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_password_change(self):
        url = reverse('users:change-password')
        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword@newpassword',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
