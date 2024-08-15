from rest_framework import serializers

from .models import Recipe, RecipeCategory, RecipeLike, MailQueue, MailStat, RecipeLikeNotifications

from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ('id', 'name')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    category = RecipeCategorySerializer()
    total_number_of_likes = serializers.SerializerMethodField()
    total_number_of_bookmarks = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'category', 'category_name', 'picture', 'title', 'desc',
                  'cook_time', 'ingredients', 'procedure', 'author', 'username',
                  'total_number_of_likes', 'total_number_of_bookmarks')

    def get_username(self, obj):
        return obj.author.username

    def get_category_name(self, obj):
        return obj.category.name

    def get_total_number_of_likes(self, obj):
        return obj.get_total_number_of_likes()

    def get_total_number_of_bookmarks(self, obj):
        return obj.get_total_number_of_bookmarks()

    def create(self, validated_data):
        category = validated_data.pop('category')
        category_instance, created = RecipeCategory.objects.get_or_create(
            **category)
        recipe_instance = Recipe.objects.create(
            **validated_data, category=category_instance)
        return recipe_instance

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            nested_serializer = self.fields['category']
            nested_instance = instance.category
            nested_data = validated_data.pop('category')

            nested_serializer.update(nested_instance, nested_data)

        return super(RecipeSerializer, self).update(instance, validated_data)


class RecipeLikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RecipeLike
        fields = ('id', 'user', 'recipe')



class MailQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailQueue
        fields = ['id', 'recipient', 'sender', 'subject', 'body', 'mail_type', 'is_sent', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_mail_type(self, value):
        valid_types = dict(MailQueue.MAIL_TYPES).keys()
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid mail type. Choose from {', '.join(valid_types)}")
        return value

class MailStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailStat
        fields = ['id', 'recipient', 'sender', 'subject', 'body', 'mail_type', 'sent_at', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_mail_type(self, value):
        valid_types = dict(MailStat.MAIL_TYPES).keys()
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid mail type. Choose from {', '.join(valid_types)}")
        return value

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title']


class RecipeLikeNotificationsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = RecipeSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        write_only=True, 
        source='user'
    )
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), 
        write_only=True, 
        source='recipe'
    )

    class Meta:
        model = RecipeLikeNotifications
        fields = ['id', 'user', 'recipe', 'user_id', 'recipe_id', 'recipe_likes_today', 'recipe_likes_weekly', 'created_at']
        read_only_fields = ['id', 'created_at']