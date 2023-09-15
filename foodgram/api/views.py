from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    RecipeSerializer, UserSerializer, RecipeListSerializer,
    IngredientSerializer, FollowSerializer
)
from .permissions import AuthorOrReadOnly , ReadOnly
from recipes.models import Recipe, Ingredient, Follow


User = get_user_model()

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name','tags', 'author')

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
    # Нужно настроить
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('first_name','email')


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
