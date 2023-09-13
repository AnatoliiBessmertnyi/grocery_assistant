from rest_framework import serializers

from .models import Recipe, Owner, Ingredient, IngredientRecipe, Tag, TagRecipe


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
    publication_date = serializers.DateTimeField(
        source='pub_date', read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'name', 'cooking_time', 'ingredients', 'description',
            'publication_date', 'owner', 'tags', 
        ) 

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
    publication_date = serializers.DateTimeField(
        source='pub_date', read_only=True
    )
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time','publication_date', 'owner', 'tags'
        ) 



class OwnerSerializer(serializers.ModelSerializer):
    recipes = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'recipes')
