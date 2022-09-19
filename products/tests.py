import datetime
import json
from decimal import Decimal

from django.test import TestCase, RequestFactory
from http import HTTPStatus

from rest_framework.test import APIClient

from .views import CategoryViewSet
from .models import Category, Product, ProductHistory


class CategoryTestCase(TestCase):

    def setUp(self) -> None:
        Category.objects.create(name="Phone")
        Category.objects.create(name="Laptop")

    def test_slug_creation(self):
        phone = Category.objects.get(name="Phone")
        laptop = Category.objects.get(name="Laptop")
        self.assertEqual(phone.slug, 'phone')
        self.assertEqual(laptop.slug, 'laptop')


class ProductTestCase(TestCase):

    def setUp(self) -> None:
        self.category = Category.objects.create(name="Phone")
        Product.objects.create(
            title='product 1',
            sku='123',
            description='desc',
            market_price=123.00,
            category=self.category
        )

    def test_create_product(self):
        product = Product.objects.get(pk=1)
        self.assertEqual(product.current_price, Decimal(123.00))

    def test_change_price(self):
        product = Product.objects.get(pk=1)
        product.change_price(450, datetime.date(2022, 9, 1), datetime.date(2022, 9, 15))
        self.assertEqual(product.current_price, 450.00)
        self.assertEqual(product.start_date, datetime.date(2022, 9, 1))
        self.assertEqual(product.end_date, datetime.date(2022, 9, 15))

    def test_log_history(self):
        product = Product.objects.get(pk=1)
        product.change_price(450, datetime.date(2022, 9, 1), datetime.date(2022, 9, 15))
        product_history = ProductHistory.objects.filter(product=product).first()
        self.assertEqual(product_history.product, product)
        self.assertEqual(product_history.start_date, datetime.date(2022, 9, 1))
        self.assertEqual(product_history.end_date, datetime.date(2022, 9, 15))
        self.assertEqual(product_history.price, 450.00)


class CategoryViewSetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        category_1 = Category.objects.create(name="Phone")
        category_2 = Category.objects.create(name="Laptop")
        Product.objects.create(
            title='product 1',
            sku='777',
            description='desc',
            market_price=100.00,
            category=category_1
        )
        Product.objects.create(
            title='product 2',
            sku='666',
            description='desc',
            market_price=1000.00,
            category=category_2
        )
        Product.objects.create(
            title='product 3',
            sku='333',
            description='desc',
            market_price=2500.00,
            category=category_2
        )

    def test_category_view_set(self):
        request = self.factory.get('/category')
        response = CategoryViewSet.as_view({'get': 'list'})(request)
        # Check if the first dog's name is Balto, like it is in the fixtures:
        self.assertEqual(response.data['results'][0]['name'], 'Phone')
        self.assertEqual(response.data['results'][1]['name'], 'Laptop')
        # Check if you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_category_create(self):
        data = json.dumps({
            "name": "TV",
        })
        client = APIClient()
        response = client.post('/category/', data=data, content_type='application/json')
        self.assertEqual(response.data['name'], 'TV')
        self.assertEqual(response.data['slug'], 'tv')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_category_change_price(self):
        data = json.dumps({"price": 123})
        client = APIClient()
        response = client.post('/category/laptop/change_price/', data=data, content_type='application/json')
        product_1 = Product.objects.get(title='product 2')
        product_2 = Product.objects.get(title='product 3')
        self.assertEqual(product_1.market_price, 123)
        self.assertEqual(product_2.market_price, 123)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class ProductViewSetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        category_1 = Category.objects.create(name="Phone")
        category_2 = Category.objects.create(name="Laptop")
        Product.objects.create(
            title='product 1',
            sku='123',
            description='desc',
            market_price=100.00,
            category=category_1
        )
        Product.objects.create(
            title='product 2',
            sku='456',
            description='desc',
            market_price=1000.00,
            category=category_2
        )
        Product.objects.create(
            title='product 3',
            sku='789',
            description='desc',
            market_price=2500.00,
            category=category_2
        )

    def test_product_add_price(self):
        data = json.dumps({
            "current_price": 123,
            "start_date": "2022-09-01",
            "end_date": '2022-09-15'
        })
        client = APIClient()
        response = client.post('/product/2/add_price/', data=data, content_type='application/json')
        product = Product.objects.get(pk=2)

        self.assertEqual(product.current_price, 123)
        self.assertEqual(product.start_date, datetime.date(2022, 9, 1))
        self.assertEqual(product.end_date, datetime.date(2022, 9, 15))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PriceCalculationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        category_1 = Category.objects.create(name="Phone")
        category_2 = Category.objects.create(name="Laptop")
        Product.objects.create(
            title='product 1',
            sku='123',
            description='desc',
            market_price=100.00,
            category=category_1,
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 9, 3)

        )
        Product.objects.create(
            title='product 2',
            sku='456',
            description='desc',
            market_price=200.00,
            category=category_2,
            start_date=datetime.date(2022, 9, 7),
            end_date=datetime.date(2022, 9, 10)
        )
        Product.objects.create(
            title='product 3',
            sku='789',
            description='desc',
            market_price=300.00,
            category=category_2,
            start_date=datetime.date(2022, 9, 1),
            end_date=datetime.date(2022, 9, 30)
        )

    def test_price_calculation(self):
        data = json.dumps({
                "category_id": 2,
                "start_date": "2022-09-01",
                "end_date": '2022-09-30'
        })
        client = APIClient()
        response = client.post('/calculate_price/', data=data, content_type='application/json')

        self.assertEqual(response.data["overall_avg_price"], 250)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_price_calculation_with_changed_values(self):
        data = json.dumps({
            "current_price": 400,
            "start_date": "2022-09-01",
            "end_date": '2022-09-15'
        })
        client = APIClient()
        client.post('/product/2/add_price/', data=data, content_type='application/json')
        data = json.dumps({
            "current_price": 600,
            "start_date": "2022-09-09",
            "end_date": '2022-09-23'
        })
        client = APIClient()
        client.post('/product/3/add_price/', data=data, content_type='application/json')
        data = json.dumps({
            "current_price": 1100,
            "start_date": "2022-09-09",
            "end_date": '2022-09-23'
        })
        client = APIClient()
        client.post('/product/3/add_price/', data=data, content_type='application/json')

        data = json.dumps({
            "category_id": 2,
            "start_date": "2022-09-01",
            "end_date": '2022-09-30'
        })
        client = APIClient()
        response = client.post('/calculate_price/', data=data, content_type='application/json')

        # ProductHistory prices (400, 600, 1100) and current prices (1100, 400)
        self.assertEqual(response.data["overall_avg_price"], 725.00)
        self.assertEqual(response.status_code, HTTPStatus.OK)
