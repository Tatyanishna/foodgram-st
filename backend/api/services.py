from django.db.models import Sum
from django.utils.timezone import now

from .models import RecipeIngredient


def get_shopping_cart_ingredients(user):
    """
    Получение списка ингредиентов из корзины пользователя.
    """
    return (
        RecipeIngredient.objects.filter(recipe__shoppingcarts__user=user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(total_amount=Sum("amount"))
        .order_by("ingredient__name")
    )


def generate_shopping_list(ingredients, recipes):
    """
    Генерирует текстовый файл со списком покупок.

    Args:
        ingredients (QuerySet): QuerySet с ингредиентами, содержащий поля:
            - ingredient__name: Название ингредиента
            - ingredient__measurement_unit: Единица измерения
            - total_amount: Общее количество ингредиента
        recipes (QuerySet): QuerySet с рецептами, содержащий поля:
            - name: Название рецепта
            - author__username: Имя автора рецепта

    Returns:
        str: Текст списка покупок
    """
    products = [
        f"{idx}. {item['ingredient__name'].capitalize()} "
        f"({item['ingredient__measurement_unit']}) - {item['total_amount']}"
        for idx, item in enumerate(ingredients, 1)
    ]

    recipes_list = [
        f"{idx}. {recipe['name']} (автор: {recipe['author__username']})"
        for idx, recipe in enumerate(recipes, 1)
    ]

    return "\n".join(
        [
            (
                f"Список покупок\n"
                f"Дата составления: {now().strftime('%d.%m.%Y %H:%M')}\n"
            ),
            "\nПродукты:\n",
            *products,
            "\nРецепты:\n",
            *recipes_list,
        ]
    )
