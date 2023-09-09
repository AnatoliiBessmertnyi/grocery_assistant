
from django.urls import path

from .views import api_recipes, api_recipes_detail

urlpatterns = [
    path('api/recipes/', api_recipes, name='api_recipes'),
    path('api/recipes/<int:pk>/', api_recipes_detail, name='api_recipes_pk'),
]