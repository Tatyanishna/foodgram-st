from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'tag name',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'color in HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'ingredient name',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'measurement unit',
        max_length=200,
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='author'
    )
    name = models.CharField(
        'recipe name',
        max_length=200,
    )
    image = models.ImageField(
        'image',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'description',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'cooking time',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        'publication date',
        auto_now_add=True,
    )
    slug = models.SlugField(
        'slug',
        max_length=200,
        unique=True,
        blank=True,
    )
    short_link = models.CharField(
        'short link',
        max_length=8,
        unique=True,
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.short_link:
            self.short_link = get_random_string(8)
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'amount',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'recipe ingredient'
        verbose_name_plural = 'recipe ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe} to favorites'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe} to shopping cart'