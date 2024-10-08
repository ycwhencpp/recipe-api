# Generated by Django 3.2.9 on 2024-08-15 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0003_recipelike'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=50)),
                ('sender', models.CharField(max_length=50)),
                ('subject', models.TextField()),
                ('body', models.TextField()),
                ('mail_type', models.CharField(choices=[('daily_receipe_like', 'daily_receipe_like')], max_length=20)),
                ('is_sent', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MailStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=50)),
                ('sender', models.CharField(max_length=50)),
                ('subject', models.TextField()),
                ('body', models.TextField()),
                ('mail_type', models.CharField(choices=[('daily_receipe_like', 'daily_receipe_like')], max_length=20)),
                ('sent_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RecipeLikeNotifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe_likes_today', models.IntegerField()),
                ('recipe_likes_weekly', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipe.recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
