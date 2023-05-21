from django.contrib.admin import ModelAdmin, TabularInline, register

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


class RecipeIngredient(TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'tags')
    list_filter = ['name', 'author', 'tags']
    inlines = (RecipeIngredient,)


@register(ShoppingCart)
class ShoppingListAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    empty_value_display = '-пусто-'


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    empty_value_display = '-пусто-'
