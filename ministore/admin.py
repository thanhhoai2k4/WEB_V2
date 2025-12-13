from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html

from unfold.decorators import display
from django.contrib.admin.sites import NotRegistered
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import (
    UserProfile, Product, Category, Order, OrderItem,
    ProductImage, Review, Address, Cart, CartItem,
    Coupon, Transaction, StockLog, Post
)

from django.utils.safestring import mark_safe # <--- Quan trọng
from django.utils.html import escape # Để bảo mật tên danh mục
from treewidget.widgets import TreeWidget
from mptt.models import TreeForeignKey

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
    list_display = ('name', 'show_price', 'stock', 'category_badge', 'is_active', 'created_at')
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

    formfield_overrides = {
        TreeForeignKey: {'widget': TreeWidget(options={
            'expand_selected_ancestors': True,  # Tự động mở nhánh cha của mục đang chọn
            'open_links_in_new_window': True
        })},
    }

    # Hiển thị Category đẹp hơn trong danh sách sản phẩm (Option thêm)
    @display(description="Danh mục")
    def category_badge(self, obj):
        if obj.category:
            # Hiển thị tên danh mục với màu sắc nổi bật
            return format_html(
                '<span style="background-color: #f3f4f6; color: #374151; padding: 4px 8px; border-radius: 6px; font-weight: 500; border: 1px solid #e5e7eb;">📂 {}</span>',
                obj.category.name
            )
        return "-"

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

    @display(description="Danh mục (Cây phân cấp)")
    def indented_title(self, obj):
        level = getattr(obj, 'level', 0)
        indent_pixels = level * 24

        # 1. Tạo Prefix (Dùng f-string bình thường, không cần format_html ở đây)
        prefix = ""
        if level > 0:
            prefix = f'<span style="margin-left: {indent_pixels}px; color: #9ca3af; font-family: monospace; font-size: 1.2em;">├─ </span>'

        # 2. Icon hiển thị
        icon = '📂' if not obj.is_leaf_node() else '📄'

        # 3. Tên danh mục
        # QUAN TRỌNG: Dùng escape() để mã hóa tên danh mục, tránh lỗi nếu tên có ký tự đặc biệt
        safe_name = escape(obj.name)

        if level == 0:
            name_display = f"<b>{safe_name}</b>"
        else:
            name_display = safe_name

        # 4. Kết hợp tất cả lại thành một chuỗi HTML lớn
        full_html = f'''
                <div style="display: flex; align-items: center;">
                    {prefix}
                    {icon}
                    <span style="margin-left: 8px;">{name_display}</span>
                </div>
            '''

        # 5. Trả về với mark_safe (Đây là "chìa khóa" để render HTML)
        return mark_safe(full_html)

    @display(description="Số SP")
    def product_count_display(self, obj):
        count = obj.products.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{}</span>',
                count
            )
        return "-"






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




