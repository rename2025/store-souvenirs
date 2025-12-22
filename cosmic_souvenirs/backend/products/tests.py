from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Product


class ProductsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.catalog_url = '/catalog/'


        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            description='Test Description'
        )

    def test_catalog_page_loads(self):
        """Тест загрузки страницы каталога"""
        response = self.client.get(self.catalog_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Каталог', html=True)

    def test_product_detail_page(self):
        """Тест страницы деталей продукта"""
        url = f'/product/{self.product.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product', html=True)