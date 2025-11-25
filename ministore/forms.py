from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# Form 1: Xử lý thông tin cơ bản (User Model)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# Form 2: Xử lý thông tin mở rộng (UserProfile Model)
class ProfileUpdateForm(forms.ModelForm):
    # Thêm class CSS bootstrap cho đẹp
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), 
        required=False
    )
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'birth_date', 'avatar']