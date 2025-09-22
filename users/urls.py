from django.urls import path
from .views import signup_view, CustomLoginView, CustomLogoutView, ProfileView, ProfileUpdateView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
]
