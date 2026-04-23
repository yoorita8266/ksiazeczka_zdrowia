from django import forms
from .models import Child, Vaccination, HealthCheck

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = '__all__'

class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['vaccine_name', 'date', 'status']

class HealthCheckForm(forms.ModelForm):
    class Meta:
        model = HealthCheck
        fields = ['date', 'weight', 'height', 'notes']
