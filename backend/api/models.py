from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator


class FoodgramUser(AbstractUser):
    """
    Кастомная модель пользователя с дополнительными полями
    """

    email = models.EmailField(max_length=254, unique=True,
                              verbose_name="Email адрес")
    username = models.CharField(
        verbose_name="Никнейм",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="users/", null=True, blank=True,
        verbose_name="Аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]


class Ingredient(models.Model):
    """
    Модель ингредиентов
    """

    name = models.CharField(max_length=128,
                            verbose_name="Название ингредиента")
    measurement_unit = models.CharField(max_length=64,
                                        verbose_name="Единица измерения")

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """
    Модель рецептов
    """

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    name = models.CharField(max_length=256, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to="recipes/images/", default="",
        verbose_name="Изображение блюда"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления (мин)"
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(fields=["recipe", "ingredient"],
                                    name="unique_recipe_ingredient")
        ]


class Subscription(models.Model):
    """
    Модель подписок пользователей друг на друга
    """

    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name="subscribers",
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_user_author"),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_subscription",
            )
        ]


class UserRecipeBaseModel(models.Model):
    """
    Базовая абстрактная модель для связи пользователя и рецепта.
    """
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_%(class)s"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class Favorite(UserRecipeBaseModel):
    """
    Модель избранных рецептов
    """

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class ShoppingCart(UserRecipeBaseModel):
    """
    Модель списка покупок
    """

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
