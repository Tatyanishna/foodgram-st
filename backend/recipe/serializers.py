from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from users.serializers import UserSerializer
from django.core.validators import MinValueValidator

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            'short_link',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        write_only=True,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'At least one ingredient is required'
            })

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ingredients must be unique'
            })

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'At least one tag is required'
            })

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Tags must be unique'
            })

        cooking_time = data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Cooking time must be at least 1 minute'
            })

        return data

    @transaction.atomic
    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Recipe is already in favorites'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Recipe is already in shopping cart'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data