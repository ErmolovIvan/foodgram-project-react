from django.contrib.auth.password_validation import validate_password
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
        if request is None or request.user.is_anonymous:
            return False

        return Subscribe.objects.filter(
            user=request.user,
            author=value
        ).exist()


class SignUpSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        )

    def validate_username(self, value):
        invalid_usernames = ['me', 'set_password', 'subscriptions']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                'Использовать данный username запрещено.'
            )

        return value


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля"""
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, value):
        validate_password(value)
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""
    image = Base64ImageField(read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор подписки"""
    is_subscribe = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribe(self, value):
        return (
                self.context.get('request').user.is_authenticated
                and Subscribe.objects.filter(user=self.context['request'].user,
                                             author=value).exists()
        )

    def get_recipes_count(self, value):
        return value.recipes.count()

    def get_recipes(self, value):
        request = self.context.get('request')
        limit = request.get('recipes_limit')
        recipes = value.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializers = RecipeSerializer(recipes, many=True, read_only=True)
        return serializers.data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок"""
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError({'errors': 'Ошибка подписки'})
        return value

    def get_is_subscribed(self, value):
        return (
                self.context.get('request').user.is_authenticated
                and Subscribe.objects.filter(user=self.context['request'].user,
                                             author=value).exists()
        )

    def get_recipes_count(self, value):
        return value.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('name', 'units',)


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

    def get_is_favorited(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and Favorite.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов-ингредиентов"""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    id = serializers.IntegerField(read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
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
        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self._create_set(instance, tags, ingredients)
        instance.save()

        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data
