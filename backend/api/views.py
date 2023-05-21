from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User, Subscribe

from .mixins import CreateListRetrieveViewSet
from .serializers import UserSerializer, SignUpSerializer, SetPasswordSerializer, SubscriptionsSerializer, SubscribeSerializer
from .pagination import CustomPaginator


class UserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return SignUpSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer
        if serializer.is_valid():
            serializer.save()
        return Response(
            {'detail': 'Пароль успешно изменен!'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPaginator
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )

        @action(
            detail=False,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,)
        )
        def subscribe(self, request, **kwargs):
            author = get_object_or_404(User, id=kwargs['pk'])

            if request.method == 'POST':
                serializer = SubscribeSerializer(
                    author,
                    data=request.data,
                    context={"request": request}
                )
                serializer.is_valid(raise_exception=True)
                Subscribe.objects.create(user=request.user, author=author)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            if request.method == 'DELETE':
                get_object_or_404(Subscribe, user=request.user,
                                  author=author).delete()
                return Response({'detail': 'Успешная отписка'},
                                status=status.HTTP_204_NO_CONTENT)
