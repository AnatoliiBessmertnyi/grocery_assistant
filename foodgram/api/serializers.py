import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import (
    Recipe, Ingredient, IngredientRecipe, Tag, TagRecipe, User
)


class UserSerializer(serializers.ModelSerializer):
    recipes = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'recipes')
        ref_name = 'ReadOnlyUsers'


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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(required=False)
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'cooking_time', 'ingredients', 'description',
            'pub_date', 'author', 'tags', 'image'
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
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            lst = []
            for ingredient in ingredients_data:
                current_ingredient, status = ingredient.objects.get_or_create(
                    **ingredient
                    )
                lst.append(current_ingredient)
            instance.ingredients.set(lst)

        instance.save()
        return instance
    


class RecipeListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time','pub_date', 'author', 'tags'
        ) 


