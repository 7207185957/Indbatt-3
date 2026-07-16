from django import forms

from .models import DailyStrength


class DailyStrengthForm(forms.ModelForm):
    class Meta:
        model = DailyStrength
        fields = [
            'date', 'company', 'total_posted_strength', 'present', 'leave',
            'temporary_duty', 'course', 'hospital_sick', 'attached_out',
            'other_absence', 'remarks',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css)

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get('company')
        date = cleaned_data.get('date')
        if company and date:
            qs = DailyStrength.objects.filter(company=company, date=date)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('date', 'A strength entry for this company and date already exists.')

        total = cleaned_data.get('total_posted_strength') or 0
        present = cleaned_data.get('present') or 0
        leave = cleaned_data.get('leave') or 0
        td = cleaned_data.get('temporary_duty') or 0
        course = cleaned_data.get('course') or 0
        hospital = cleaned_data.get('hospital_sick') or 0
        attached_out = cleaned_data.get('attached_out') or 0
        other = cleaned_data.get('other_absence') or 0
        accounted = present + leave + td + course + hospital + attached_out + other
        if total and accounted != total:
            self.add_error(
                None,
                f"Present + all absence categories ({accounted}) does not match Total posted strength ({total}). "
                'Please verify the figures.',
            )
        return cleaned_data
