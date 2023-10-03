from django.db import models
from django.conf import settings


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
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGHT,
        unique=True,
        verbose_name='Идентификатор',
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
    measure = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Единица измерения',
        
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=settings.MAX_LENGHT,
        verbose_name='Название',

    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэг',

    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиент',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления рецепта в минутах',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
        verbose_name='Картинка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Промежуточная модель для связи между рецептом и ингредиентом."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class TagRecipe(models.Model):
    """Промежуточная модель для связи между тэгом и рецептом."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тэг и рецепт'
        verbose_name_plural = 'Тэги и рецепты'

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Follow(models.Model):
    """Модель подписок на автора."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']

    def __str__(self):
        return f'{self.user} {self.following}'


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoriter',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriting',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='buying',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'
