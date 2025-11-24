from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    
    return render(request, 'index.html')


def register_view(request):
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        phone = request.POST.get('phone')  # Dữ liệu này thuộc về Profile

        # 2. Kiểm tra tính hợp lệ (Validation cơ bản)
        if password != re_password:
            messages.error(request, "Mật khẩu không khớp!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại!")
            return redirect('register')

        # 3. Tạo User
        try:
            # Tạo user mới
            new_user = User.objects.create_user(username=username, email=email, password=password)

            # 4. Cập nhật Profile (Profile đã được Signal tạo tự động rồi)
            # Chúng ta chỉ cần lấy ra và sửa đổi
            new_user.profile.phone_number = phone
            new_user.profile.save()

            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {e}")
            return redirect('register')

    return render(request, 'register.html')