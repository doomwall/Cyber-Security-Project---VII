from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from notes.models import Note

from .forms import ProfileForm


def login_view(request):
    error = None

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        error = 'Invalid username or password.'

    return render(request, 'accounts/login.html', {'error': error})


@login_required
def home_view(request):
    return render(request, 'accounts/home.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    """Let a user edit their own profile, and nothing else about it."""
    saved = False

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            saved = True
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'saved': saved,
    })


@login_required
def admin_panel_view(request):
    """Staff-only overview of every user and every note.

    The link to this page is hidden from non-staff in base.html, but that is
    only cosmetic -- the real protection is the is_staff check below, which
    runs before anything is shown.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('403 Forbidden: staff access required.')

    return render(request, 'accounts/admin_panel.html', {
        'users': get_user_model().objects.all().order_by('id'),
        'notes': Note.objects.select_related('owner').all(),
    })
