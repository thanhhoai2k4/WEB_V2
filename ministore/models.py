from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# --- 1. CATEGORY (DANH MỤC) ---
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL thân thiện (SEO)")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name="Danh mục cha")

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --- 2. PRODUCT (SẢN PHẨM) ---
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name="Mô tả chi tiết", blank=True)

    # Giá tiền: Luôn dùng DecimalField để tránh lỗi làm tròn số học
    base_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá gốc")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     verbose_name="Giá khuyến mãi")

    image = models.ImageField(upload_to='products/', verbose_name="Ảnh đại diện")

    # --- ĐIỂM NHẤN CHO DÂN CÔNG NGHỆ ---
    # Lưu thông số kỹ thuật động dạng JSON.
    # Ví dụ: {"RAM": "8GB", "Chip": "M1", "SSD": "256GB"}
    specifications = models.JSONField(default=dict, blank=True, verbose_name="Thông số kỹ thuật")

    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def price(self):
        """Trả về giá bán thực tế (ưu tiên giá sale) để hiển thị"""
        return self.sale_price if self.sale_price else self.base_price


# --- 3. GALLERY (BỘ SƯU TẬP ẢNH) ---
# Hàng điện tử cần xem nhiều góc độ, 1 ảnh là không đủ.
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Ảnh của {self.product.name}"


# --- 4. ORDER (ĐƠN HÀNG) ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xử lý'),
        ('SHIPPING', 'Đang giao'),
        ('COMPLETED', 'Hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


# --- 5. ORDER ITEM (CHI TIẾT ĐƠN HÀNG) ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Giá tại thời điểm mua")

    def save(self, *args, **kwargs):
        # Lưu cứng giá tại thời điểm mua để tránh việc sau này giá SP thay đổi làm sai lệch báo cáo
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.price * self.quantity