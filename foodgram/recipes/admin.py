from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagRecipe,
)


class IngredientRecipeAdmin(admin.StackedInline):
    model = IngredientRecipe
    list_display = (
        'measure',
    )


class TagRecipeAdmin(admin.StackedInline):
    model = TagRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'get_tags',
        'get_ingredients',
        'cooking_time',
        'author',
        'text',
        'pub_date',
    )
    search_fields = ('name',)
    inlines = (IngredientRecipeAdmin, TagRecipeAdmin,)
    empty_value_display = '-пусто-'

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        list_ = [_.name for _ in obj.tags.all()]
        return ', '.join(list_)

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measure"]}.'
            for item in obj.recipe.values(
                'ingredient__name',
                'amount',
                'ingredient__measure',
            )])


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following',
    )
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measure',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(FavoriteRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(ShoppingCart)
