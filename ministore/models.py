from django.db import models

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)  # Tên danh mục (Mobile, Watch)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Liên kết với danh mục
    title = models.CharField(max_length=200)  # Tên SP (Iphone 13)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá (1500.00)
    image = models.ImageField(upload_to='products/')  # Ảnh sản phẩm
    description = models.TextField(blank=True)  # Mô tả

    def __str__(self):
        return self.title