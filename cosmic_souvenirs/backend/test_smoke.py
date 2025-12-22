"""
Упрощенные smoke-тесты для проверки работы приложения
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


class SmokeTests(TestCase):
    """Простые тесты для проверки что страницы загружаются"""

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        """Тест главной страницы"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✅ Главная страница работает")

    def test_catalog_page(self):
        """Тест каталога"""
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)
        print("✅ Страница каталога работает")

    def test_contacts_page(self):
        """Тест контактов"""
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)
        print("✅ Страница контактов работает")

    def test_login_page(self):
        """Тест страницы входа"""
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)
        print("✅ Страница входа работает")

    def test_register_page(self):
        """Тест страницы регистрации"""
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        print("✅ Страница регистрации работает")

    def test_cart_page(self):
        """Тест корзины"""
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        print("✅ Страница корзины работает")

    def test_create_user(self):
        """Тест создания пользователя"""
        User = get_user_model()
        user = User.objects.create_user(
            username='smoketest',
            email='smoke@test.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'smoketest')
        print("✅ Создание пользователя работает")