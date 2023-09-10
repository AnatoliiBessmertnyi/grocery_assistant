from rest_framework import serializers

from .models import Recipe, Owner


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time', 'ingredient', 'description',
            'pub_date', 'owner'
        ) 


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'recipes')
