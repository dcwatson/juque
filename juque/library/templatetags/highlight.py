from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def highlight(s, q=None):
    if not q:
        return s
    return mark_safe(re.sub(r'(%s)' % q, r'<em>\1</em>', s, flags=re.I))
