from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters, permissions,  status, views, viewsets
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from djoser.views import UserViewSet

from .serializers import (
    ProfileEditSerializer,
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()

class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_serializer_context(self):
        return {'user': self.request.user}

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # queryset = User.objects.all()
    # serializer_class = UserSerializer

    # def get_serializer_context(self):
    #     return {'user': self.request.user}

    # @action(detail=False,
    #         methods=['GET', ],
    #         permission_classes=[IsAuthenticated, ],
    #         url_path='me',)
    # def get_me(self, request):
    #     user = get_object_or_404(User, pk=request.user.pk)
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False,
    #         url_path='subscriptions',
    #         serializer_class=SubscriptionListSerializer,
    #         permission_classes=[IsAuthenticated, ],
    #         pagination_class=CustomPagination)
    # def get_subscriptions(self, request):
    #     """
    #     Returns queryset with the recipes of
    #     all authors the user is subscribed to.
    #     """
    #     subscriptions = User.objects.filter(subscribed__user=request.user)
    #     log.info(subscriptions)
    #     pagination = self.paginate_queryset(subscriptions)
    #     if pagination is None:
    #         log.warning('Pagination in subscriptions is disabled')

    #     serializer = self.get_serializer(pagination, many=True)

    #     return self.get_paginated_response(serializer.data)



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
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise ValidationError(serializer.errors)
        token = AccessToken.for_user(user)
        data = {}
        data['token'] = str(token)
        return Response(data, status=status.HTTP_200_OK)
