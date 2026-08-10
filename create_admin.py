#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketsystem.settings')
django.setup()

from tickets.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='',
        password='admin123',
        full_name='مدیر سیستم',
        role='admin'
    )
    print("✅ کاربر ادمین ساخته شد → admin / admin123")
else:
    print("کاربر admin از قبل وجود دارد.")
