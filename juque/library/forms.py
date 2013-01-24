from django import forms
from bootstrap.forms import BootstrapModelForm
from juque.library.models import Track

class TrackForm (BootstrapModelForm):
    track_number = forms.IntegerField(widget=forms.TextInput({'size': 2}))

    class Meta:
        model = Track
        exclude = ('owner',)
