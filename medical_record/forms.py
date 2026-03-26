from django import forms
from .models import Child, Vaccination, HealthCheck

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = '__all__' 

class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = '__all__'

class HealthCheckForm(forms.ModelForm):
    class Meta:
        model = HealthCheck
        fields = '__all__'