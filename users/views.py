from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegisterForm, EmailLoginForm, UserUpdateForm
from .models import CustomUser
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy

def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'mailing_app/login.html'
    authentication_form = EmailLoginForm

class CustomLogoutView(LogoutView):
    next_page = 'login'

class ProfileView(DetailView):
    model = CustomUser
    template_name = 'users/profile.html'

    def get_object(self):
        return self.request.user

class ProfileUpdateView(UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user