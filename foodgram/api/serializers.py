import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = '__all__'


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return Subscription.objects.filter(
            author=obj, subscriber=current_user).exists()


class SubscriptionSerializer(UserSerializer):
    """Сериализатор подписок."""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeListSerializer(recipes, many=True).data
    
    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        author = data['author']
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        if Subscription.objects.filter(
            author=author, subscriber=user).exists():
            raise serializers.ValidationError('Вы уже подписаны!')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов промежуточной модели."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    """Сериализатор декодирования изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(use_url=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def validate(self, data):
        for field in ('tags', 'ingredients', 'name', 'text', 'cooking_time'):
            if not self.initial_data.get(field):
                raise serializers.ValidationError(
                    f'Поле не заполнено')
        ingredients = self.initial_data['ingredients']
        ingredients_ids = set()
        for ingredient in ingredients:
            if not ingredient.get('amount') or not ingredient.get('id'):
                raise serializers.ValidationError(
                    'Пожалуйста, заполните поля "ингредиенты" правильно.')
            if not int(ingredient['amount']) > 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше нуля.')
            if ingredient['id'] in ingredients_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            ingredients_ids.add(ingredient['id'])
        request = self.context['request']
        if request.method == 'POST' and (Favorite.objects.filter(
            recipe=self.instance, user=request.user).exists() or
            ShoppingCart.objects.filter(
                recipe=self.instance, user=request.user).exists()):
            raise serializers.ValidationError('Рецепт уже добавлен.')
        return data

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, user=current_user).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj, user=current_user).exists()

    def get_recipe_ingredient(self, recipe, ingredients):
        obj = (RecipeIngredient(
            recipe=recipe, ingredient_id=ing['id'], amount=ing['amount']
        ) for ing in ingredients)
        RecipeIngredient.objects.bulk_create(obj)

    def create(self, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.get_recipe_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        request = self.context['request']
        if request.method == 'DELETE' and not Favorite.objects.filter(
            recipe=instance, user=request.user).exists():
            raise serializers.ValidationError('Рецепт не найден в избранном.')
        ingredients = self.initial_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        self.get_recipe_ingredient(instance, ingredients)
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()
        return instance
