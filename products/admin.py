from django.contrib import admin
from .models import Category, Product, ProductHistory


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(ProductHistory)
