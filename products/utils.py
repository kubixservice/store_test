from django.db.models import Avg

from .models import Category, Product, ProductHistory


def calculate_avg_price(category_id, start_date, end_date) -> dict:
    category = Category.objects.get(pk=category_id)

    products = Product.objects.filter(
        category=category,
        start_date__range=(start_date, end_date),
        end_date__range=(start_date, end_date)
    ).aggregate(Avg('current_price'))

    product_history = ProductHistory.objects.select_related().filter(
        product__category=category,
        start_date__range=(start_date, end_date),
        end_date__range=(start_date, end_date)
    ).aggregate(Avg('price'))

    divider = 2
    if not products['current_price__avg']:
        products['current_price__avg'] = 0
        divider = 1
    if not product_history['price__avg']:
        product_history['price__avg'] = 0
        divider = 1

    avg_price = (float(products['current_price__avg']) + float(product_history['price__avg'])) / divider

    return {
        "category_id": category.id,
        "category_name": category.name,
        "current_avg_price": round(float(products['current_price__avg']), 2),
        "history_avg_price": round(float(product_history['price__avg']), 2),
        "overall_avg_price": round(avg_price, 2)

    }


def change_category_price(category, price):
    product = Product.objects.filter(category=category)
    for product in product:
        product.market_price = price
        product.save()
