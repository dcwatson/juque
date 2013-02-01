from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login, logout as django_logout
from juque.core.forms import LoginForm

def home(request):
    return redirect('library')

def login(request):
    next = request.REQUEST.get('next', 'library').strip()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            django_login(request, form.user)
            return redirect(next)
    else:
        form = LoginForm()
    return render(request, 'login.html', {
        'form': form,
        'next': next,
    })

def logout(request):
    django_logout(request)
    return redirect('login')
