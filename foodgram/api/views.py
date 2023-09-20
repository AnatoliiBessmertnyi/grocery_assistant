from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Follow, Ingredient, Recipe, Tag
from rest_framework import (
    filters, permissions, serializers, status, views, viewsets
)
from rest_framework.decorators import action
# from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser as User
from recipes.models import FavoriteRecipe, ShoppingCart
from .serializers import (
    FavoriteRecipeSerializer,
    FavoriteShoppingSerializer,
    FollowSerializer,
    IngredientSerializer,
    ProfileEditSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer,
)


def custom_post_delete(self, request, pk, model):
    '''Функция-обработчик POST, DELETE запросов '''
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
        methods=['post', 'delete'], detail=True,
    )
    def favorite(self, request, pk):
        model = FavoriteRecipe
        return custom_post_delete(self, request, pk, model)

    @action(
        methods=['post', 'delete'], detail=True,
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = ProfileEditSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data['username']
        user, _ = User.objects.get_or_create(email=email, username=username)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=(user.email,),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        # confirmation_code = serializer.data['confirmation_code']
        # if not default_token_generator.check_token(user, confirmation_code):
        #     raise ValidationError(serializer.errors)
        token = AccessToken.for_user(user)
        data = {}
        data['token'] = str(token)
        return Response(data, status=status.HTTP_200_OK)
