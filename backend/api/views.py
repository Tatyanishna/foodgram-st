from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .filters import RecipeFilter
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    FoodgramUser,
)
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeMinifiedSerializer,
    UserWithRecipesSerializer,
    FoodgramUserSerializer,
    UserAvatarSerializer,
)
from .services import (
    generate_shopping_list,
    get_shopping_cart_ingredients
)


class FoodgramUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = PageLimitPagination
    permission_classes = [AllowAny]

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        return super().me(request)

    @action(
        detail=True, methods=["put", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request, id):
        """
        Обработка аватара пользователя:
        - PUT: добавление/обновление аватара
        - DELETE: удаление аватара
        """
        user = request.user

        if request.method == "PUT":
            user = request.user
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid() and "avatar" in request.data:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            raise ValidationError(detail=serializer.errors)

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError(detail="У пользователя нет аватара.")

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticatedOrReadOnly])
    def subscriptions(self, request):
        """
        Получение списка подписок текущего пользователя.
        """
        user = request.user
        authors = [subscription.author
                   for subscription in user.subscriptions.all()]

        # Пагинация
        return self.get_paginated_response(
            UserWithRecipesSerializer(
                self.paginate_queryset(authors),
                many=True, context={"request": request}
            ).data
        )

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = self.get_object()
        if request.method == "POST":
            if request.user == author:
                raise ValidationError(
                    detail="Нельзя подписаться на самого себя."
                )
            _, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                raise ValidationError(
                    detail="Вы уже подписаны на этого пользователя."
                )
            serializer = UserWithRecipesSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Subscription, user=request.user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = PageLimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        return (
            RecipeWriteSerializer
            if self.action in ["create", "update", "partial_update"]
            else RecipeReadSerializer
        )

    @staticmethod
    def _handle_recipe_action(model, user, recipe, request_method):
        """
        Обрабатывает добавление или удаление рецепта в избранное/корзину.
        :param model: Модель (Favorite или ShoppingCart).
        :param user: Пользователь.
        :param recipe: Рецепт.
        :param request_method: Действие ("POST" или "DELETE").
        :return: Response с данными или ошибкой.
        """
        if request_method == "POST":
            _, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                raise ValidationError(detail=(
                    f"Рецепт '{recipe.name}' уже добавлен в избранное/корзину."
                ))

            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request_method == "DELETE":
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise ValidationError(detail="Некорректное действие.")

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """
        Обрабатывает добавление/удаление рецепта в избранное.
        """
        recipe = self.get_object()
        return self._handle_recipe_action(
            Favorite, request.user, recipe, request.method)

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """
        Обрабатывает добавление/удаление рецепта в корзину.
        """
        recipe = self.get_object()
        return self._handle_recipe_action(
            ShoppingCart, request.user, recipe, request.method)

    @action(detail=False, permission_classes=[IsAuthenticatedOrReadOnly])
    def download_shopping_cart(self, request):
        ingredients = get_shopping_cart_ingredients(request.user)

        recipes = (
            Recipe.objects.filter(shoppingcarts__user=request.user).distinct()
        )

        shopping_list = generate_shopping_list(ingredients, recipes)

        return FileResponse(shopping_list,
                            content_type="text/plain; charset=utf-8",
                            filename="shopping_list.txt")


@api_view(["GET"])
def get_recipe_short_link(request, id):
    """
    Создает и возвращает короткую ссылку на рецепт.
    """
    # Предварительная валидация: проверяем, что id является ключом рецепта
    get_object_or_404(Recipe, id=id)

    return Response(
        {
            "short-link": request.build_absolute_uri(
                reverse("redirect_short_link", kwargs={"short_id": id})
            )
        },
        status=status.HTTP_200_OK,
    )


def redirect_short_link(request, short_id):
    """
    Перенаправляет с короткой ссылки на страницу рецепта.
    """
    get_object_or_404(Recipe, id=short_id)
    return redirect(f"recipes/{short_id}")


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        name = self.request.GET.get("name")
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset
