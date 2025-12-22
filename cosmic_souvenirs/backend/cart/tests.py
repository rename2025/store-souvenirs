from django.test import TestCase, Client
from django.urls import reverse
from products.models import Category, Product
from django.contrib.auth import get_user_model


class CartTest(TestCase):
    def setUp(self):
        self.client = Client()


        self.cart_url = '/cart/'
        self.add_to_cart_url = '/cart/add/'


        try:
            self.category = Category.objects.create(
                name='Test Category',
                slug='test-category'
            )
        except:
            pass


        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=50.00,
            description='Test description'
        )


        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_cart_page_loads(self):
        """Тест загрузки страницы корзины"""
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Корзина', html=True)