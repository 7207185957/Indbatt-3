from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UnitUserCreationForm(UserCreationForm):
    """Used by Super Admin to create a new, individually-attributable login."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'rank', 'service_number',
            'role', 'company', 'contact_number', 'email',
        )
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['role'].widget.attrs['class'] = 'form-select'
        self.fields['company'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company = cleaned_data.get('company')
        if role == 'CLERK' and not company:
            self.add_error('company', 'A Company Clerk account must be assigned to a Company/sub-unit.')
        return cleaned_data


class UnitUserChangeForm(forms.ModelForm):
    """Used by Super Admin to edit an existing account (no password change here)."""

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'rank', 'service_number',
            'role', 'company', 'contact_number', 'email', 'is_active', 'is_staff',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('is_active', 'is_staff'):
                field.widget.attrs.setdefault('class', 'form-control')
        self.fields['role'].widget.attrs['class'] = 'form-select'
        self.fields['company'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company = cleaned_data.get('company')
        if role == 'CLERK' and not company:
            self.add_error('company', 'A Company Clerk account must be assigned to a Company/sub-unit.')
        return cleaned_data
