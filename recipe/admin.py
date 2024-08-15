from django.contrib import admin
from .models import RecipeCategory, Recipe, RecipeLike, MailQueue, MailStat, RecipeLikeNotifications

# Register your models here.
admin.site.register(RecipeCategory)
admin.site.register(Recipe)
admin.site.register(RecipeLike)

admin.site.register(RecipeLikeNotifications)
admin.site.register(MailQueue)
admin.site.register(MailStat)
