from django_filters import rest_framework as filters
from .models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для модели Recipe с расширенными возможностями фильтрации.
    """

    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited", label="Is favorited"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart", label="Is in shopping cart"
    )
    author = filters.NumberFilter(field_name="author__id", label="Author ID")

    class Meta:
        model = Recipe
        fields = ["is_favorited", "is_in_shopping_cart", "author"]

    def filter_is_favorited(self, recipes, name, value):
        """
        Фильтр для избранных рецептов.

        :param recipes: Исходный набор рецептов
        :param name: Имя поля
        :param value: Значение фильтра (True/False)
        :return: Отфильтрованный набор рецептов
        """
        user = self.request.user
        if value and user.is_authenticated:
            return recipes.filter(favorites__user=user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        """
        Фильтр для рецептов в списке покупок.

        :param recipes: Исходный набор рецептов
        :param name: Имя поля
        :param value: Значение фильтра (True/False)
        :return: Отфильтрованный набор рецептов
        """
        user = self.request.user
        if value and user.is_authenticated:
            return recipes.filter(shoppingcarts__user=user)
        return recipes
