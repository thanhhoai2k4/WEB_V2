from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q # doc sach UIT de hieu ve Q
from .models import Product, Category, CartItem, Cart
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage
from django.contrib.admin.views.decorators import staff_member_required
# PageNotAnIntege



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
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng!")
            return render(request, 'register.html', {'active_tab': 'register'})
        if User.objects.filter(profile__phone_number=phone).exists():
            messages.error(request, "Số điện thoại đã được sử dụng!")
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
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 1. Lưu lại session key của khách vãng lai TRƯỚC khi login
        # (Vì sau khi login, Django có thể đổi session key để bảo mật)
        anonymous_session_key = request.session.session_key
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # --- START LOGIC GỘP GIỎ HÀNG (SÁNG TẠO) ---
            # Ý tưởng: Tìm giỏ hàng của session cũ, gán nó cho User mới đăng nhập
            if anonymous_session_key:
                try:
                    # Tìm giỏ hàng "vô chủ" của session cũ
                    guest_cart = Cart.objects.get(session_key=anonymous_session_key, user__isnull=True)
                    
                    # Tìm hoặc tạo giỏ hàng của User
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    
                    # Chuyển từng món đồ từ Guest Cart -> User Cart
                    for item in guest_cart.items.all():
                        # Kiểm tra xem món này đã có trong giỏ User chưa
                        existing_item = CartItem.objects.filter(cart=user_cart, product=item.product).first()
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            # Nếu chưa có thì đổi chủ sở hữu sang User Cart
                            item.cart = user_cart
                            item.save()
                    
                    # Xóa giỏ hàng tạm sau khi đã chuyển hết đồ
                    guest_cart.delete()
                    
                except Cart.DoesNotExist:
                    pass # Không có giỏ hàng tạm thì thôi
            # --- END LOGIC ---

            messages.success(request, f"Chào mừng {username} quay trở lại!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu!")
            return render(request, 'register.html', {'active_tab': 'login'})
            
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
    # products = Product.objects.all()
    products = Product.objects.filter(is_active=True).annotate(
        current_price=Coalesce('sale_price', 'base_price')
    )
    categories = Category.objects.all()

    # 2. Lấy tham số từ URL (Method GET)
    category_slug = request.GET.get('category',"") 
    search_query = request.GET.get('q', "")
    min_price = request.GET.get('min_price',"")
    max_price = request.GET.get('max_price',"")

    # 3. Áp dụng bộ lọc (Logic lọc tuần tự)
    
    # Lọc theo danh mục
    if category_slug:
        products = products.filter(category__slug__icontains=category_slug, is_active=True)

    # Lọc theo từ khóa tìm kiếm (Tìm trong tên hoặc mô tả)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    # Lọc theo giá (Bây giờ ta có thể dùng current_price đã annotate)
    if min_price:
        try:
            products = products.filter(current_price__gte=float(min_price))
        except ValueError:
            pass # Bỏ qua nếu user nhập chữ

    if max_price:
        try:
            products = products.filter(current_price__lte=float(max_price))
        except ValueError:
            pass
    
    paginator = Paginator(products, 6)  # Hiển thị 6 sản phẩm mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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



def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # 3. Tăng lượt xem (Optional - Sáng tạo thêm)
    # Logic: Mỗi khi có người vào xem, ta tăng biến đếm này lên. 
    # Giúp bạn thống kê được sản phẩm nào đang "hot".
    product.views_count += 1
    product.save()

    context = {
        'product': product,
    }
    return render(request, 'single-product.html', context)







def _get_cart(request):
    """
    Hàm bổ trợ (Private helper): Lấy hoặc tạo giỏ hàng dựa trên trạng thái đăng nhập.
    Đây là cốt lõi của việc phân định "Lưu" hay "Không lưu" (tạm thời).
    """
    if request.user.is_authenticated:
        # Nếu đã đăng nhập: Lấy giỏ hàng theo User (Lưu vĩnh viễn)
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Nếu chưa đăng nhập: Lấy giỏ hàng theo Session (Lưu tạm thời)
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(
            session_key=session_key, 
            defaults={'user': None}
        )
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)

    # Kiểm tra xem sản phẩm đã có trong giỏ chưa
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        # Nếu có rồi thì tăng số lượng
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, "Đã cập nhật số lượng sản phẩm!")
    else:
        messages.success(request, "Đã thêm vào giỏ hàng!")
    
    return redirect('view_cart')

def view_cart(request):
    cart = _get_cart(request)
    items = cart.items.select_related('product').all()
    
    # Tính tổng tiền (Sử dụng Python để tính property total_price trong model)
    total_bill = sum(item.total_price for item in items)
    
    context = {
        'cart_items': items,
        'total_bill': total_bill
    }
    return render(request, 'cart.html', context)

def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect('view_cart')

def update_cart_item(request, item_id):
    """Cập nhật số lượng trực tiếp từ trang giỏ hàng"""
    if request.method == 'POST':
        cart = _get_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        action = request.POST.get('action')
        
        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease':
            item.quantity -= 1
            
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
            
    return redirect('view_cart')

from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    # --- PHẦN 1: XỬ LÝ FORM CẬP NHẬT ---
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Hồ sơ của bạn đã được cập nhật thành công!')
            return redirect('profile') # Post-Redirect-Get pattern
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # --- PHẦN 2 (THÊM MỚI): LẤY DỮ LIỆU GIỎ HÀNG ---
    # Sử dụng hàm helper _get_cart bạn đã viết ở trên
    cart = _get_cart(request) 
    
    # Lấy các item trong giỏ, dùng select_related để tối ưu truy vấn SQL
    cart_items = cart.items.select_related('product').all()
    
    # Tính tổng tiền (Reuse logic từ view_cart)
    total_bill = sum(item.total_price for item in cart_items)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'cart_items': cart_items, # Truyền giỏ hàng sang template
        'total_bill': total_bill, # Truyền tổng tiền
    }

    return render(request, 'profile.html', context)



class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html' # File HTML giao diện
    success_message = "Đổi mật khẩu thành công!" # Thông báo khi xong
    success_url = reverse_lazy('profile') # Đổi xong thì quay về trang Profile


def about(request):
    return render(request, 'about.html')




# Import thêm Model Post
from .models import Post 

def blog_list(request):
    """Hiển thị danh sách tất cả bài viết"""
    posts = Post.objects.all().order_by('-created_at') # Bài mới nhất lên đầu
    return render(request, 'blog.html', {'posts': posts})

def blog_detail(request, slug):
    """Hiển thị nội dung chi tiết một bài viết"""
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog_detail.html', {'post': post})



def search_suggestions(request):
    """
    API trả về gợi ý sản phẩm dưới dạng JSON cho thanh tìm kiếm.
    """
    query = request.GET.get('q', '')
    data = []

    if query:
        # Tìm kiếm trong tên sản phẩm, chỉ lấy 5 kết quả đầu tiên để tối ưu tốc độ
        products = Product.objects.filter(
            name__icontains=query, 
            is_active=True
        )[:5]

        for product in products:
            # Xây dựng dữ liệu trả về cho từng sản phẩm
            item = {
                'name': product.name,
                'price': product.price, # Sử dụng property price (đã tính giảm giá)
                'slug': product.slug,
                # Xử lý ảnh: nếu có ảnh thì lấy url, không thì rỗng
                'image': product.image.url if product.image else '', 
            }
            data.append(item)

    return JsonResponse({'results': data})




from .forms import OrderForm
from .models import Order, OrderItem

@login_required
def checkout(request):
    cart = _get_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    # 1. Nếu giỏ hàng rỗng thì đá về trang shop
    if not cart_items:
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('shop')

    # Tính lại tổng tiền để hiển thị
    total_bill = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 2. Tạo Order (nhưng chưa lưu hẳn vào DB để tính toán thêm)
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total_bill # Lưu tổng tiền tại thời điểm mua
            order.save() # Lúc này mới có ID của Order

            # 3. Chuyển CartItem -> OrderItem (Snapshot dữ liệu)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price # Quan trọng: Lưu giá tại thời điểm mua
                )
                
                # Trừ kho (Optional - logic nâng cao)
                # item.product.stock -= item.quantity
                # item.product.save()

            # 4. Xóa giỏ hàng sau khi đặt thành công
            cart.items.all().delete()

            # kiem tra xem thanh toan khi nhan hang hay la chuyen khoang
            if order.payment_method == 'BANKING':
                # chuyen sang trang web ma thanh toan
                return redirect('payment_gateway', order_id=order.id)


            
            # Gửi thông báo & Chuyển hướng
            messages.success(request, f"Đặt hàng thành công! Mã đơn: #{order.id}")
            return redirect('home') # Hoặc chuyển tới trang 'order_success'
    else:
        # --- LOGIC SÁNG TẠO: AUTO-FILL FORM ---
        initial_data = {
            'shipping_full_name': f"{request.user.last_name} {request.user.first_name}".strip(),
            'shipping_phone': '',
            'shipping_address': ''
        }
        # Nếu user có Profile, lấy dữ liệu lấp vào
        if hasattr(request.user, 'profile'):
            initial_data['shipping_phone'] = request.user.profile.phone_number
            initial_data['shipping_address'] = request.user.profile.address
            
        form = OrderForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_bill': total_bill
    }
    return render(request, 'checkout.html', context)




def payment_gateway(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # SÁNG TẠO: Tự động tạo link VietQR
    # Cấu trúc: https://img.vietqr.io/image/<BANK_ID>-<TK_NO>-<TEMPLATE>.png?amount=<TIEN>&addInfo=<NOIDUNG>
    # Bạn thay BANK_ID (ví dụ MB, VCB) và số tài khoản của bạn vào đây
    MY_BANK = {
        'BANK_ID': 'MB', 
        'ACCOUNT_NO': '0987654321', # Thay số tk của bạn
        'TEMPLATE': 'compact'
    }
    
    # Nội dung ck bắt buộc phải có mã đơn hàng để nhận diện
    content = f"THANHTOAN DONHANG {order.id}"
    qr_url = f"https://img.vietqr.io/image/{MY_BANK['BANK_ID']}-{MY_BANK['ACCOUNT_NO']}-{MY_BANK['TEMPLATE']}.png?amount={int(order.total_amount)}&addInfo={content}"

    return render(request, 'payment_gateway.html', {
        'order': order,
        'qr_url': qr_url,
        'timeout': 300 # 5 phút = 300 giây
    })

def check_payment_status(request):
    """API để frontend gọi liên tục (Polling) kiểm tra trạng thái"""
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if order.is_paid:
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'pending'})

# --- HÀM GIẢ LẬP WEBHOOK (Chỉ dùng để test) ---
def fake_payment_webhook(request, order_id):
    """Giả vờ ngân hàng báo tiền đã về"""
    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True
    order.status = 'CONFIRMED' # Đã xác nhận
    order.save()
    return JsonResponse({'message': 'Simulated Bank Transfer Success'})



def chi_tiet_nguoi_mua_hang(request):
    return render(request, 'chi_tiet_nguoi_mua_hang.html')


@staff_member_required(login_url='login')
def user_list(request):
    """
    Hiển thị danh sách tất cả user đã đăng ký.
    Chỉ dành cho Staff/Admin.
    """
    # Lấy tất cả user, sắp xếp theo ngày tham gia mới nhất
    users = User.objects.all().order_by('-date_joined')

    user_profiles = users.profile


    # lay dia chi

    
    context = {
        'users': users,
        'page_title': 'Danh sách khách hàng'
    }
    return render(request, 'user_list.html', context)