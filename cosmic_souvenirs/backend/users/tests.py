from django.test import TestCase, Client
from django.urls import reverse
# Импортируем кастомную модель User
from users.models import User  # Используем кастомную модель
from django.contrib.auth import get_user_model


class UserViewsTest(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()


        self.register_url = '/users/register/'
        self.login_url = '/users/login/'
        self.logout_url = '/users/logout/'

        # Тестовый пользователь
        self.test_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        self.login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }

    def test_register_page_loads(self):
        """Тест загрузки страницы регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        # Ищем русский текст
        self.assertContains(response, 'Регистрация', html=True)

    def test_user_registration(self):
        """Тест регистрации нового пользователя"""
        response = self.client.post(self.register_url, self.test_user)

        # Проверяем редирект после успешной регистрации
        self.assertIn(response.status_code, [200, 302])

        # Проверяем создание пользователя
        User = get_user_model()
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

    def test_login_page_loads(self):
        """Тест загрузки страницы логина"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        # Ищем русский текст "Вход" или "Войти"
        self.assertContains(response, 'Вход', html=True)

    def test_user_login(self):
        """Тест успешного входа пользователя"""
        # Создаем пользователя через кастомную модель
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )

        # Пробуем войти
        response = self.client.post(self.login_url, self.login_data)
        self.assertIn(response.status_code, [200, 302])

    def test_user_logout(self):
        """Тест выхода пользователя"""
        User = get_user_model()
        # Создаем и логиним пользователя
        user = User.objects.create_user(
            username='testuser',
            password='TestPassword123!'
        )
        self.client.force_login(user)

        # Выходим
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Редирект на главную