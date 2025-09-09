from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Count
from .models import Client, Message, Mailing, Attempt, CustomUser
from .forms import ClientForm, MessageForm, MailingForm, UserRegisterForm

@cache_page(60 * 5)
@login_required
def home_view(request):
    user_mailings = Mailing.objects.filter(owner=request.user)
    user_attempts = Attempt.objects.filter(mailing__in=user_mailings)

    context = {
        'successful_attempts': user_attempts.filter(status='Успешно').count(),
        'failed_attempts': user_attempts.filter(status='Не успешно').count(),
        'total_messages_sent': user_attempts.count(),
    }
    return render(request, 'mailing_app/home.html', context)

@cache_page(60 * 3)
@login_required
def client_list(request):
    if request.user.role == 'manager':
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(mailing__owner=request.user).distinct()
    return render(request, 'mailing_app/client_list.html', {'clients': clients})

@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('client_list')
    return render(request, 'mailing_app/client_form.html', {'form': form})

@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.user.role != 'manager' and not Mailing.objects.filter(clients=client, owner=request.user).exists():
        return HttpResponseForbidden("Нет доступа")
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        return redirect('client_list')
    return render(request, 'mailing_app/client_form.html', {'form': form})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.user.role != 'manager' and not Mailing.objects.filter(clients=client, owner=request.user).exists():
        return HttpResponseForbidden("Нет доступа")
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'mailing_app/client_confirm_delete.html', {'client': client})

@cache_page(60 * 3)
@login_required
def message_list(request):
    if request.user.role == 'manager':
        messages_qs = Message.objects.all()
    else:
        messages_qs = Message.objects.filter(mailing__owner=request.user).distinct()
    return render(request, 'mailing_app/message_list.html', {'messages': messages_qs})

@login_required
def message_create(request):
    form = MessageForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('message_list')
    return render(request, 'mailing_app/message_form.html', {'form': form})

@login_required
def message_update(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.user.role != 'manager' and not Mailing.objects.filter(message=message, owner=request.user).exists():
        return HttpResponseForbidden("Нет доступа")
    form = MessageForm(request.POST or None, instance=message)
    if form.is_valid():
        form.save()
        return redirect('message_list')
    return render(request, 'mailing_app/message_form.html', {'form': form})

@login_required
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.user.role != 'manager' and not Mailing.objects.filter(message=message, owner=request.user).exists():
        return HttpResponseForbidden("Нет доступа")
    if request.method == 'POST':
        message.delete()
        return redirect('message_list')
    return render(request, 'mailing_app/message_confirm_delete.html', {'message': message})

@cache_page(60 * 3)
@login_required
def mailing_list(request):
    if request.user.role == 'manager':
        mailings = Mailing.objects.all()
    else:
        mailings = Mailing.objects.filter(owner=request.user)
    return render(request, 'mailing_app/mailing_list.html', {'mailings': mailings})

@login_required
def mailing_create(request):
    form = MailingForm(request.POST or None)
    if form.is_valid():
        mailing = form.save(commit=False)
        mailing.owner = request.user
        mailing.save()
        form.save_m2m()
        return redirect('mailing_list')
    return render(request, 'mailing_app/mailing_form.html', {'form': form})

@login_required
def mailing_update(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.owner != request.user and request.user.role != 'manager':
        return HttpResponseForbidden("Нет доступа")
    form = MailingForm(request.POST or None, instance=mailing)
    if form.is_valid():
        form.save()
        return redirect('mailing_list')
    return render(request, 'mailing_app/mailing_form.html', {'form': form})

@login_required
def mailing_delete(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.owner != request.user and request.user.role != 'manager':
        return HttpResponseForbidden("Нет доступа")
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing_list')
    return render(request, 'mailing_app/mailing_confirm_delete.html', {'mailing': mailing})

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

def signup_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'mailing_app/signup.html', {'form': form})
