import logging

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from notes.models import Note

from .forms import ProfileForm

security_logger = logging.getLogger('security')


def register_view(request):
    ###################################################################
    # FLAW 4 -- Identification and Authentication Failures
    #           Weak password requirements
    #
    # The VULNERABLE version accepts any password at all for example "1" is fine.
    # Note that User.objects.create_user() does not run Django's password
    # validators by itself; validators only run if the code calls them.
    # So the fix is to call validate_password() before creating the user,
    # which enforces the AUTH_PASSWORD_VALIDATORS policy from settings.py
    # (minimum length, not a common password, not all numeric, not too
    # similar to the username).
    #
    # To repair the app: comment out the VULNERABLE block and uncomment
    # the SECURE block.
    ###################################################################
    
    errors = []

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        User = get_user_model()

        if not username or not password:
            errors.append('Username and password are required.')
        elif User.objects.filter(username=username).exists():
            errors.append('That username is already taken.')
        else:
            # --- SECURE version: enforce the password policy before the
            # --- account is created.
            #try:
            #    validate_password(password)
            #except ValidationError as e:
            #    errors.extend(e.messages)

            # --- VULNERABLE version: no password policy is enforced, so
            # --- trivial passwords such as "1" are accepted.
            if not errors:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                )
                login(request, user)
                return redirect('home')

    return render(request, 'accounts/register.html', {'errors': errors})


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

        ###############################################################
        # FLAW 5 -- Security Logging and Monitoring
        #           Failures. Insufficient Logging
        #
        # A failed login is a security-relevant, auditable event. Here
        # it is silently discarded: nothing is written to the security
        # log, so an attacker can guess passwords indefinitely and leave
        # no trace for anyone to detect or investigate.
        #
        # To repair the app: uncomment the SECURE line below so every
        # failed attempt is logged with the username and source IP.
        ###############################################################

        # --- SECURE version: record the failed attempt (audit trail).
        security_logger.warning(
            'Failed login attempt for username=%r from IP %s',
            username, request.META.get('REMOTE_ADDR'),
        )

        # --- VULNERABLE version: (nothing is logged.)

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
