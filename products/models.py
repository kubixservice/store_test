from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.slug

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):

    title = models.CharField(max_length=120)
    sku = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title

    def change_price(self, current_price, start_date, end_date):
        self.current_price = current_price
        self.start_date = start_date
        self.end_date = end_date
        self.save()

    def log_history(self):
        ProductHistory.objects.create(
            product=self,
            start_date=self.start_date,
            end_date=self.end_date,
            price=self.current_price
        )

    def save(self, *args, **kwargs):
        if not self.current_price:
            self.current_price = self.market_price
        super().save(*args, **kwargs)


class ProductHistory(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    crated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Product({self.product.id}) {self.start_date} - {self.end_date} price: {self.price}'


@receiver(post_save, sender=Product)
def on_change(sender, instance: Product, created, **kwargs):
    if not created:
        instance.log_history()
