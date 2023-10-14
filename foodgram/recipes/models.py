from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Название',
    )
    text = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    image = models.ImageField('Картинка', upload_to='images/')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            validators.MinValueValidator(
                1,
                message='Мин. время приготовления 1 минута',
            ),
        ],
    )
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ['-pub_date', 'name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов рецепта."""
    name = models.CharField(
        max_length=settings.MAX_LENGHT,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGHT,
        unique=True,
        null=True,
        db_index=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов рецепта."""
    name = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи между рецептом и ингредиентом."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество ингредиентов',
        validators=[
            validators.MinValueValidator(
                1,
                message='Мин. количество ингредиентов 1',
            ),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ['recipe__name']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_recipe',
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['recipe', 'user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзины."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['recipe', 'user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_in_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
