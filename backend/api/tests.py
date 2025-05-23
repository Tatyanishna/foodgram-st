from django.test import TestCase, Client
from http import HTTPStatus
from . import models


class FoodgramAPITestCase(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_recipes_exists(self):
        """Проверка доступности списка рецептов"""
        response = self.guest_client.get("/api/recipes/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_custom_user_creation(self):
        """Проверка создания нового пользователя"""
        data = {
            "email": "vpupkan@yindex.ru",
            "username": "vasya.pupkan",
            "first_name": "Вася",
            "last_name": "Иванов",
            "password": "Qgrfedmskig4563e5",
        }
        response = self.guest_client.post("/api/users/", data=data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            models.FoodgramUser.objects.filter(
                email="vpupkan@yindex.ru"
            ).exists()
        )
