from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        max_length=50,
        unique=True
    )
    # color = models.CharField(
    #     'Название цвета',
    #     max_length=20,
    #     unique=True
    # )
    # slug = models.SlugField(
    #     'Идентификатор тэга',
    #     max_length=50,
    #     unique=True
    # )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта',
    )
    tags = models.TextField()
    # tags = models.ManyToManyField(
    #     Tag,
    #     related_name='recipes',
    #     blank=True,
    #     verbose_name='Тэги',
    # )

    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    cooking_time = models.IntegerField(blank=True, null=True)
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    description = models.TextField(
        max_length=500,
        verbose_name='Описание',
    )
    image = models.ImageField(
        upload_to='recipes/', null=True, blank=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


# class TagRecipe(models.Model):
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

#     def __str__(self):
#         return f'{self.tag} {self.recipe}'

class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

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
