from rest_framework import serializers
from django.contrib.auth import get_user_model

from recipes.models import (
    Recipe, Ingredient, IngredientRecipe, Tag, TagRecipe
)


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source='name')

    class Meta:
        model = Tag
        fields = ('id', 'tag_name')


class IngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient
        fields = ('id', 'ingredient_name')


class RecipeSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(required=False)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'cooking_time', 'ingredients', 'description',
            'pub_date', 'author', 'tags', 
        )
        read_only_fields = ('author',)

    # def create(self, validated_data):
        # if 'tags' not in self.initial_data:
        #     recipe = Recipe.objects.create(**validated_data)
        #     return recipe
        
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     for tag in tags:
    #         current_tag, status = Tag.objects.get_or_create(**tag)
    #         TagRecipe.objects.create(
    #             tag=current_tag, recipe=recipe
    #         )
    #     return recipe


    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe
            )
        return recipe
    


class RecipeListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time','pub_date', 'author', 'tags'
        ) 



class UserSerializer(serializers.ModelSerializer):
    recipes = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'recipes')