from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    AddPriceProductSerializer,
    PriceCalculaterSerializerForm,
    ChangeCategoryPriceSerializer
)
from .utils import calculate_avg_price, change_category_price


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['POST'], name='Change price')
    def change_price(self, request, slug=None, *args, **kwargs):
        category = Category.objects.get(slug=slug)
        serializer = ChangeCategoryPriceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        change_category_price(category, request.data["price"])
        return Response({"Success": f"Market price changed to {request.data['price']} for category '{category.name}'"})

    def get_serializer_class(self):
        if self.action == 'change_price':
            return ChangeCategoryPriceSerializer
        return CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['POST'], name='Add Price')
    def add_price(self, request, pk=None, *args, **kwargs):
        product = Product.objects.get(pk=pk)
        serializer = AddPriceProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'add_price':
            return AddPriceProductSerializer
        return ProductSerializer


class PriceCalculationView(GenericAPIView):
    serializer_class = PriceCalculaterSerializerForm

    def post(self, request, *args, **kwargs):
        serializer = PriceCalculaterSerializerForm(data=request.data)
        serializer.is_valid()
        data = calculate_avg_price(**serializer.data)
        return Response(data)
