from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .user_views import AuthToken, SubscribtionViewSet, UsersViewSet
from .views import (DownloadShoppingCartView, FavoriteRecipeViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                    SubscribeViewSet, TagViewSet)

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UsersViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('users/<int:user_id>/subscribe/', SubscribeViewSet.as_view(),
         name='subscribe'),
    path('users/subscriptions/', SubscribtionViewSet.as_view({'get': 'list'})),
    path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeViewSet.as_view(),
         name='favorite_recipe'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartViewSet.as_view(), name='shopping_cart'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartView.as_view(),
         name='download_shopping_cart'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
