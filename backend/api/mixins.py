from rest_framework import mixins
from rest_framework import viewsets


class ListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass
