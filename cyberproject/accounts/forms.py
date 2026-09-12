from django import forms
from django.contrib.auth import get_user_model


class ProfileForm(forms.ModelForm):
    """Explicit allowlist of the fields a user may edit on their own account.

    Anything else posted to the profile view (is_staff, is_superuser, ...)
    is ignored, because a ModelForm only ever writes the fields listed here.
    """

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
