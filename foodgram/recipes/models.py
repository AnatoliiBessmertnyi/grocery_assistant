from django.db import models
from django.conf import settings


class Tag(models.Model):
    '''Модель тегов рецепта.'''
    name = models.CharField(
        'Название тэга',
        max_length=50,
        unique=True
    )
    color = models.CharField(
        'Название цвета',
        max_length=7,
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
    '''Модель ингредиентов рецепта.'''
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
        return {self.name}


class Recipe(models.Model):
    '''Модель рецепта.'''
    name = models.CharField(
        'Название рецепта',
        max_length=256,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
    )
    cooking_time = models.IntegerField(
        'Время приготовления рецепта в минутах',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    description = models.TextField(
        'Описание рецпта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    '''Промежуточная модель для связи между рецептом и ингредиентом.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    amount = models.IntegerField(
        'Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Follow(models.Model):
    '''Модель подписок на автора.'''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']

    def __str__(self):
        return f'{self.user} {self.following}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoriter',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriting',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='buying',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'
