from django import forms
from .models import Child, Vaccination, HealthCheck
from django.core.exceptions import ValidationError

def validate_pesel(value):
    if value and len(value) != 11:
        raise ValidationError("PESEL musi mieć dokładnie 11 cyfr.")
    if value and not value.isdigit():
        raise ValidationError("PESEL może zawierać tylko cyfry.")
    if value:
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        checksum = sum(int(value[i]) * weights[i] for i in range(10))
        control = (10 - (checksum % 10)) % 10
        if control != int(value[10]):
            raise ValidationError("Podany PESEL jest nieprawidłowy.")

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'birth_date', 'blood_group', 'pesel']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz imię dziecka'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. A+, B-, 0+'}),
            'pesel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz PESEL dziecka', 'maxlength': '11'}),
        }

    def clean_pesel(self):
        pesel = self.cleaned_data.get('pesel')
        validate_pesel(pesel)
        return pesel

        
class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['vaccine_name', 'date', 'status']

class HealthCheckForm(forms.ModelForm):
    class Meta:
        model = HealthCheck
        fields = ['date', 'weight', 'height', 'notes']