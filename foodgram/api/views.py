from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .filters import RecipeFilter
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer)

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Управление ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (ReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    """Управление категориями рецептов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (ReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Управление рецептами."""
    queryset = Recipe.objects.prefetch_related(
        'author', 'tags', 'ingredients').all()
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        """Создание нового рецепта."""
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        """Добавляет/удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            _, created = Favorite.objects.get_or_create(
                recipe=recipe, user=request.user)
            serializer = RecipeListSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            fav_recipe = get_object_or_404(
                Favorite, recipe=recipe, user=request.user)
            fav_recipe.delete()
            return Response(
                {"Успешно": "Рецепт удален."},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        """Добавляет/удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            _, created = ShoppingCart.objects.get_or_create(
                recipe=recipe, user=request.user)
            serializer = RecipeListSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            cart_recipe = get_object_or_404(
                ShoppingCart, recipe=recipe, user=request.user)
            cart_recipe.delete()
            return Response(
                {"Успешно": "Рецепт удален."},
                status=status.HTTP_204_NO_CONTENT
            )


class DownloadShoppingCartView(views.APIView):
    """Скачивание списка покупок в виде PDF файла."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Обработчик GET-запроса для создания и возврата списка покупок в виде
        PDF файла."""
        buffer = BytesIO()
        page = canvas.Canvas(buffer, pagesize=letter)
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        x_position, y_position = 50, 800
        shopping_cart = (
            Recipe.objects.filter(shopping_cart__user=request.user)
            .values(
                'ingredients__name',
                'ingredients__measurement_unit'
            )
            .annotate(amount=Sum('recipeingredient__amount'))
            .order_by()
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
            response = FileResponse(
                buffer, content_type='application/pdf')
            response['Content-Disposition'] = (
                'attachment; filename="shoppingcart.pdf"')
            return response
        page.setFont('FreeSans', 24)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!',
        )
        page.save()
        buffer.seek(0)
        response = FileResponse(
            buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shoppingcart.pdf"')
        return response


class UserViewSet(DjoserUserViewSet):
    """Управление пользователями."""
    serializer_class = SubscriptionSerializer
    pagination_class = PageNumberPagination

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Подписать на автора рецепта."""
        author = get_object_or_404(User, pk=id)
        _, created = Subscription.objects.get_or_create(
            author=author, subscriber=request.user)
        serializer = self.get_serializer(
            author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        """Отписывает от автора рецепта."""
        author = get_object_or_404(User, pk=id)
        subscription = get_object_or_404(
            Subscription, author=author, subscriber=request.user)
        subscription.delete()
        return Response({"success": "Вы успешно отписаны."},
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        authors = User.objects.filter(subscription__subscriber=request.user)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            authors, many=True, context={'request': request})
        return Response(serializer.data)
