from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .models import Recipe
from .serializers import (
    RecipeSerializer, UserSerializer, RecipeListSerializer
)

User = get_user_model()

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer 

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer 


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer 
