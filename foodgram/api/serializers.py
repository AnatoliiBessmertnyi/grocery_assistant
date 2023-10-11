import base64
import re

import django.contrib.auth.password_validation as validators
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, Subscribe, Tag)
from rest_framework import serializers

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор декодирования изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TokenSerializer(serializers.Serializer):
    """Сериализатор токена авторизации."""
    email = serializers.CharField(label='Email', write_only=True)
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label='Токен', read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError(
                    'Ошибка ввода пароля или email.',
                    code='authorization',
                )
        else:
            mess = 'Ошибка.'
            raise serializers.ValidationError(
                mess,
                code='authorization',
            )
        attrs['user'] = user
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра пользователей."""
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.follower.filter(author=obj).exists()
            if user.is_authenticated
            else False
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователей."""
    email = serializers.EmailField(
        max_length=settings.MAX_LENGHT,
        required=True,
    )
    username = serializers.CharField(
        required=True,
        max_length=settings.MAX_LENGHT,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def validate_password(self, password):
        validators.validate_password(password)
        return password

    def validate(self, data):
        username = data['username']
        email = data['email']
        email_exists = User.objects.filter(email=email).exists()
        username_exists = User.objects.filter(username=username).exists()
        if username.lower() == 'me':
            raise serializers.ValidationError(
                f'Имя пользователя "{username}" недоступно.',
            )
        if not re.match(r'^[\w.@+-]+$', username):
            raise serializers.ValidationError('Некорректный формат логина')
        if username_exists and not email_exists:
            raise serializers.ValidationError(
                'Пользователь зарегистрирован с другой почтой'
            )
        if email_exists and not username_exists:
            raise serializers.ValidationError(
                'Пользователь зарегистрирован с другим логином'
            )
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'


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


class RecipeUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей промежуточной модели."""
    is_subscribed = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.follower.filter(author=obj).exists()
            if user.is_authenticated
            else False
        )


class IngredientsEditSerializer(serializers.ModelSerializer):
    """Сериализатор сохранения ингредиентов в рецепте."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания и редактирования рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientsEditSerializer(many=True)
    image = Base64ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = get_object_or_404(Ingredient, id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент не должен повторяться!'
                )
            ingredient_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError('Минимум 1 тэг!')
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга "{tag_name}" не существует!'
                )
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""
    ingredients = RecipeIngredientSerializer(
        source='recipe',
        many=True,
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    author = RecipeUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки промежуточной модели."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = self.instance
        user = self.context['request'].user
        if user.favorite_recipe.recipe.filter(id=recipe.id).exists():
            raise serializers.ValidationError(
                "Этот рецепт уже находится в вашем избранном.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        favorite_recipe, created = FavoriteRecipe.objects.get_or_create(
            user=user)
        favorite_recipe.recipe.add(self.instance)
        return self.instance


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на автора."""
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all()
        )
        return SubscribeRecipeSerializer(
            recipes,
            many=True
        ).data

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        author = data['author']
        if user.id == author.id:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError('Вы уже подписаны!')
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = validated_data['author']
        subscription, created = Subscribe.objects.get_or_create(
            user=user, author=author)
        return subscription
