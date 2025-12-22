from django.test import TestCase, Client
from django.urls import reverse


class MainPagesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        """Тест загрузки главной страницы"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'cosmic_souvenirs/index.html')
        self.assertContains(response, 'Cosmic Souvenirs', html=True)

    def test_contacts_page_loads(self):
        """Тест загрузки страницы контактов"""
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'pages/contacts.html')
        self.assertContains(response, 'Контакты', html=True)

    def test_404_page(self):
        """Тест несуществующей страницы"""
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)

    def test_static_files_served(self):
        """Тест что статические файлы доступны"""

        pass

