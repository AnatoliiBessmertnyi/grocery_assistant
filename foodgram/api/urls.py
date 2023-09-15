from django.urls import include, path

from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    UserViewSet,
    IngredientViewSet,
    FollowViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)
router.register('follow', FollowViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),
    path('', include(router.urls)),
]