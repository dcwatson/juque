from django import template

register = template.Library()

@register.inclusion_tag('bootstrap/form.html')
def bootstrap_form(form):
    return {'form': form}

@register.inclusion_tag('bootstrap/field.html')
def bootstrap_field(field):
    return {'field': field}
