from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegisterForm

def signup_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'users/signup.html', {'form': form})
