from django import template
import jdatetime
from django.utils import timezone

register = template.Library()


@register.filter
def to_jalali(value, arg=None):
    """Convert datetime to Jalali (Persian) date. Use arg='date' for date only."""
    if not value:
        return "—"
    try:
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        jdt = jdatetime.datetime.fromgregorian(datetime=value)
        if arg == 'date':
            return jdt.strftime('%Y/%m/%d')
        return jdt.strftime('%Y/%m/%d %H:%M')
    except Exception:
        return str(value)[:16]
