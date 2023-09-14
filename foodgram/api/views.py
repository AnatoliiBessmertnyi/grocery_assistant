from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Ingredient
from .serializers import (
    RecipeSerializer, UserSerializer, RecipeListSerializer,
    IngredientSerializer,
)
from .permissions import AuthorOrReadOnly , ReadOnly


User = get_user_model()

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)

# Вывод информации на главной и в подробностях рецепта разный
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer