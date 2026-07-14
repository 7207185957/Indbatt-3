from django import forms

from .models import Personnel


class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = [
            'army_number', 'rank', 'full_name', 'company', 'platoon', 'section',
            'appointment', 'date_of_joining_unit', 'status', 'remarks', 'is_active',
        ]
        widgets = {
            'date_of_joining_unit': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'
            field.widget.attrs.setdefault('class', css)

    def clean_army_number(self):
        return self.cleaned_data['army_number'].strip().upper()

    def clean(self):
        cleaned_data = super().clean()
        platoon = cleaned_data.get('platoon')
        section = cleaned_data.get('section')
        company = cleaned_data.get('company')
        if platoon and company and platoon.company_id != company.id:
            self.add_error('platoon', 'Selected platoon does not belong to the selected company.')
        if section and platoon and section.platoon_id != platoon.id:
            self.add_error('section', 'Selected section does not belong to the selected platoon.')
        return cleaned_data


class PersonnelSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search (Army No / Name / Rank)')
    company = forms.CharField(required=False, widget=forms.HiddenInput())
    status = forms.CharField(required=False, widget=forms.HiddenInput())
