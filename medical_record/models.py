from django.db import models

class Child(models.Model):
    name = models.CharField(max_length=100, verbose_name="Imię dziecka")
    birth_date = models.DateField(verbose_name="Data urodzenia")
    blood_group = models.CharField(max_length=10, verbose_name="Grupa krwi", blank=True)

    def __str__(self):
        return self.name

class Vaccination(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='vaccinations', verbose_name="Dziecko")
    vaccine_name = models.CharField(max_length=200, verbose_name="Nazwa szczepionki")
    date = models.DateField(verbose_name="Data szczepienia")
    status = models.BooleanField(default=False, verbose_name="Czy wykonano?")

    def __str__(self):
        return f"{self.vaccine_name} - {self.child.name}"

class HealthCheck(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='health_checks', verbose_name="Dziecko")
    date = models.DateField(verbose_name="Data bilansu")
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Waga (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Wzrost (cm)")
    notes = models.TextField(blank=True, verbose_name="Uwagi lekarskie")

    def __str__(self):
        return f"Bilans {self.child.name} z dnia {self.date}"