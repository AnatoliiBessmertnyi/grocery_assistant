from rest_framework import filters, mixins, viewsets

from .permissions import AdminOrReadOnly


class GetPostDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('=slug',)
    search_fields = ('name',)
