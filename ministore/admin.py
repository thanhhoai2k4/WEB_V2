from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Product, Category, Order  # Import các model của bạn


# 1. Định nghĩa form nhập liệu Profile nằm ngay trong trang User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Thông tin mở rộng (Profile)'

# 2. Tạo UserAdmin mới kế thừa từ cái cũ
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

#test
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số lượng dòng trống hiển thị sẵn để thêm ảnh
    readonly_fields = ['image_preview'] # Nếu muốn hiện ảnh xem trước (cần viết hàm trong model)

    def image_preview(self, obj):
        # Hàm phụ để hiển thị ảnh nhỏ (nếu bạn muốn nâng cao)
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return ""
#test
class ProductAdmin(admin.ModelAdmin):
    # A. Tùy chỉnh danh sách hiển thị (Trang danh sách)
    list_display = ('name', 'show_price', 'stock', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('stock', 'is_active')  # Cho phép sửa nhanh tồn kho và trạng thái ngay ở list

    # B. Tùy chỉnh trang Thêm/Sửa (Trang chi tiết)
    # prepopulated_fields: Tự động tạo slug khi gõ tên sản phẩm
    prepopulated_fields = {'slug': ('name',)}

    # fieldsets: Gom nhóm các trường lại cho gọn
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('category', 'name', 'slug', 'description', 'is_active')
        }),
        ('Giá & Kho hàng', {
            'fields': ('base_price', 'sale_price', 'stock'),
            'classes': ('collapse',),  # Thêm class 'collapse' để nhóm này mặc định thu gọn (nếu muốn)
        }),
        ('Media & Thông số', {
            'fields': ('image', 'specifications'),
        }),
        ('Thống kê (Chỉ đọc)', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            # Các trường này thường không cho sửa
            'classes': ('collapse',),
        }),
    )

    # readonly_fields: Các trường chỉ được xem, không được sửa
    readonly_fields = ('views_count', 'created_at', 'updated_at')

    # inlines: Nhúng form thêm ảnh phụ vào trang sản phẩm
    inlines = [ProductImageInline]

    # Hàm hiển thị giá tiền đẹp hơn trong list
    def show_price(self, obj):
        return f"{obj.price:,.0f} đ"

    show_price.short_description = "Giá bán"
admin.site.register(Product, ProductAdmin)
#test


# 3. Hủy đăng ký User cũ và đăng ký User mới
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(Transaction)
admin.site.register(StockLog)
admin.site.register(Category_TEST)
admin.site.register(Product_TEST)