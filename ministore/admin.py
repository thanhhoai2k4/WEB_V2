from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
# removed unused format_html import

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
from django.utils.text import slugify

from treewidget.fields import TreeSelect, TreeModelChoiceField
from mptt.admin import DraggableMPTTAdmin
from django import forms

# import-export integration
from import_export import resources, fields as import_fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

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
            return mark_safe(f'<img src="{escape(obj.image.url)}" width="50" style="object-fit:cover;" />')
        return ""
    
    image_preview.short_description = "Xem trước"

# import-export resource for Product
class ProductResource(resources.ModelResource):
    category = import_fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'base_price', 'sale_price', 'stock',
            'category', 'is_active', 'views_count', 'created_at', 'updated_at'
        )
        export_order = (
            'id', 'name', 'slug', 'description', 'base_price', 'sale_price', 'stock',
            'category', 'is_active', 'views_count', 'created_at', 'updated_at'
        )

    def before_import_row(self, row, **kwargs):
        """
        Ensure the category value maps to an existing Category instance.
        Behavior:
        - Try to find Category by name (case-sensitive) then by slug.
        - If not found, create a new Category with slugified value.
        This helps imports that reference categories by name or slug.
        """
        cat_val = row.get('category')
        if not cat_val:
            return

        # try by exact name
        try:
            Category.objects.get(name=cat_val)
            return
        except Category.DoesNotExist:
            pass

        # try by slug
        try:
            Category.objects.get(slug=cat_val)
            return
        except Category.DoesNotExist:
            pass

        # create category automatically (safe default). Use slugify for slug.
        new_slug = slugify(cat_val)
        # avoid slug collision by appending a suffix if needed
        base_slug = new_slug
        i = 1
        while Category.objects.filter(slug=new_slug).exists():
            new_slug = f"{base_slug}-{i}"
            i += 1
        Category.objects.create(name=cat_val, slug=new_slug)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    # A. Danh sách hiển thị
    list_display = ('name', 'show_price', 'stock', 'category_badge', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('stock', 'is_active')  # Sửa nhanh trên danh sách
    prepopulated_fields = {'slug': ('name',)}

    # performance: avoid N+1 for category
    list_select_related = ('category',)
    list_per_page = 25

    # Bind our custom form inside the class to avoid ambiguous external assignment
    form = None  # will be set after ProductAdminForm is defined

    # Add resource_class for import-export
    resource_class = ProductResource

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

    # Hiển thị Category đẹp hơn trong danh sách sản phẩm (Option thêm)
    @display(description="Danh mục")
    def category_badge(self, obj):
        if obj.category:
            # Hiển thị tên danh mục với màu sắc nổi bật
            safe_cat = escape(obj.category.name)
            return mark_safe(f'<span style="background-color: #f3f4f6; color: #374151; padding: 4px 8px; border-radius: 6px; font-weight: 500; border: 1px solid #e5e7eb;">📂 {safe_cat}</span>')
        return "-"

    def show_price(self, obj):
        return f"{obj.price:,.0f} đ"
    show_price.short_description = "Giá bán"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Force the tree widget for category fields so the admin renders a tree selector
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.all()
            # The TreeSelect widget in this project/version does not accept a 'settings' kwarg
            # so we instantiate it without that parameter. If you need client-side options,
            # pass them via attrs (data-*), or upgrade the treewidget package.
            kwargs['widget'] = TreeSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductAdminForm(forms.ModelForm):
    # Explicitly use the TreeModelChoiceField with TreeSelect widget
    category = TreeModelChoiceField(
        queryset=Category.objects.all(),
        widget=TreeSelect(),
        # 'settings' is not a valid argument for fields; removed to avoid TypeError
    )

    class Meta:
        model = Product
        fields = '__all__'

    # Optional: you can adjust clean/validation here if needed

    # Tell admin to use our custom form so the category field renders as a tree

# Bind the custom form to the ProductAdmin (must be after the form class is defined)
ProductAdmin.form = ProductAdminForm







@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, ModelAdmin):
    # Use draggable tree admin to show categories as a tree and allow reordering
    mptt_indent_field = "name"
    list_display = ("tree_actions", "indented_title", "slug", "is_active", "product_count_display")
    list_display_links = ("indented_title",)

    # 1. Tìm kiếm & Lọc
    search_fields = ['name', 'slug']
    list_filter = ['is_active', 'level']
    list_filter_submit = True  # Nút lọc của Unfold

    # 3. Sắp xếp QUAN TRỌNG cho MPTT
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

    # Ensure admin add/change form uses TreeSelect for the parent FK so a tree is shown
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = Category.objects.all()
            kwargs['widget'] = TreeSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
            return mark_safe(f'<span style="background-color: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{escape(str(count))}</span>')
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




