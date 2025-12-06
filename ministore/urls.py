from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),


    # register
    path('auth/', views.auth_view, name='auth'),
    path("Register/", views.register, name="register"),
    path("Login/", views.login_view, name="login"),
    path('logout/', views.logout_user, name='logout'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),



    # profile
    path('profile/', views.profile, name='profile'),

    # change password
    path('password-change/', views.ChangePasswordView.as_view(), name='password_change'),


    path('about/', views.about, name='about'),



    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),


    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    


    # checkout
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment_gateway, name='payment_gateway'),
    path('api/check-payment-status/', views.check_payment_status, name='check_payment_status'),
    path('fake-webhook/<int:order_id>/', views.fake_payment_webhook, name='fake_webhook'), # Chỉ dùng test






    path('chi-tiet-nguoi-mua-hang/', views.user_list, name='chi_tiet_nguoi_mua_hang'),

    path("formtest/", views.form_test, name="formtest"),




    # so sanh
    path('toggle-compare/<int:product_id>/', views.toggle_compare, name='toggle_compare'),
    path('compare/', views.compare_view, name='compare_view'),

]

