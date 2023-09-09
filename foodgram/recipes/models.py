from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название рецепта",
        )
    # tag = models.ForeignKey(
    #     Tag, on_delete=models.SET_NULL,
    #     related_name='recipes', blank=True, null=True
    # )
    cooking_time = models.IntegerField(blank=True, null=True)
    # author = models.ForeignKey(
    #     User, on_delete=models.CASCADE, related_name='recipes'
    # )
    ingredient = models.CharField(
        max_length=256,
        verbose_name="Название ингредиента",
        )
    description = models.TextField(
        max_length=500,
        verbose_name="Описание",
        )
    # image = models.ImageField(
    #     upload_to='recipes/', null=True, blank=True
    # )


    def __str__(self):
        return self.name
    

