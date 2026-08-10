from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'ادمین'),
        ('user', 'کاربر'),
    ]
    full_name = models.CharField('نام کامل', max_length=150)
    role = models.CharField('نقش', max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.full_name or self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('hardware', 'سخت‌افزار'),
        ('software', 'نرم‌افزار'),
        ('network', 'شبکه و اینترنت'),
        ('email', 'ایمیل'),
        ('access', 'دسترسی'),
        ('other', 'سایر'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('critical', 'بحرانی'),
    ]
    STATUS_CHOICES = [
        ('open', 'باز'),
        ('in_progress', 'در حال بررسی'),
        ('resolved', 'حل‌شده'),
        ('closed', 'بسته'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name='کاربر')
    title = models.CharField('عنوان', max_length=255)
    description = models.TextField('توضیحات')
    category = models.CharField('دسته‌بندی', max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField('اولویت', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='open')
    admin_note = models.TextField('یادداشت ادمین', blank=True, null=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'

    def __str__(self):
        return f"#{self.id} - {self.title}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='کاربر')
    title = models.CharField('عنوان', max_length=255)
    body = models.TextField('متن', blank=True)
    link = models.CharField('لینک', max_length=255, default='/')
    is_read = models.BooleanField('خوانده شده', default=False)
    created_at = models.DateTimeField('تاریخ', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نوتیفیکیشن'
        verbose_name_plural = 'نوتیفیکیشن‌ها'

    def __str__(self):
        return self.title
