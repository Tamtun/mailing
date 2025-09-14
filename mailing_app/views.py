from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from users.models import CustomUser
from django.db.models import Count
from .models import Client, Message, Mailing, Attempt
from .forms import ClientForm, MessageForm, MailingForm
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
@cache_page(60 * 5)
def home_view(request):
    user_mailings = Mailing.objects.filter(owner=request.user)
    user_attempts = Attempt.objects.filter(mailing__in=user_mailings)

    context = {
        'successful_attempts': user_attempts.filter(status='Успешно').count(),
        'failed_attempts': user_attempts.filter(status='Не успешно').count(),
        'total_messages_sent': user_attempts.count(),
    }
    return render(request, 'mailing_app/home.html', context)

class ClientListView(ListView):
    model = Client
    template_name = 'mailing_app/client_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Client.objects.all()
        return Client.objects.filter(mailing__owner=user).distinct()

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing_app/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing_app/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role != 'manager' and not Mailing.objects.filter(clients=obj, owner=user).exists():
            raise PermissionDenied("Нет доступа")
        return obj

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'mailing_app/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role != 'manager' and not Mailing.objects.filter(clients=obj, owner=user).exists():
            raise PermissionDenied("Нет доступа")
        return obj

class MessageListView(ListView):
    model = Message
    template_name = 'mailing_app/message_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Message.objects.all()
        return Message.objects.filter(owner=user)

class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing_app/message_form.html'
    success_url = reverse_lazy('message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing_app/message_form.html'
    success_url = reverse_lazy('message_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role != 'manager' and obj.owner != user:
            raise PermissionDenied("Нет доступа")
        return obj

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing_app/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role != 'manager' and obj.owner != user:
            raise PermissionDenied("Нет доступа")
        return obj

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing_app/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_app/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        form.save_m2m()
        return response

class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_app/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if obj.owner != user and user.role != 'manager':
            raise PermissionDenied("Нет доступа")
        return obj

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing_app/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if obj.owner != user and user.role != 'manager':
            raise PermissionDenied("Нет доступа")
        return obj

@login_required
def mailing_send(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.owner != request.user and request.user.role != 'manager':
        return HttpResponseForbidden("Нет доступа")
    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email='noreply@example.com',
                recipient_list=[client.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                mailing=mailing,
                status='Успешно',
                server_response='Письмо отправлено успешно'
            )
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status='Не успешно',
                server_response=str(e)
            )
    mailing.status = 'Запущена'
    mailing.save()
    messages.success(request, 'Рассылка отправлена!')
    return redirect('mailing_list')

@login_required
def deactivate_mailing(request, pk):
    if request.user.role != 'manager':
        return HttpResponseForbidden("Нет доступа")
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_active = False
    mailing.save()
    messages.warning(request, f'Рассылка "{mailing.message.subject}" отключена.')
    return redirect('mailing_list')

@login_required
def user_list(request):
    if request.user.role != 'manager':
        return HttpResponseForbidden("Нет доступа")
    users = CustomUser.objects.all()
    return render(request, 'mailing_app/user_list.html', {'users': users})

@login_required
def block_user(request, pk):
    if request.user.role != 'manager':
        return HttpResponseForbidden("Нет доступа")
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_blocked = True
    user.save()
    return redirect('user_list')

class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'mailing_app/attempt_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Attempt.objects.all()
        return Attempt.objects.filter(mailing__owner=user)

class MailingReportView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing_app/mailing_report.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = []
        for mailing in context['object_list']:
            attempts = Attempt.objects.filter(mailing=mailing)
            report.append({
                'mailing': mailing,
                'total': attempts.count(),
                'success': attempts.filter(status='Успешно').count(),
                'fail': attempts.filter(status='Не успешно').count(),
            })
        context['report'] = report
        return context
