from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.expressions import Exists, OuterRef, Value
from djoser.views import UserViewSet
from recipes.models import Subscribe
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .serializers import (SubscribeSerializer, TokenSerializer,
                          UserCreateSerializer, UserListSerializer)

User = get_user_model()


class SubscribtionViewSet(viewsets.ModelViewSet):
    """Управление подписками пользователей."""
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Получение списка подписок для текущего пользователя."""
        return Subscribe.objects.filter(user=self.request.user)


class UsersViewSet(UserViewSet):
    """Управление пользователями."""
    serializer_class = UserListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Получение списка пользователей с информацией о подписках."""
        return User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.follower.filter(
                    author=OuterRef('id'))
            )).prefetch_related(
                'follower', 'following'
        ) if self.request.user.is_authenticated else User.objects.annotate(
            is_subscribed=Value(False))

    def get_serializer_class(self):
        """Определение класса сериализатора."""
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        """Создание нового пользователя с хешированным паролем."""
        password = make_password(self.request.data['password'])
        serializer.save(password=password)


class AuthToken(ObtainAuthToken):
    """Создание аутентификационного токена пользователя."""
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """Обработка запроса и создание токена."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED,
        )


# Исходный вариант
# from django.contrib.auth import get_user_model
# from django.contrib.auth.hashers import make_password
# from django.db.models.expressions import Exists, OuterRef, Value
# from djoser.views import UserViewSet
# from recipes.models import Subscribe
# from rest_framework import permissions, status
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.decorators import action
# from rest_framework.response import Response

# from .serializers import (SubscribeSerializer, TokenSerializer,
#                           UserCreateSerializer, UserListSerializer)

# User = get_user_model()


# class UsersViewSet(UserViewSet):
#     serializer_class = UserListSerializer
#     permission_classes = (permissions.IsAuthenticated,)

#     def get_queryset(self):
#         return User.objects.annotate(
#             is_subscribed=Exists(
#                 self.request.user.follower.filter(
#                     author=OuterRef('id'))
#             )).prefetch_related(
#                 'follower', 'following'
#         ) if self.request.user.is_authenticated else User.objects.annotate(
#             is_subscribed=Value(False))

#     def get_serializer_class(self):
#         if self.request.method.lower() == 'post':
#             return UserCreateSerializer
#         return UserListSerializer

#     def perform_create(self, serializer):
#         password = make_password(self.request.data['password'])
#         serializer.save(password=password)

#     @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
#     def subscriptions(self, request):
#         user = request.user
#         queryset = Subscribe.objects.filter(user=user)
#         pages = self.paginate_queryset(queryset)
#         serializer = SubscribeSerializer(
#             pages, many=True,
#             context={'request': request},
#         )
#         return self.get_paginated_response(serializer.data)


# class AuthToken(ObtainAuthToken):
#     """Создание аутентификационного токена пользователя."""
#     serializer_class = TokenSerializer
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, *args, **kwargs):
#         """Обработка запроса и создание токена."""
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response(
#             {'auth_token': token.key},
#             status=status.HTTP_201_CREATED,
#         )

