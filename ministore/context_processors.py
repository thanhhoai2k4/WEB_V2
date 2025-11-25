# ministore/context_processors.py
from .models import Order

def cart_info(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            # Lấy đơn hàng chưa hoàn thành (giỏ hàng hiện tại)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            # Sử dụng property get_cart_items bạn đã viết trong models.py
            cartItems = order.get_cart_items 
        except:
            cartItems = 0
    else:
        # Xử lý cho khách vãng lai (nếu chưa làm cookie cart thì để tạm là 0)
        cartItems = 0
        
    # Trả về biến cartItems để dùng ở mọi template
    return {'cartItems': cartItems}