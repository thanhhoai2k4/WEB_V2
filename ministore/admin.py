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