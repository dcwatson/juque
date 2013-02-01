from django import forms
from django.contrib.auth import authenticate
from bootstrap.widgets import EmailWidget, PasswordWidget

class LoginForm (forms.Form):
    email = forms.EmailField(label='Email Address', widget=EmailWidget)
    password = forms.CharField(widget=PasswordWidget)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        email = self.cleaned_data.get('email', '')
        password = self.cleaned_data.get('password', '')
        self.user = authenticate(username=email, password=password)
        if not self.user:
            raise forms.ValidationError('The email address or password you entered is incorrect.')
        return self.cleaned_data
