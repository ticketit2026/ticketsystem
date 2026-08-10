# سیستم تیکت IT - Django (آماده برای Render)

نسخه کامل سیستم تیکت با Django، آماده دیپلوی روی **Render.com**

## حساب پیش‌فرض
- نام کاربری: `admin`
- رمز عبور: `admin123`

---

## روش دیپلوی روی Render (گام‌به‌گام)

### روش ۱: با GitHub (پیشنهادی)

1. این پوشه را در یک ریپازیتوری GitHub قرار بده (یا از همین فایل zip استفاده کن).

2. برو به [dashboard.render.com](https://dashboard.render.com) و حساب بساز (با GitHub لاگین کن).

3. **New +** → **Web Service**

4. ریپازیتوری را انتخاب کن.

5. تنظیمات را این‌طور پر کن:

| فیلد | مقدار |
|------|-------|
| Name | it-ticket-system |
| Runtime | Python 3 |
| Build Command | `./build.sh` |
| Start Command | `gunicorn ticketsystem.wsgi:application` |
| Instance Type | Free |

6. در بخش **Environment** این متغیرها را اضافه کن:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | یک رشته تصادفی بلند (یا دکمه Generate) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |

7. **Create Web Service** را بزن.

8. بعد از اولین دیپلوی، برای ساخت کاربر ادمین:
   - به Shell سرویس برو (یا از تب Shell)
   - این دستور را بزن:

```bash
python manage.py shell -c "
from tickets.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '', 'admin123', full_name='مدیر سیستم', role='admin')
    print('Admin created')
"
```

---

### روش ۲: بدون GitHub (آپلود مستقیم)

اگر GitHub نداری، می‌تونی از **Blueprint** یا آپلود دستی استفاده کنی، ولی GitHub خیلی راحت‌تره.

---

## دیتابیس

- به صورت پیش‌فرض از **SQLite** استفاده می‌کند (برای شروع رایگان کافیست).
- اگر خواستی Postgres اضافه کنی:
  1. در Render یک **PostgreSQL** (Free) بساز
  2. متغیر محیطی `DATABASE_URL` را از دیتابیس کپی کن و به وب‌سرویس اضافه کن.

---

## نکات مهم Render رایگان

- بعد از حدود ۱۵ دقیقه بی‌استفاده بودن، سرویس می‌خوابد.
- اولین درخواست بعد از خواب ممکن است ۳۰–۶۰ ثانیه طول بکشد.
- برای استفاده شخصی و داخلی کاملاً قابل قبوله.

---

## توسعه محلی

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # یا با دستور بالا ادمین بساز
python manage.py runserver
```

---

## ساختار پروژه

```
ticketsystem/
├── build.sh              # دستور ساخت برای Render
├── Procfile
├── render.yaml
├── requirements.txt
├── manage.py
├── ticketsystem/         # تنظیمات
├── tickets/              # اپ اصلی
└── templates/
```
