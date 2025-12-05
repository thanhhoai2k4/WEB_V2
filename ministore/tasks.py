from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from django.utils import timezone
from datetime import timedelta

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
        return f"Email sent for Order #{order_id}"

    except Order.DoesNotExist:
        return f"Order #{order_id} not found!"
    except Exception as e:
        return f"Error sending email: {e}"
    



@shared_task
def send_login_notification_task(username, email, ip_address, login_time):
    """
    Task chạy ngầm gửi email cảnh báo khi có đăng nhập mới.
    """
    subject = f"Cảnh báo đăng nhập: Tài khoản {username}"
    message = f"""
    Xin chào {username},

    Tài khoản của bạn vừa đăng nhập thành công vào hệ thống MiniStore.
    
    Thông tin chi tiết:
    - Thời gian: {login_time}
    - Địa chỉ IP: {ip_address}
    
    Nếu không phải là bạn, vui lòng đổi mật khẩu ngay lập tức.
    
    Trân trọng,
    Đội ngũ bảo mật MiniStore.
    """
    
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, email_from, recipient_list)
        return f"Sent login alert to {email}"
    except Exception as e:
        return f"Failed to send login alert: {e}"




