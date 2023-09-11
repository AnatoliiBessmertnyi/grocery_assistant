from rest_framework import serializers

from .models import Recipe, Owner


class RecipeSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time', 'ingredient', 'description',
            'pub_date', 'owner', 'tag'
        ) 


class OwnerSerializer(serializers.ModelSerializer):
    recipes = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'recipes')
