from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Recipe, RecipeCategory, RecipeLike
from .serializers import RecipeSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from datetime import time

User = get_user_model()

class BaseTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@com.com')
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
    def tearDown(self):
        for recipe in Recipe.objects.all():
            if recipe.picture:
                recipe.picture.delete()

class RecipeListAPIViewTest(BaseTestCase):
    def test_recipe_list(self):
        url = reverse('recipe:recipe-list')
        response = self.client.get(url)
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        def normalize_picture_field(data):
            for item in data:
                if 'picture' in item:
                    item['picture'] = item['picture'].replace('http://testserver', '')
            return data
        response_data_normalized = normalize_picture_field(response.data)
        serializer_data_normalized = normalize_picture_field(serializer.data)
        self.assertEqual(response_data_normalized, serializer_data_normalized)

    def test_recipe_list_filter(self):
        url = reverse('recipe:recipe-list')
        response = self.client.get(url, {'category__name': 'category'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(url, {'author__username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class RecipeCreateAPIViewTest(BaseTestCase):
    def test_recipe_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-create')
        
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        picture = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        data = {
            'title': 'title',
            'desc': 'desc',
            'cook_time': '02:30:00',  
            'ingredients': 'ingredients',
            'procedure': 'procedure',
            'picture': picture,
            'category.name': 'indian'
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        self.assertEqual(Recipe.objects.latest('id').title, 'title')

    def test_unauthenticated_recipe_create(self):
        url = reverse('recipe:recipe-create')
        data = {
            'category': self.category.id,
            'title': 'title',
            'desc': 'desc',
            'cook_time': '02:30:00',  
            'ingredients': 'ingredients',
            'procedure': 'procedure',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class RecipeAPIViewTest(BaseTestCase):
    def test_recipe_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        data = {
            'title': 'updated title',
            'desc': 'updated desc'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'updated title')

    def test_recipe_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_unauthorized_recipe_update(self):
        other_user = User.objects.create_user(username='otheruser', email='other@com.com', password='otherpass')
        self.client.force_authenticate(user=other_user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        data = {
            'title': 'test title'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_recipe_delete(self):
        other_user = User.objects.create_user(username='otheruser', email='other@com.com', password='otherpass')
        self.client.force_authenticate(user=other_user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class RecipeLikeAPIViewTest(BaseTestCase):
    def test_recipe_like(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-like', kwargs={'pk': self.recipe.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(RecipeLike.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_recipe_unlike(self):
        self.client.force_authenticate(user=self.user)
        RecipeLike.objects.create(user=self.user, recipe=self.recipe)
        url = reverse('recipe:recipe-like', kwargs={'pk': self.recipe.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(RecipeLike.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_unauthenticated_recipe_like(self):
        url = reverse('recipe:recipe-like', kwargs={'pk': self.recipe.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# coverage run --source='.' manage.py test
# coverage report -m
# coverage html 
# python manage.py test