from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe
from users.models import User, Subscribe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
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
        return Subscribe.objects.filter(user=request.user,
                                        author=value).exist()


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

        def validate_username(self, value):
            if value == 'me' or 'subscriptions' or 'set_password':
                raise serializers.ValidationError(
                    'Использовать данный username запрещено.'
                )

            return value


class SetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, value):
        validate_password(value)
        return value


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
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
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
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
        if (self.context['request'].user == value):
            raise serializers.ValidationError({'errors': 'Ошибка подписки'})
        return value

    def get_is_subscribe(self, value):
        return (
                self.context.get('request').user.is_authenticated
                and Subscribe.objects.filter(user=self.context['request'].user,
                                             author=value).exists()
        )

    def get_recipes_count(self, value):
        return value.recipes.count()
