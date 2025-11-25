from .models import Cart, CartItem
from django.db.models import Sum

def cart_count(request):
    total_quantity = 0
    
    # 1. Xác định giỏ hàng (Logic tương tự hàm _get_cart trong views.py của bạn)
    if request.user.is_authenticated:
        # Nếu đã đăng nhập: Tìm theo User
        cart = Cart.objects.filter(user=request.user).first()
    else:
        # Nếu chưa đăng nhập: Tìm theo Session Key
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
        else:
            cart = None

    # 2. Tính tổng số lượng item
    if cart:
        # Dùng aggregate để tính tổng cột quantity của các CartItem thuộc giỏ này
        result = CartItem.objects.filter(cart=cart).aggregate(total=Sum('quantity'))
        if result['total']:
            total_quantity = result['total']

    # 3. Trả về biến 'cart_quantity' để dùng ngoài HTML
    return {'cart_quantity': total_quantity}