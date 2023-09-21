import base64
import re

from django.core.files.base import ContentFile
from recipes.models import (
    FavoriteRecipe,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagRecipe,
)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser as User


class Base64ImageField(serializers.ImageField):
    '''Сериализатор декодирования изображений.'''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор тэгов.'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов.'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientEditSerializer(serializers.ModelSerializer):
    '''Сериализатор сохранения ингредиентов в рецепте.'''
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount',
        )


class RecipeIngredientsListSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов промежуточной модели.'''
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measure = serializers.ReadOnlyField(
        source='ingredient.measure'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measure',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор создания и редактирования рецептов.'''
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientEditSerializer(
        many=True,
    )
    image = Base64ImageField(
        required=False,
        allow_null=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        for tag in tags:
            TagRecipe.objects.create(
                recipe=recipe,
                tag=tag.get('id'),
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.description = validated_data.get('description')
        instance.cooking_time = validated_data.get('cooking_time')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            },
        ).data


class RecipeListSerializer(serializers.ModelSerializer):
    '''Сериализатор списка рецептов.'''
    ingredients = RecipeIngredientsListSerializer(
        source='recipe',
        many=True,
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited_recipe = serializers.SerializerMethodField()
    is_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited_recipe(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and bool(obj.favoriting.filter(user=user))

    def get_is_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and bool(obj.buying.filter(user=user))


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор подписки на автора.'''
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError('Нельзя подписываться на себя!')
        return data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор добавления рецепта в избранное.'''

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт Вы уже добавили в список избранных.',
            )
        ]


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    '''Сериализатор рецептов в избранном и в корзине одновременно.'''

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time',
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт Вы уже добавили в список покупок.',
            )
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
    )

    class Meta:
        model = User
        fields = ('username', 'email')

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
                'Пользователь заренистрирован с другой почтой'
            )
        if email_exists and not username_exists:
            raise serializers.ValidationError(
                'Пользователь заренистрирован с другим логином'
            )
        return data


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
        )
