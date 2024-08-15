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

class RecipeAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@com.com')
        self.category = RecipeCategory.objects.create(name='Test Category')
        
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')

        
        self.recipe = Recipe.objects.create(
            author=self.user,
            category=self.category,
            title='Test Recipe',
            desc='Test Description',
            cook_time=time(1, 30),
            ingredients='Test Ingredients',
            procedure='Test Procedure',
            picture= SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        )

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
        serializer_data_normalized = normalize_picture_field( serializer.data)
        self.assertEqual(response_data_normalized, serializer_data_normalized)


    def test_recipe_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-create')
        
        image_path = os.path.join(settings.BASE_DIR, 'recipe', 'test_images', 'test_image.png')
        picture = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        print(f"category {self.category.name}")
        data = {
            'title': 'New Recipe',
            'desc': 'New Description',
            'cook_time': '02:30:00',  
            'ingredients': 'New Ingredients',
            'procedure': 'New Procedure',
            'picture': picture,
            'category': self.category,
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        self.assertEqual(Recipe.objects.latest('id').title, 'New Recipe')



    def test_recipe_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        data = {
            'title': 'Updated Recipe',
            'desc': 'Updated Description'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Updated Recipe')

    def test_recipe_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)

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

    def test_unauthenticated_recipe_create(self):
        url = reverse('recipe:recipe-create')
        data = {
            'category': self.category.id,
            'title': 'New Recipe',
            'desc': 'New Description',
            'cook_time': '00:45:00',
            'ingredients': 'New Ingredients',
            'procedure': 'New Procedure'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_recipe_like(self):
        url = reverse('recipe:recipe-like', kwargs={'pk': self.recipe.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recipe_list_filter(self):
        url = reverse('recipe:recipe-list')
        response = self.client.get(url, {'category__name': 'Test Category'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(url, {'author__username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_recipe_update(self):
        other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='otherpass')
        self.client.force_authenticate(user=other_user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        data = {
            'title': 'Unauthorized Update'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_recipe_delete(self):
        other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='otherpass')
        self.client.force_authenticate(user=other_user)
        url = reverse('recipe:recipe-detail', kwargs={'pk': self.recipe.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        for recipe in Recipe.objects.all():
            if recipe.picture:
                recipe.picture.delete()

# coverage run --source='.' manage.py test
# coverage report -m
# coverage html  # This generates an HTML report you can open in a browser
# python manage.py test
