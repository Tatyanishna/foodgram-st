from django.core.management.base import BaseCommand
from django.db import transaction
import json
import os
from api.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из файла"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.load_ingredients("ingredients.json")

        self.stdout.write(
            self.style.SUCCESS("Начальные данные успешно загружены"))

    def load_ingredients(self, *args):
        json_file_path = args[0]

        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                ingredients_list = Ingredient.objects.bulk_create([
                    Ingredient(**ingredient_info)
                    for ingredient_info in json.load(file)
                ], ignore_conflicts=True)

                self.stdout.write(self.style.SUCCESS(
                    f"Successfully loaded "
                    f"{len(ingredients_list)} ingredients. "
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"An error occurred with file "
                f"{os.getcwd()}/{json_file_path}: {e}"
            ))
