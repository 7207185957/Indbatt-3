from django import forms

from .models import DutyRoster


class DutyRosterForm(forms.ModelForm):
    class Meta:
        model = DutyRoster
        fields = [
            'duty_date', 'duty_type', 'company', 'personnel_detailed',
            'duty_location', 'shift_time', 'remarks', 'status',
        ]
        widgets = {
            'duty_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
            'personnel_detailed': forms.SelectMultiple(attrs={'size': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else 'form-control'
            field.widget.attrs.setdefault('class', css)
        self.fields['personnel_detailed'].queryset = self.fields['personnel_detailed'].queryset.filter(is_active=True)

    def clean_personnel_detailed(self):
        personnel = self.cleaned_data.get('personnel_detailed')
        if not personnel:
            raise forms.ValidationError('At least one person must be detailed for this duty.')
        return personnel
