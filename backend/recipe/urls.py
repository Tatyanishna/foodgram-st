from django.urls import path
from rest_framework.routers import DefaultRouter
from recipe.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipe', RecipeViewSet, basename='recipe')

urlpatterns = [
    path(
        'recipe/download_shopping_cart/',
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name='download_shopping_cart'
    ),
] + router.urls