from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Favorite)
from users.models import User, Subscribe


class UserListSerializer(UserSerializer):
    """Сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, value):
        request = self.context.get('request')

        return (
                request.user.is_authenticated
                and request.user.subscriber.filter(author=value).exists()
        )


class SignUpSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        invalid_usernames = ['me', 'set_password', 'subscriptions']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                'Использовать данный username запрещено.'
            )

        return value


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с краткой информацией о рецепте"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""
    image = Base64ImageField(read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор информации о подписках пользователя"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, value):
        request = self.context.get('request')

        return (
                request.user.is_authenticated
                and request.user.subscriber.filter(author=value).exists()
        )

    def get_recipes_count(self, value):
        return value.recipes.count()

    def get_recipes(self, value):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = value.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializers = RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializers.data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок"""

    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, value):
        request = self.context.get('request')
        if request.user == value['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return value

    def get_is_subscribed(self, value):
        request = self.context.get('request')

        return (
                request.user.is_authenticated
                and request.user.subscriber.filter(author=value).exists()
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionsSerializer(
            instance.author,
            context={'request': request}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'units',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов-ингредиентов"""
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    units = serializers.CharField(source='ingredient.units', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'units', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов"""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, value):
        request = self.context.get('request')

        return (
                request.user.is_authenticated
                and request.user.favorite.filter(recipe=value).exists()
        )

    def get_is_in_shopping_cart(self, value):
        request = self.context.get('request')

        return (
                request.user.is_authenticated
                and request.user.shopping_cart.filter(recipe=value).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов-ингредиентов"""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    def validate(self, value):
        for field in ['name', 'text', 'cooking_time']:
            if not value.get(field):
                raise serializers.ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not value.get('tags'):
            raise serializers.ValidationError(
                'Нужно указать тег.'
            )
        if not value.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно указать ингредиент.'
            )
        inrgedient_id_list = [item['id'] for item in value.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )

        return value

    @staticmethod
    def _create_set(recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self._create_set(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        super().update(instance, validated_data)
        self._create_set(instance, tags, ingredients)
        instance.save()

        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного"""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')

        return RecipeShortSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор корзины"""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в корзину'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': request}
        ).data
