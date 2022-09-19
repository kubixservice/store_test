from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ChangeCategoryPriceSerializer(serializers.Serializer): # noqa
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class AddPriceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['current_price', 'start_date', 'end_date']

    def update(self, instance, validated_data):
        instance.change_price(**validated_data)
        return instance


class PriceCalculaterSerializerForm(serializers.Serializer): # noqa
    category_id = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
