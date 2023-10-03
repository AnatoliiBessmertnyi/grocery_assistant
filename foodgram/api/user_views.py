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
    # TokenSerializer,
    # UserCreateSerializer,
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

