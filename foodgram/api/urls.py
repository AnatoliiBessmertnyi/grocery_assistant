from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FollowViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)
from .user_views import UserViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)
router.register('follow', FollowViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
