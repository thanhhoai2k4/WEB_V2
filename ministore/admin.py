from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
# Import tất cả models của bạn
from .models import (
    UserProfile, Product, Category, Order, OrderItem,
    ProductImage, Review, Address, Cart, CartItem,
    Coupon, Transaction, StockLog, Post
)

# --- 1. SETUP USER PROFILE (Mở rộng User) ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Thông tin mở rộng (Profile)'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# --- 2. SETUP PRODUCT (Sản phẩm & Ảnh) ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Số lượng dòng trống hiển thị sẵn
    readonly_fields = ['image_preview'] 

    def image_preview(self, obj):
        # Hiển thị ảnh nhỏ 50px
        if obj.image:
            return format_html('<img src="{}" width="50" style="object-fit:cover;" />', obj.image.url)
        return ""
    
    image_preview.short_description = "Xem trước"

class ProductAdmin(admin.ModelAdmin):
    # A. Danh sách hiển thị
    list_display = ('name', 'show_price', 'stock', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('stock', 'is_active')  # Sửa nhanh trên danh sách
    prepopulated_fields = {'slug': ('name',)}

    # B. Giao diện trang chi tiết (Form)
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('category', 'name', 'slug', 'description', 'is_active')
        }),
        ('Giá & Kho hàng', {
            'fields': ('base_price', 'sale_price', 'stock'),
            'classes': ('collapse',), # Nhóm này mặc định thu gọn
        }),
        ('Media & Thông số', {
            'fields': ('image', 'specifications'),
        }),
        ('Thống kê (Chỉ đọc)', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('views_count', 'created_at', 'updated_at')
    inlines = [ProductImageInline] # Nhúng form ảnh phụ

    def show_price(self, obj):
        return f"{obj.price:,.0f} đ"
    show_price.short_description = "Giá bán"

# --- 3. SETUP CATEGORY (Danh mục kéo thả) ---
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'is_active', 'id')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('name',)}
    
    # Thêm cái này để tìm kiếm danh mục dễ hơn nếu cây quá dài
    search_fields = ['name'] 


# --- 4. ĐĂNG KÝ (REGISTER) ---

# Xử lý User cũ -> mới
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Các model chính
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
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
admin.site.register(Post)