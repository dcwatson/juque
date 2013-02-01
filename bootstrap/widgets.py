from django import forms
from django.template import loader, Context

class BootstrapWidget (forms.Widget):
    def render(self, name, value, attrs=None):
        template_choices = [
            'bootstrap/widgets/%s.html' % self.__class__.__name__.lower(),
            'bootstrap/widgets/widget.html',
        ]
        template = loader.select_template(template_choices)
        context = Context({
            'name': name,
            'value': value,
            'attrs': attrs,
        })
        return template.render(context)

class EmailWidget (BootstrapWidget):
    pass

class PasswordWidget (BootstrapWidget):
    pass
