
# from django.urls import path

# from .views import RecipeList, RecipeDetail# APIRecipe # api_recipes, api_recipes_detail

# urlpatterns = [
#     path('api/recipes/', RecipeList.as_view(), name='api_recipes'),
#     path(
#         'api/recipes/<int:pk>/', RecipeDetail.as_view(), name='api_recipes_pk'
#     ),
    # path('api/recipes/', api_recipes, name='api_recipes'),
    # path('api/recipes/<int:pk>/', api_recipes_detail, name='api_recipes_pk'),
# ]

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from recipes.views import RecipeViewSet

router = DefaultRouter()
router.register('api/recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
] 