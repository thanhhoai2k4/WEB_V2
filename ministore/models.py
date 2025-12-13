from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
# from mptt.models import MPTTModel, TreeForeignKey


from mptt.models import MPTTModel
from treewidget.fields import TreeForeignKey

# class Category_TEST(MPTTModel):
#     name = models.CharField(max_length=50)
#     slug = models.SlugField(unique=True)
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

#     class MPTTMeta:
#         order_insertion_by = ['name'] # Sắp xếp các node con

#     def __str__(self):
#         return self.name

# chuyen doi tu models.Model sang MPTTModel
class Category(MPTTModel):
    name = models.CharField(max_length=200, unique=True, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL thân thiện cho SEO")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True, help_text="Tắt danh mục này thay vì xóa nó")

    # class Meta:
    #     verbose_name_plural = "Categories"
    class MPTTMeta:
        order_insertion_by = ['name'] # Sắp xếp các node con

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Docstring for __str__

        :param self: Description
        """
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent

        sorted(full_path)
        return ' -> '.join(full_path[::-1])


class Product(models.Model):
    category = TreeForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name="Mô tả chi tiết", blank=True)

    # Pricing & Inventory
    base_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá gốc")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     verbose_name="Giá khuyến mãi")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")

    # Metadata
    image = models.ImageField(upload_to='products/', verbose_name="Ảnh đại diện")
    specifications = models.JSONField(default=dict, blank=True, verbose_name="Thông số kỹ thuật (JSON)")

    # Analytics & Control
    views_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def price(self):
        """Logic: Trả về giá thấp nhất đang hiệu lực"""
        return self.sale_price if self.sale_price and self.sale_price < self.base_price else self.base_price

    def __str__(self):
        return self.name





class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True, help_text="Văn bản thay thế cho SEO")



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Số sao (1-5)"
    )
    comment = models.TextField(verbose_name="Nội dung đánh giá")
    created_at = models.DateTimeField(auto_now_add=True)

    # Xác thực xã hội
    is_verified_purchase = models.BooleanField(default=False, verbose_name="Đã mua hàng thật")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}*)"


# --- 3. USER EXPERIENCE: CART & ADDRESS (MỚI) ---

class Address(models.Model):
    """Lưu danh bạ địa chỉ của người dùng để không phải nhập lại"""
    ADDRESS_TYPE = [('HOME', 'Nhà riêng'), ('OFFICE', 'Văn phòng')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100, verbose_name="Tỉnh/Thành")
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện")
    detailed_address = models.CharField(max_length=255, verbose_name="Số nhà, đường")
    is_default = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=ADDRESS_TYPE, default='HOME')

    def __str__(self):
        return f"{self.full_name} - {self.detailed_address}"


class Cart(models.Model):
    """Giỏ hàng lưu DB để đồng bộ đa thiết bị"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Cho khách vãng lai
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity


# --- 4. MARKETING: COUPONS (MỚI) ---

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giảm tối đa bao nhiêu tiền")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=100, help_text="Số lần mã này được dùng")
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and self.used_count < self.usage_limit

    def __str__(self):
        return self.code


# --- 5. COMMERCE: ORDERS ---

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xử lý'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('SHIPPING', 'Đang giao'),
        ('COMPLETED', 'Hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Snapshot thông tin giao hàng (Lưu cứng để không bị đổi khi user sửa Address)
    shipping_full_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField(help_text="Địa chỉ đầy đủ tại thời điểm mua")

    # Tài chính
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Logistics & Thanh toán
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50, default='COD')
    is_paid = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=50, blank=True, null=True, help_text="Mã vận đơn")

    note = models.TextField(blank=True, verbose_name="Ghi chú của khách")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.shipping_full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Giá tại thời điểm chốt đơn")

    def save(self, *args, **kwargs):
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """
    Lưu vết mọi giao dịch thanh toán (Thành công lẫn Thất bại).
    Lý do: Một đơn hàng (Order) có thể có nhiều lần thanh toán (VD: Lần 1 thẻ lỗi, Lần 2 thành công).
    """
    TRANSACTION_STATUS = [
        ('PENDING', 'Đang xử lý'),
        ('SUCCESS', 'Thành công'),
        ('FAILED', 'Thất bại'),
        ('REFUNDED', 'Đã hoàn tiền'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True,
                                      help_text="Mã giao dịch từ cổng thanh toán (VD: Stripe ID, Momo ID)")
    payment_method = models.CharField(max_length=50, default='COD')
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Số tiền giao dịch thực tế")
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='PENDING')

    # Dữ liệu thô để debug (Quan trọng cho kỹ thuật)
    raw_response = models.JSONField(default=dict, blank=True, verbose_name="Dữ liệu gốc từ cổng thanh toán")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trans {self.transaction_id or self.id} - {self.status}"


class StockLog(models.Model):
    """
    Sổ cái kho hàng: Ghi lại TẠI SAO số lượng thay đổi.
    Giúp trả lời câu hỏi: 'Tại sao tháng này mất 5 cái áo?' (Bán hay mất trộm?)
    """
    REASON_CHOICES = [
        ('IMPORT', 'Nhập kho'),
        ('SALE', 'Bán hàng'),
        ('RETURN', 'Khách trả hàng'),
        ('DAMAGE', 'Hư hỏng/Mất mát'),
        ('ADJUST', 'Kiểm kê điều chỉnh'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    change_quantity = models.IntegerField(help_text="Số lượng thay đổi (Âm là xuất, Dương là nhập)")
    old_stock = models.IntegerField(help_text="Tồn kho trước khi thay đổi")
    new_stock = models.IntegerField(help_text="Tồn kho sau khi thay đổi")

    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    note = models.TextField(blank=True, verbose_name="Ghi chú chi tiết")
    created_at = models.DateTimeField(auto_now_add=True)

    # Người thực hiện (Để quy trách nhiệm)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name}: {self.change_quantity} ({self.reason})"





class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Thông tin cá nhân mở rộng
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Ảnh đại diện")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ mặc định")

    # Hệ thống khách hàng thân thiết
    loyalty_points = models.IntegerField(default=0, verbose_name="Điểm tích lũy")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


# --- SIGNALS: TỰ ĐỘNG HÓA ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
        Ngay khi một User mới được tạo (created=True),
        hàm này sẽ tự động tạo một UserProfile rỗng đi kèm.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        # Chỉ lưu nếu profile đã tồn tại
        instance.profile.save()
    except ObjectDoesNotExist:
        # Nếu chưa có profile (đang trong quá trình tạo), thì bỏ qua, không báo lỗi
        pass
    except AttributeError:
        # Dự phòng cho các lỗi thuộc tính khác
        pass




class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='blog/', verbose_name="Ảnh bìa")
    content = models.TextField(verbose_name="Nội dung bài viết")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tác giả")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def save(self, *args, **kwargs):
        # Tự động tạo slug từ tiêu đề nếu chưa có
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    




from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Category_TEST(MPTTModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name'] # Sắp xếp các node con

    def __str__(self):
        return self.name


class Product_TEST(models.Model):
    category = TreeForeignKey(Category_TEST, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name="Mô tả chi tiết", blank=True)

    # Pricing & Inventory
    base_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá gốc")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     verbose_name="Giá khuyến mãi")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")

    # Metadata
    image = models.ImageField(upload_to='products/', verbose_name="Ảnh đại diện")
    specifications = models.JSONField(default=dict, blank=True, verbose_name="Thông số kỹ thuật (JSON)")

    # Analytics & Control
    views_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def price(self):
        """Logic: Trả về giá thấp nhất đang hiệu lực"""
        return self.sale_price if self.sale_price and self.sale_price < self.base_price else self.base_price

    def __str__(self):
        return self.name
