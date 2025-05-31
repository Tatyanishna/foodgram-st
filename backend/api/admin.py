from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import (
    FoodgramUser,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
    Subscription,
)


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    """Кастомизация администрирования пользователей."""

    list_display = (
        "id",
        "username",
        "full_name",
        "email",
        "avatar_display",
        "recipes_count",
        "subscriptions_count",
        "subscribers_count",
        "is_staff",
    )
    search_fields = ("username", "email")

    @admin.display(description="ФИО")
    def full_name(self, user):
        """
        Возвращает ФИО пользователя (имя + фамилия).
        """
        return f"{user.first_name} {user.last_name}".strip()

    @mark_safe
    @admin.display(description="Аватар")
    def avatar_display(self, user):
        """
        Возвращает HTML-разметку для отображения аватара.
        """
        if user.avatar:
            return (
                f'<img src="{user.avatar.url}" '
                f'width="50" height="50" style="border-radius: 50%;" />'
            )
        return "-"

    @admin.display(description="Рецепты")
    def recipes_count(self, user):
        """
        Возвращает количество рецептов пользователя.
        """
        return user.recipes.count()

    @admin.display(description="Подписки")
    def subscriptions_count(self, user):
        """
        Возвращает количество подписок пользователя.
        """
        return user.subscriptions.count()

    @admin.display(description="Подписчики")
    def subscribers_count(self, user):
        """
        Возвращает количество подписчиков пользователя.
        """
        return user.subscribers.count()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""

    list_display = (
        "id",
        "name",
        "author",
        "cooking_time_display",
        "ingredients_display",
        "image_display",
        "get_favorites_count",
        "created_at",
    )
    list_filter = ("author",)
    search_fields = ("author__username", "name")
    readonly_fields = (
        "get_favorites_count", "ingredients_display", "image_display"
    )

    @admin.display(description="Время готовки")
    def cooking_time_display(self, recipe):
        """
        Возвращает время готовки в формате "X мин".
        """
        return f"{recipe.cooking_time} мин"

    @mark_safe
    @admin.display(description="Продукты")
    def ingredients_display(self, recipe):
        """
        Возвращает HTML-разметку для отображения списка продуктов.
        """
        ingredients = (
            recipe.recipe_ingredients.select_related("ingredient").all()
        )
        return "<br>".join(
            f"{ri.ingredient.name} "
            f"({ri.ingredient.measurement_unit}) - {ri.amount}"
            for ri in ingredients
        )

    @mark_safe
    @admin.display(description="Картинка")
    def image_display(self, recipe):
        """
        Возвращает HTML-разметку для отображения картинки.
        """
        if recipe.image:
            return (
                f'<img src="{recipe.image.url}"'
                f'width="100" height="100" style="object-fit: cover;" />'
            )
        return "-"

    @admin.display(description="В избранном")
    def get_favorites_count(self, recipe):
        """Подсчет количества добавлений рецепта в избранное."""
        return recipe.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""

    list_display = ("id", "name", "measurement_unit", "recipe_count")
    list_filter = ("measurement_unit",)
    search_fields = ("name", "measurement_unit")

    @admin.display(description="Рецептов")
    def recipe_count(self, ingredient):
        """
        Возвращает количество рецептов, в которых используется ингредиент.
        """
        return ingredient.recipe_ingredients.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов в рецептах."""

    list_display = ("id", "recipe", "ingredient", "amount")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Администрирование избранных рецептов."""

    list_display = ("id", "user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Администрирование списка покупок."""

    list_display = ("id", "user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Администрирование подписок."""

    list_display = ("id", "user", "author")
    list_filter = ("user", "author")
