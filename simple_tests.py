from django.test import TestCase, Client
from django.contrib.auth.models import User


class SimpleSmokeTests(TestCase):
    """Простые smoke-тесты для проверки работы страниц"""

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✓ Главная страница работает")

    def test_catalog_page(self):
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)
        print("✓ Страница каталога работает")

    def test_contacts_page(self):
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)
        print("✓ Страница контактов работает")

    def test_login_page(self):
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)
        print("✓ Страница логина работает")

    def test_register_page(self):
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        print("✓ Страница регистрации работает")

    def test_cart_page(self):
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        print("✓ Страница корзины работает")

    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        print("✓ Создание пользователя работает")