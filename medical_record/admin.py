from django.contrib import admin

from django.contrib import admin
from .models import Child, Vaccination, HealthCheck

admin.site.register(Child)
admin.site.register(Vaccination)
admin.site.register(HealthCheck)
