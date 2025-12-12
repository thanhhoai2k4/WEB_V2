from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html

from mptt.admin import DraggableMPTTAdmin
# Import tất cả models của bạn
# test
from unfold.decorators import display
from django.contrib.admin.sites import NotRegistered
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import (
    UserProfile, Product, Category, Order, OrderItem,
    ProductImage, Review, Address, Cart, CartItem,
    Coupon, Transaction, StockLog, Post
)

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


# user profile
# -----------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Thông tin mở rộng (Profile)'
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    inlines = (UserProfileInline,)
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
# --------------------------

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    search_fields = ['name']
    list_display = ['name']

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


@admin.register(Product)
class ProductAdmin(ModelAdmin):
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



@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    # 1. Tìm kiếm & Lọc
    search_fields = ['name', 'slug']
    list_filter = ['is_active', 'level']
    list_filter_submit = True  # Nút lọc của Unfold

    # 2. Hiển thị danh sách
    # 'indented_title' để hiện cây thư mục, 'parent' để biết cha là ai
    list_display = ('indented_title', 'slug', 'is_active', 'product_count_display')

    # 3. Sắp xếp QUAN TRỌNG cho MPTT
    # Nếu không có dòng này, cây thư mục sẽ bị lộn xộn
    ordering = ('tree_id', 'lft')

    prepopulated_fields = {'slug': ('name',)}

    # 4. Form nhập liệu chi tiết
    fieldsets = (
        ('Thông tin chung', {
            'fields': (('name', 'slug'), 'parent', 'is_active'),
        }),
        ('Hình ảnh', {
            'fields': ('image',),
        }),
    )

    # --- CÁC HÀM TÙY BIẾN GIAO DIỆN ---

    @display(description="Danh mục (Cây phân cấp)", ordering="name")
    def indented_title(self, obj):
        """
        Tạo hiển thị thụt đầu dòng dựa trên level của category
        """
        level = getattr(obj, 'level', 0)
        indent_pixels = level * 24  # Thụt vào 24px mỗi cấp

        # Icon hiển thị: Folder mở cho cha, dấu chấm cho con
        icon = '📂' if not obj.is_leaf_node() else '📄'

        # Màu sắc đường kẻ
        line_style = f"margin-left: {indent_pixels}px; color: #9ca3af; font-family: monospace; font-size: 1.2em;"

        if level > 0:
            prefix = f'<span style="{line_style}">├─ </span>'
        else:
            prefix = ""

        # Kết hợp icon và tên, bôi đậm nếu là cấp cha (level 0)
        name_html = f"<b>{obj.name}</b>" if level == 0 else obj.name

        return format_html(
            '<div style="display: flex; align-items: center;">'
            '{}{}<span style="margin-left: 8px;">{}</span>'
            '</div>',
            format_html(prefix),  # Prefix an toàn
            icon,
            format_html(name_html)  # Tên an toàn
        )

    @display(description="Số SP")
    def product_count_display(self, obj):
        """
        Hiển thị số lượng sản phẩm trong danh mục này
        """
        count = obj.products.count()  # Giả sử related_name trong Product là 'products'
        if count > 0:
            return format_html(
                '<span style="background-color: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{}</span>',
                count
            )
        return "-"
# @admin.register(Category)
# class CategoryAdmin(ModelAdmin):
#     search_fields = ['name']
#     list_display = ('indented_title', 'slug', 'is_active', 'id')
#     list_filter = ['is_active', 'level']
#     prepopulated_fields = {'slug': ('name',)}
#
#     # Hiển thị cây phân cấp bằng text (thay thế cho kéo thả của MPTT)
#     def indented_title(self, obj):
#         return format_html(
#             '<span style="padding-left: {}px">{} {}</span>',
#             obj.level * 20,
#             "├─" if obj.level > 0 else "<b>•</b>",
#             obj.name
#         )
#
#     indented_title.short_description = "Danh mục"



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