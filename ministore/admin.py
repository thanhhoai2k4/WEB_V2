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

# 3. Hủy đăng ký User cũ và đăng ký User mới
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Product)
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




from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product

# Hiển thị Category dạng cây có thể kéo thả để sắp xếp
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_cumulative_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)