from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Follow, Ingredient, Recipe, Tag
from rest_framework import (
    filters, permissions, serializers, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import FavoriteRecipe, ShoppingCart
from .serializers import (
    FavoriteRecipeSerializer,
    FavoriteShoppingSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


def custom_post_delete(self, request, pk, model):
    """Функция-обработчик POST, DELETE запросов."""
    user = self.request.user
    recipe = self.get_object()
    if request.method == 'DELETE':
        instance = model.objects.filter(recipe=recipe, user=user)
        if not instance:
            raise serializers.ValidationError(
                {
                    'errors': [
                        'Этого рецепта нету в списке.'
                    ]
                }
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = {
        'user': user.id,
        'recipe': pk,
    }
    favorite = self.get_serializer(data=data)
    favorite.is_valid(raise_exception=True)
    favorite.save()
    serializer = FavoriteShoppingSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        if self.action == 'favorite':
            return FavoriteRecipeSerializer
        if self.action == 'shopping_car':
            return ShoppingCartSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'], detail=True,
    )
    def favorite(self, request, pk):
        model = FavoriteRecipe
        return custom_post_delete(self, request, pk, model)

    @action(
        methods=['POST', 'DELETE'], detail=True,
    )
    def shopping_cart(self, request, pk):
        model = ShoppingCart
        return custom_post_delete(self, request, pk, model)

# Тут нужно реализовать скачивание рецептов в пдф формате


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
