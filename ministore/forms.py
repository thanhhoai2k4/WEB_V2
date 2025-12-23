from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Order


class Usergisiger(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ["username", "password"]

        widgets = {

        }


# basic form for user
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Form 2:profile
class ProfileUpdateForm(forms.ModelForm):
    

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

# Form 3: order history 
class OrderForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('COD', 'Thanh toán khi nhận hàng (COD)'),
        ('BANKING', 'Chuyển khoản ngân hàng'),
    ]
    
    # Ghi đè widget để hiển thị lựa chọn thay vì text box
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect, label="Phương thức thanh toán")

    class Meta:
        model = Order
        fields = ['shipping_full_name', 'shipping_phone', 'shipping_address', 'note', 'payment_method']
        widgets = {
            'shipping_full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nguyễn Văn A'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0909...'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Số nhà, Đường, Quận/Huyện...'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Giao giờ hành chính...'}),
        }
        labels = {
            'shipping_full_name': 'Họ và tên người nhận',
            'shipping_phone': 'Số điện thoại',
            'shipping_address': 'Địa chỉ giao hàng',
            'note': 'Ghi chú đơn hàng',
        }

class FormTest(forms.ModelForm):
    # user_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # address =  forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', "last_name", "email", "password"]
    def __str__(self):
        return "form test"


# --- New: Staff registration form used from admin login page ---
class StaffRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    registration_key = forms.CharField(label='Mã đăng ký', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Tên đăng nhập đã tồn tại")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email đã được sử dụng")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError({'password2': "Mật khẩu không khớp"})
        # validate password strength
        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                raise ValidationError({'password1': e.messages})
        return cleaned

    def save(self, commit=True, make_staff=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # staff account only (no superuser)
        if make_staff:
            user.is_staff = True
            user.is_active = True
            user.is_superuser = False
        if commit:
            user.save()
        return user

