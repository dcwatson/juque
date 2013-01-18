from django import template

register = template.Library()

@register.filter
def track_length(length):
    mins = int(length // 60)
    secs = int(length - (mins * 60))
    return '%d:%02d' % (mins, secs)

@register.filter
def bitrate(rate):
    vbr = ' (VBR)' if rate % 1000 != 0 else ''
    kbps = int(rate // 1000)
    return '%s Kbps%s' % (kbps, vbr)
