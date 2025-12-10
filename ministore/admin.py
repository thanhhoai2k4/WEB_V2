# from .models import *
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
# from .models import UserProfile, Product, Category, Order  # Import các model của bạn
# from django.utils.html import format_html

# # 1. Định nghĩa form nhập liệu Profile nằm ngay trong trang User
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'Thông tin mở rộng (Profile)'

# # 2. Tạo UserAdmin mới kế thừa từ cái cũ
# class UserAdmin(BaseUserAdmin):
#     inlines = (UserProfileInline,)

# #test
# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1  # Số lượng dòng trống hiển thị sẵn để thêm ảnh
#     readonly_fields = ['image_preview'] # Nếu muốn hiện ảnh xem trước (cần viết hàm trong model)

#     def image_preview(self, obj):
#         # Hàm phụ để hiển thị ảnh nhỏ (nếu bạn muốn nâng cao)
#         if obj.image:
#             return format_html('<img src="{}" width="50" />', obj.image.url)
#         return ""
# #test
# class ProductAdmin(admin.ModelAdmin):
#     # A. Tùy chỉnh danh sách hiển thị (Trang danh sách)
#     list_display = ('name', 'show_price', 'stock', 'category', 'is_active', 'created_at')
#     list_filter = ('category', 'is_active', 'created_at')
#     search_fields = ('name', 'description')
#     list_editable = ('stock', 'is_active')  # Cho phép sửa nhanh tồn kho và trạng thái ngay ở list

#     # B. Tùy chỉnh trang Thêm/Sửa (Trang chi tiết)
#     # prepopulated_fields: Tự động tạo slug khi gõ tên sản phẩm
#     prepopulated_fields = {'slug': ('name',)}

#     # fieldsets: Gom nhóm các trường lại cho gọn
#     fieldsets = (
#         ('Thông tin chung', {
#             'fields': ('category', 'name', 'slug', 'description', 'is_active')
#         }),
#         ('Giá & Kho hàng', {
#             'fields': ('base_price', 'sale_price', 'stock'),
#             'classes': ('collapse',),  # Thêm class 'collapse' để nhóm này mặc định thu gọn (nếu muốn)
#         }),
#         ('Media & Thông số', {
#             'fields': ('image', 'specifications'),
#         }),
#         ('Thống kê (Chỉ đọc)', {
#             'fields': ('views_count', 'created_at', 'updated_at'),
#             # Các trường này thường không cho sửa
#             'classes': ('collapse',),
#         }),
#     )

#     # readonly_fields: Các trường chỉ được xem, không được sửa
#     readonly_fields = ('views_count', 'created_at', 'updated_at')

#     # inlines: Nhúng form thêm ảnh phụ vào trang sản phẩm
#     inlines = [ProductImageInline]

#     # Hàm hiển thị giá tiền đẹp hơn trong list
#     def show_price(self, obj):
#         return f"{obj.price:,.0f} đ"

#     show_price.short_description = "Giá bán"
# admin.site.register(Product, ProductAdmin)
# #test


# # 3. Hủy đăng ký User cũ và đăng ký User mới
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# admin.site.register(Category)
# admin.site.register(ProductImage)
# admin.site.register(Order)
# admin.site.register(OrderItem)
# admin.site.register(Review)
# admin.site.register(Address)
# admin.site.register(Cart)
# admin.site.register(CartItem)
# admin.site.register(Coupon)
# admin.site.register(Transaction)
# admin.site.register(StockLog)
# admin.site.register(Category_TEST)
# admin.site.register(Product_TEST)


# # from django.contrib import admin
# # from mptt.admin import DraggableMPTTAdmin # Import cái này
# # from .models import Category

# # class CategoryAdmin(DraggableMPTTAdmin):
# #     mptt_indent_field = "name"
# #     list_display = ('tree_actions', 'indented_title', 'is_active', 'id')
# #     list_display_links = ('indented_title',)
# #     prepopulated_fields = {'slug': ('name',)}

# # admin.site.register(Category, CategoryAdmin)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html # <-- Cần thêm dòng này để hiện ảnh preview
from mptt.admin import DraggableMPTTAdmin # <-- Import cho Category

# Import tất cả models của bạn
from .models import (
    UserProfile, Product, Category, Order, OrderItem,
    ProductImage, Review, Address, Cart, CartItem,
    Coupon, Transaction, StockLog, Post # Đừng quên import Post nếu có
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
admin.site.register(Category, CategoryAdmin) # Đã kích hoạt giao diện Kéo-Thả
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