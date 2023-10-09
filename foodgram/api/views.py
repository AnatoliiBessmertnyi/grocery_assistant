import io

from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter
from .serializers import (IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, SubscribeRecipeSerializer,
                          SubscribeSerializer, TagSerializer)

User = get_user_model()


class SubscribeViewSet(
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView,):
    """Управление подписками на пользователей и их рецепты."""
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        """Получение списка подписок пользователя с информацией о рецептах."""
        return self.request.user.follower.select_related(
            'following'
        ).prefetch_related(
            'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True),
        )

    def get_object(self):
        """Получение объекта пользователя по его идентификатору."""
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        """Создание подписки на другого пользователя."""
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {'errors': 'Нельзя подписаться на себя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.follower.filter(author=instance).exists():
            return Response(
                {'errors': 'Вы уже подписаны!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subs = request.user.follower.create(author=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Удаление подписки на пользователя."""
        self.request.user.follower.filter(author=instance).delete()


class FavoriteRecipeViewSet(
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView):
    """Управление избранными рецептами."""
    serializer_class = SubscribeRecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Получение объекта рецепта по его идентификатору."""
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe

    def create(self, request, *args, **kwargs):
        """Добавление рецепта в избранное."""
        instance = self.get_object()
        favorite_recipe, created = (
            FavoriteRecipe.objects.get_or_create(user=request.user))
        if not favorite_recipe.recipe.filter(id=instance.id).exists():
            favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Удаление рецепта из избранного."""
        self.request.user.favorite_recipe.recipe.remove(instance)


class ShoppingCartViewSet(
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView):
    """Управление корзиной покупок."""
    serializer_class = SubscribeRecipeSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        """Получение объекта рецепта по его идентификатору."""
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe

    def create(self, request, *args, **kwargs):
        """Добавление рецепта в корзину покупок."""
        instance = self.get_object()
        request.user.shopping_cart.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Удаление рецепта из корзины покупок."""
        self.request.user.shopping_cart.recipe.remove(instance)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в виде PDF файла."""
        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        x_position, y_position = 50, 800
        shopping_cart = (
            request.user.shopping_cart.recipe.
            values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by()
        )
        page.setFont('FreeSans', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["ingredients__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredients__measurement_unit"]}.'
                )
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename='shoppingcart.pdf'
            )
        page.setFont('FreeSans', 24)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!',
        )
        page.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shoppingcart.pdf'
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """Управление рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        """Определение класса сериализатора в зависимости от действия."""
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer

    def get_queryset(self):
        """Получение списка рецептов с информацией о пользователе."""
        return Recipe.objects.annotate(
            is_favorited=Exists(
                FavoriteRecipe.objects.filter(
                    user=self.request.user, recipe=OuterRef('id')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('id')
                )
            )
        ).select_related('author').prefetch_related(
            'tags', 'ingredients', 'recipe',
            'shopping_cart', 'favorite_recipe'
        ) if self.request.user.is_authenticated else Recipe.objects.annotate(
            is_in_shopping_cart=Value(False),
            is_favorited=Value(False),
        ).select_related('author').prefetch_related(
            'tags', 'ingredients', 'recipe',
            'shopping_cart', 'favorite_recipe'
        )

    def perform_create(self, serializer):
        """Создание нового рецепта с указанием автора."""
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """Управление категориями рецептов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Управление ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
