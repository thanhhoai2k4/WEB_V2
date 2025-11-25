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
]