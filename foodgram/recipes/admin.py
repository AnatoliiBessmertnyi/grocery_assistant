from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Subscribe,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    list_display = ('measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'get_author',
        'get_tags',
        'get_ingredients',
        'cooking_time',
        'text',
        'pub_date',
    )
    search_fields = ('name',)
    inlines = (RecipeIngredientAdmin,)
    empty_value_display = '-пусто-'

    @admin.display(description='Email автора')
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        list_ = [_.name for _ in obj.tags.all()]
        return ', '.join(list_)

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join(
            [
                f'{item["ingredient__name"]} - {item["amount"]}'
                f'{item["ingredient__name"]} - {item["amount"]}'
                f' {item["ingredient__measurement_unit"]}.'
                for item in obj.recipe.values(
                    'ingredient__name',
                    'amount',
                    'ingredient__measurement_unit',
                )
            ],
        )

    @admin.display(description='Избранное')
    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_recipe')
    empty_value_display = '-пусто-'

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [f'{item["name"]} ' for item in obj.recipe.values('name')[:6]]


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_recipe')
    empty_value_display = '-пусто-'

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [f'{item["name"]} ' for item in obj.recipe.values('name')[:6]]


admin.site.register(RecipeIngredient)
