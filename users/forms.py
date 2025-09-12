from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'avatar', 'phone_number', 'country', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'avatar', 'phone_number', 'country']

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("Аккаунт заблокирован", code='inactive')
