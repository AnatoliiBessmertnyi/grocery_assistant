from rest_framework import viewsets
from django.contrib.auth import get_user_model

from recipes.models import Recipe
from .serializers import (
    RecipeSerializer, UserSerializer, RecipeListSerializer
)

User = get_user_model()

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer 

# Вывод информации на главной и в подробностях рецепта разный
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer 