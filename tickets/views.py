from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import User, Ticket, Notification


def is_admin(user):
    return user.is_authenticated and user.is_admin


def create_notification(user, title, body, link='/'):
    Notification.objects.create(user=user, title=title, body=body, link=link)


def notify_admins(title, body, link='/'):
    for admin in User.objects.filter(role='admin'):
        create_notification(admin, title, body, link)


# ---------- Auth ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'خوش آمدید {user.full_name or user.username}')
            return redirect('home')
        messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
    return render(request, 'tickets/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'با موفقیت خارج شدید')
    return redirect('login')


# ---------- Home / Dashboard ----------
@login_required
def home(request):
    if request.user.is_admin:
        return admin_dashboard(request)
    return user_dashboard(request)


@login_required
def user_dashboard(request):
    tickets = Ticket.objects.filter(user=request.user)
    status_filter = request.GET.get('status')
    if status_filter in dict(Ticket.STATUS_CHOICES):
        tickets = tickets.filter(status=status_filter)

    stats = {
        'total': Ticket.objects.filter(user=request.user).count(),
        'open': Ticket.objects.filter(user=request.user, status='open').count(),
        'in_progress': Ticket.objects.filter(user=request.user, status='in_progress').count(),
        'resolved': Ticket.objects.filter(user=request.user, status='resolved').count(),
        'closed': Ticket.objects.filter(user=request.user, status='closed').count(),
    }
    return render(request, 'tickets/user_dashboard.html', {
        'tickets': tickets,
        'stats': stats,
        'current_status': status_filter or '',
    })


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    tickets = Ticket.objects.select_related('user').all()

    # Filters
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    category = request.GET.get('category', '')
    user_id = request.GET.get('user', '')

    if q:
        tickets = tickets.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__full_name__icontains=q)
        )
    if status in dict(Ticket.STATUS_CHOICES):
        tickets = tickets.filter(status=status)
    if priority in dict(Ticket.PRIORITY_CHOICES):
        tickets = tickets.filter(priority=priority)
    if category in dict(Ticket.CATEGORY_CHOICES):
        tickets = tickets.filter(category=category)
    if user_id.isdigit():
        tickets = tickets.filter(user_id=int(user_id))

    stats = {
        'total': Ticket.objects.count(),
        'open': Ticket.objects.filter(status='open').count(),
        'in_progress': Ticket.objects.filter(status='in_progress').count(),
        'resolved': Ticket.objects.filter(status='resolved').count(),
        'closed': Ticket.objects.filter(status='closed').count(),
    }

    users_list = User.objects.all().order_by('full_name')

    return render(request, 'tickets/admin_dashboard.html', {
        'tickets': tickets[:100],  # limit for performance
        'stats': stats,
        'users_list': users_list,
        'filters': {
            'q': q,
            'status': status,
            'priority': priority,
            'category': category,
            'user': user_id,
        },
        'STATUS_CHOICES': Ticket.STATUS_CHOICES,
        'PRIORITY_CHOICES': Ticket.PRIORITY_CHOICES,
        'CATEGORY_CHOICES': Ticket.CATEGORY_CHOICES,
    })


# ---------- Tickets ----------
@login_required
def ticket_new(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other')
        priority = request.POST.get('priority', 'medium')

        if not title or not description:
            messages.error(request, 'عنوان و توضیحات الزامی است')
            return render(request, 'tickets/ticket_form.html', {
                'CATEGORY_CHOICES': Ticket.CATEGORY_CHOICES,
                'PRIORITY_CHOICES': Ticket.PRIORITY_CHOICES,
            })

        ticket = Ticket.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category if category in dict(Ticket.CATEGORY_CHOICES) else 'other',
            priority=priority if priority in dict(Ticket.PRIORITY_CHOICES) else 'medium',
        )
        notify_admins(
            f'تیکت جدید #{ticket.id}',
            f'{request.user.full_name or request.user.username}: {title}',
            f'/ticket/{ticket.id}/'
        )
        messages.success(request, 'تیکت با موفقیت ثبت شد')
        return redirect('ticket_detail', pk=ticket.id)

    return render(request, 'tickets/ticket_form.html', {
        'CATEGORY_CHOICES': Ticket.CATEGORY_CHOICES,
        'PRIORITY_CHOICES': Ticket.PRIORITY_CHOICES,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.select_related('user'), pk=pk)

    # Permission: owner or admin
    if not request.user.is_admin and ticket.user != request.user:
        messages.error(request, 'دسترسی غیرمجاز')
        return redirect('home')

    if request.method == 'POST' and request.user.is_admin:
        new_status = request.POST.get('status')
        admin_note = request.POST.get('admin_note', '').strip()

        changed = False
        if new_status in dict(Ticket.STATUS_CHOICES) and new_status != ticket.status:
            old = ticket.get_status_display()
            ticket.status = new_status
            changed = True
            create_notification(
                ticket.user,
                f'وضعیت تیکت #{ticket.id} تغییر کرد',
                f'وضعیت از «{old}» به «{ticket.get_status_display()}» تغییر یافت.',
                f'/ticket/{ticket.id}/'
            )
        if admin_note != (ticket.admin_note or ''):
            ticket.admin_note = admin_note
            changed = True
            if admin_note:
                create_notification(
                    ticket.user,
                    f'یادداشت جدید روی تیکت #{ticket.id}',
                    admin_note[:100],
                    f'/ticket/{ticket.id}/'
                )
        if changed:
            ticket.save()
            messages.success(request, 'تیکت بروزرسانی شد')
            return redirect('ticket_detail', pk=pk)

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'STATUS_CHOICES': Ticket.STATUS_CHOICES,
    })


# ---------- Admin User Management ----------
@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'tickets/admin_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_user_new(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        full_name = request.POST.get('full_name', '').strip()
        role = request.POST.get('role', 'user')

        if not username or not password or not full_name:
            messages.error(request, 'همه فیلدها الزامی است')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً استفاده شده')
        else:
            User.objects.create_user(
                username=username,
                password=password,
                full_name=full_name,
                role=role if role in ('admin', 'user') else 'user',
            )
            messages.success(request, 'کاربر با موفقیت ساخته شد')
            return redirect('admin_users')

    return render(request, 'tickets/admin_user_form.html', {'edit': False})


@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        role = request.POST.get('role', 'user')
        password = request.POST.get('password', '').strip()

        user.full_name = full_name
        user.role = role if role in ('admin', 'user') else user.role
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, 'کاربر ویرایش شد')
        return redirect('admin_users')

    return render(request, 'tickets/admin_user_form.html', {'edit': True, 'edit_user': user})


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'نمی‌توانید خودتان را حذف کنید')
    else:
        user.delete()
        messages.success(request, 'کاربر حذف شد')
    return redirect('admin_users')


# ---------- Notifications ----------
@login_required
def notifications(request):
    items = Notification.objects.filter(user=request.user)[:50]
    return render(request, 'tickets/notifications.html', {'items': items})


@login_required
@require_POST
def notifications_read_all(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'همه نوتیف‌ها خوانده شد')
    return redirect('notifications')


@login_required
def api_notifications_poll(request):
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    latest = list(Notification.objects.filter(user=request.user, is_read=False)
                  .order_by('-id')[:5]
                  .values('id', 'title', 'body', 'link'))
    return JsonResponse({'unread': unread, 'latest': latest})
