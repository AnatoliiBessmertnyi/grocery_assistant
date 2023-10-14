from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Название',
    )
    text = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    image = models.ImageField('Фото', upload_to='images/')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(
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
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created', 'name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега для рецептов."""
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
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента для рецептов."""
    name = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'

    def get_absolute_url(self):
        return reverse('ingredient-detail', args=self.pk)


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1, message='Количество должно быть больше нуля.')]
    )

    class Meta:
        ordering = ['recipe__name']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredient_recipe')
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    """Модель для связи избранного рецепта и пользователя."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_favorite_recipe')
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель связывает пользователя и добавленные в корзину рецепты."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Рецепт из списка покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe_in_cart')
        ]

    def __str__(self):
        return f'{self.user}: {self.recipe}'
