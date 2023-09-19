from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FollowViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    TokenView,
    UserSignUpView,
    UserViewSet,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)
router.register('follow', FollowViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', UserSignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='get_token'),
]
