from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/edit/', views.client_update, name='client_update'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/edit/', views.message_update, name='message_update'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    path('mailings/', views.mailing_list, name='mailing_list'),
    path('mailings/create/', views.mailing_create, name='mailing_create'),
    path('mailings/<int:pk>/edit/', views.mailing_update, name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.mailing_delete, name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.mailing_send, name='mailing_send'),
    #path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='mailing_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='mailing_app/password_reset.html'), name='password_reset'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/block/', views.block_user, name='block_user'),
    path('mailings/<int:pk>/deactivate/', views.deactivate_mailing, name='deactivate_mailing'),
]
