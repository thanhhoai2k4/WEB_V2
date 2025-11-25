from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q # doc sach UIT de hieu ve Q
from .models import Product, Category


def home(request):

    mobile_products = Product.objects.select_related('category').filter(
        is_active=True  # Chỉ lấy sản phẩm đang kinh doanh
    ).filter(
        Q(name__icontains='mobile') |
        Q(name__icontains='phone') |
        Q(category__slug__icontains='mobile') |
        Q(category__slug__icontains='phone')
    ).order_by('-created_at')[:4] # Slicing: Giới hạn 4 sản phẩm


    smart_products = Product.objects.select_related('category').filter(
        is_active=True
    ).filter(
        Q(name__icontains='smartwatch')|
        Q(name__icontains='smart') |
        Q(name__icontains='watch') |
        Q(category__slug__icontains='smartwatch')
    ).order_by('-created_at')[:4]
    context = {
        'mobile_products': mobile_products,
        'smart_products': smart_products,
    }

    return render(request, 'index.html', context)


    return render(request, 'index.html')

def register(request):
    # Nếu đã đăng nhập thì đá về trang chủ, không cho đăng ký nữa
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # 1. Lấy dữ liệu
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        phone = request.POST.get('phone')

        # 2. Validate
        if password != re_password:
            messages.error(request, "Mật khẩu không khớp!")
            return render(request, 'register.html', {'active_tab': 'register'}) # Giữ lại tab đăng ký

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại!")
            return render(request, 'register.html', {'active_tab': 'register'})

        # 3. Tạo User
        try:
            new_user = User.objects.create_user(username=username, email=email, password=password)
            
            # Cập nhật Profile (Signal đã tạo profile, giờ ta update)
            if hasattr(new_user, 'profile'):
                new_user.profile.phone_number = phone
                new_user.profile.save()
            
            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
            # Chuyển sang tab login để người dùng nhập lại
            return redirect('login') 

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {e}")
            return render(request, 'register.html', {'active_tab': 'register'})

    # GET request: Hiển thị form và mặc định active tab Register
    return render(request, 'register.html', {'active_tab': 'register'})

def login_view(request):
    # Nếu đã đăng nhập thì đá về trang chủ
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Chào mừng {username} quay trở lại!")
            
            # Kiểm tra xem có url nào cần redirect tới không (ví dụ: đang mua hàng bị bắt đăng nhập)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu!")
            # Render lại trang với tab login đang mở
            return render(request, 'register.html', {'active_tab': 'login'})
            
    # GET request: Quan trọng! Phải render trang thay vì redirect loop
    print("GET LOGIN")
    return render(request, 'register.html', {'active_tab': 'login'})

def logout_user(request):
    logout(request)
    messages.success(request, "Đã đăng xuất thành công.")
    return redirect('login')

# View này có thể bỏ hoặc để dùng chung
def auth_view(request):
    return render(request, 'register.html', {'active_tab': 'login'})





def shop(request):
    # 1. Lấy dữ liệu gốc
    products = Product.objects.all()
    categories = Category.objects.all()

    # 2. Lấy tham số từ URL (Method GET)
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # 3. Áp dụng bộ lọc (Logic lọc tuần tự)
    
    # Lọc theo danh mục
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Lọc theo từ khóa tìm kiếm (Tìm trong tên hoặc mô tả)
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Lọc theo giá tối thiểu
    if min_price:
        try:
            products = products.filter(price__gte=min_price) # gte: greater than or equal
        except ValueError:
            pass # Bỏ qua nếu người dùng nhập linh tinh không phải số

    # Lọc theo giá tối đa
    if max_price:
        try:
            products = products.filter(price__lte=max_price) # lte: less than or equal
        except ValueError:
            pass

    context = {
        'products': products,
        'categories': categories,
        # Trả lại các giá trị đã lọc để giữ lại trên form sau khi reload
        'current_category': category_slug,
        'search_query': search_query,
        'min_price': min_price, 
        'max_price': max_price
    }
    return render(request, 'shop.html', context)