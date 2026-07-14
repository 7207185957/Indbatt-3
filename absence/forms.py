from django import forms

from .models import AbsenceRecord


class AbsenceRecordForm(forms.ModelForm):
    class Meta:
        model = AbsenceRecord
        fields = [
            'person', 'type', 'from_date', 'to_date', 'authority_reference',
            'destination', 'status', 'remarks',
        ]
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else 'form-control'
            field.widget.attrs.setdefault('class', css)

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        if from_date and to_date and to_date < from_date:
            self.add_error('to_date', 'To date cannot be earlier than From date.')
        return cleaned_data
