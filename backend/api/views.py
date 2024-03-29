from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Favorite)
from users.models import User, Subscribe
from .filters import RecipeFilter
from .mixins import ListViewSet, ListRetrieveViewSet
from .pagination import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (SubscriptionsSerializer, SubscribeSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeCreateSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)


class SubscribeView(APIView):
    """Подписка на пользователя"""
    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        get_object_or_404(
            Subscribe,
            user=request.user,
            author=author.id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(ListViewSet):
    """Список подписок"""
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        return User.objects.filter(subscribing__user=self.request.user)


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет тегов"""
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюсет ингредиентов"""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов"""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(Favorite, user=request.user, recipe=recipe).delete()

        return Response(
            {'detail': 'Рецепт успешно удален из избранного.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        ).delete()

        return Response(
            {'detail': 'Рецепт успешно удален из списка покупок.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def download_shopping_cart(self, request, **kwargs):
        filename = 'foodgram_shopping_cart.txt'
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__units'
            )
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)
        ) for ingredient in ingredients]
        file = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(file_list),
            content_type='text/plain'
        )
        file['Content-Disposition'] = f'attachment; filename={filename}'

        return file
