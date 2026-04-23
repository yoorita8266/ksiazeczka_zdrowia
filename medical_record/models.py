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

class HealthCheckSchedule(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='schedule')
    age_months = models.IntegerField(verbose_name="Wiek w miesiącach")
    due_date = models.DateField(verbose_name="Planowana data")
    is_done = models.BooleanField(default=False, verbose_name="Czy wykonano?")
    health_check = models.ForeignKey(HealthCheck, null=True, blank=True, on_delete=models.SET_NULL, related_name='schedule')

    def __str__(self):
        return f"Bilans {self.age_months} mies. - {self.child.name}"

from dateutil.relativedelta import relativedelta

HEALTH_CHECK_AGES = [1, 2, 4, 6, 9, 12, 18, 24, 36, 48, 60, 72, 120, 156, 192, 216]

def create_health_check_schedule(child):
    for age in HEALTH_CHECK_AGES:
        due_date = child.birth_date + relativedelta(months=age)
        HealthCheckSchedule.objects.create(
            child=child,
            age_months=age,
            due_date=due_date
        )