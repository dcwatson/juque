from django import template

register = template.Library()

@register.filter
def track_length(length, words=False):
    mins = int(length // 60)
    secs = int(length - (mins * 60))
    hours = int(mins // 60)
    if hours > 0:
        mins -= hours * 60
    days = int(hours // 24)
    if days > 0:
        hours -= days * 24
    if days:
        if words:
            frac = ((hours * 60 * 60) + (mins * 60) + secs) / 86400.0
            return '%.1f days' % (days + frac)
        else:
            return '%d:%02d:%02d:%02d' % (days, hours, mins, secs)
    elif hours:
        if words:
            frac = ((mins * 60) + secs) / 3600.0
            return '%.1f hours' % (hours + frac)
        else:
            return '%d:%02d:%02d' % (hours, mins, secs)
    else:
        if words:
            frac = secs / 60.0
            return '%.1f minutes' % (mins + frac)
        else:
            return '%d:%02d' % (mins, secs)

@register.filter
def bitrate(rate):
    vbr = ' (VBR)' if rate % 1000 != 0 else ''
    kbps = int(rate // 1000)
    return '%s Kbps%s' % (kbps, vbr)
