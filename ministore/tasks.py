from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@shared_task
def send_order_confirmation_email_task(order_id, user_email, user_last_name, user_first_name):
    """
    Task chạy ngầm để gửi email xác nhận đơn hàng.
    """
    try:
        # Worker thực hiện Query database để lấy thông tin đơn hàng
        order = Order.objects.get(id=order_id)
        
        subject = f"Xác nhận đơn hàng #{order.id} từ MiniStore"
        message = f"""
        Chào {user_last_name} {user_first_name},

        Cảm ơn bạn đã đặt hàng tại MiniStore.
        Mã đơn hàng của bạn là: #{order.id}
        Tổng tiền: {order.total_amount:,.0f} VND
        Phương thức thanh toán: {order.payment_method}
        Trạng thái: {order.get_status_display()}

        Chúng tôi sẽ sớm liên hệ để giao hàng.
        Trân trọng.
        """
        
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_email, ]

        # Gửi mail (Hành động tốn thời gian này giờ đã nằm ở background)
        send_mail(subject, message, email_from, recipient_list)
        print(f"--- [SUCCESS] Đã gửi email thành công tới {user_email} ---") # In khi thành công
        return f"Email sent for Order #{order_id}"

    except Order.DoesNotExist:
        return f"Order #{order_id} not found!"
    except Exception as e:
        return f"Error sending email: {e}"