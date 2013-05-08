from django import forms
from django.db import models
from django.core.urlresolvers import reverse
from bootstrap.forms import BootstrapModelForm
from juque.library.models import Track

class TrackForm (BootstrapModelForm):
    track_number = forms.IntegerField(widget=forms.TextInput({'size': 2}))

    class Meta:
        model = Track
        exclude = ('owner',)

class CommonForm (forms.Form):
    def set_field_value(self, obj, field, value, model_class):
        if '__' in field:
            # TODO: follow more than one __ relation.
            rel_field, field_name = field.rsplit('__', 1)
            try:
                q = {str(field_name): value}
                related_obj = model_class.objects.get(**q)
            except:
                related_obj = model_class.objects.create(**q)
            setattr(obj, rel_field, related_obj)
        else:
            setattr(obj, field, value)

    def save(self, commit=True):
        for obj in self.queryset:
            changed = False
            for field, value in self.cleaned_data.items():
                if value:
                    model_class = self.model_classes.get(field)
                    self.set_field_value(obj, field, value, model_class)
                    changed = True
            if changed and commit:
                obj.save()

def common_form_factory(queryset, fields, form=CommonForm):
    field_values = {}
    # First, get all unique values for each field requested.
    for obj in queryset:
        for field_name, field_label, model_class in fields:
            value = obj
            for attr_name in field_name.split('__'):
                value = getattr(value, attr_name, None)
            if field_name not in field_values:
                field_values[field_name] = set()
            field_values[field_name].add(value)
    # Now, build the form.
    form_fields = {
        'queryset': queryset,
        'model_classes': {},
    }
    for field_name, field_label, model_class in fields:
        meta = queryset.model._meta
        field = None
        for attr_name in field_name.split('__'):
            field = meta.get_field(attr_name)
            if isinstance(field, models.ForeignKey):
                meta = field.rel.to._meta
        # Only set an initial value if it's common to all the objects.
        all_values = list([v for v in field_values[field_name] if v])
        initial = all_values[0] if len(all_values) == 1 else None
        widget = forms.TextInput(attrs={
            'class': 'input-block-level track-typeahead',
            'data-typeahead-url': reverse('ajax-autocomplete'),
        })
        form_fields[field_name] = field.formfield(label=field_label, initial=initial, required=False, widget=widget)
        form_fields['model_classes'][field_name] = model_class
    return type('%sCommonForm' % queryset.model.__name__, (form,), form_fields)
