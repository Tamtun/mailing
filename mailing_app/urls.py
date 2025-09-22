from django.urls import path
from .views import (
    home_view,
    mailing_send, deactivate_mailing,
    user_list, block_user,
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    MailingListView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    AttemptListView, MailingReportView
)
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home_view, name='home'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', mailing_send, name='mailing_send'),
    path('mailings/<int:pk>/deactivate/', deactivate_mailing, name='deactivate_mailing'),
    path('login/', auth_views.LoginView.as_view(template_name='mailing_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='mailing_app/password_reset.html'), name='password_reset'),
    path('users/', user_list, name='user_list'),
    path('users/<int:pk>/block/', block_user, name='block_user'),
    path('attempts/', AttemptListView.as_view(), name='attempt_list'),
    path('reports/', MailingReportView.as_view(), name='mailing_report'),
]
