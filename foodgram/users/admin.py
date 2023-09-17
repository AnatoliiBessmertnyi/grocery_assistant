from django.contrib import admin

from recipes.models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", 'username', 'first_name', 'last_name')
    search_fields = ("username",)
