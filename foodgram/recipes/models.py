from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        max_length=50,
        unique=True
    )
    color = models.CharField(
        'Название цвета',
        max_length=20,
        unique=True
    )
    slug = models.SlugField(
        'Идентификатор тэга',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=50
    )
    measure = models.CharField(
        'Единица измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта',
    )
    # tags = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=True,
        verbose_name='Тэги',
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    cooking_time = models.IntegerField(
        'Время приготовления рецепта'
    )
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        upload_to='recipes/', null=True, blank=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe'
    )
    amount = models.IntegerField(
        'Количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']


class FavoriteRecipe(models.Model):
    pass


class ShoppingCart(models.Model):
    pass
