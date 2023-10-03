from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
     FavoriteRecipeViewSet,
     IngredientViewSet,
     RecipeViewSet,
     ShoppingCartViewSet,
     SubscribeViewSet,
     TagViewSet,
)
from .user_views import AuthToken, UsersViewSet


router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UsersViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
     path('auth/token/login/', AuthToken.as_view(), name='login'),
     path(
          'users/<int:user_id>/subscribe/',
          SubscribeViewSet.as_view(),
          name='subscribe',
     ),
     path(
          'recipes/<int:recipe_id>/favorite/',
          FavoriteRecipeViewSet.as_view(),
          name='favorite_recipe',
     ),
     path(
          'recipes/<int:recipe_id>/shopping_cart/',
          ShoppingCartViewSet.as_view(),
          name='shopping_cart',
     ),
     path('', include(router.urls)),
     path('', include('djoser.urls')),
     path('auth/', include('djoser.urls.authtoken')),
]
