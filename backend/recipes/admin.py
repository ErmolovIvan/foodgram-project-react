from django.contrib.admin import ModelAdmin, TabularInline, register, display

from .models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                     ShoppingCart, Tag)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'
    ordering = ('color',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'units')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    ordering = ('name',)


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'


@register(ShoppingCart)
class ShoppingListAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    empty_value_display = '-пусто-'


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    empty_value_display = '-пусто-'
