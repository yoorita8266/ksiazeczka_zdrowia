from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = [
    ('M', 'Chłopiec'),
    ('F', 'Dziewczynka'),
]

class Child(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Właściciel", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Imię dziecka")
    birth_date = models.DateField(verbose_name="Data urodzenia")
    blood_group = models.CharField(max_length=10, verbose_name="Grupa krwi", blank=True)
    pesel = models.CharField(max_length=11, verbose_name="PESEL", unique=True, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Płeć", blank=True)

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
    
    # Pomiary
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Masa ciała (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Wzrost (cm)")
    head_circumference = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Obwód głowy (cm)")
    blood_pressure = models.CharField(max_length=20, blank=True, verbose_name="Ciśnienie tętnicze")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Wskaźnik BMI")
    
    # Badanie lekarskie
    skin = models.CharField(max_length=200, blank=True, verbose_name="Skóra")
    head = models.CharField(max_length=200, blank=True, verbose_name="Głowa")
    neck = models.CharField(max_length=200, blank=True, verbose_name="Szyja")
    eyes = models.CharField(max_length=200, blank=True, verbose_name="Oczy")
    ears = models.CharField(max_length=200, blank=True, verbose_name="Uszy")
    mouth = models.CharField(max_length=200, blank=True, verbose_name="Jama ustna/gardło")
    lymph_nodes = models.CharField(max_length=200, blank=True, verbose_name="Węzły chłonne")
    lungs = models.CharField(max_length=200, blank=True, verbose_name="Płuca")
    heart = models.CharField(max_length=200, blank=True, verbose_name="Serce")
    abdomen = models.CharField(max_length=200, blank=True, verbose_name="Brzuch")
    urogenital = models.CharField(max_length=200, blank=True, verbose_name="Układ moczowo-płciowy")
    musculoskeletal = models.CharField(max_length=200, blank=True, verbose_name="Układ kostno-stawowy")
    nutrition_status = models.CharField(max_length=200, blank=True, verbose_name="Stan odżywienia")
    
    # Zaburzenia
    vision = models.CharField(max_length=50, blank=True, verbose_name="Zaburzenia wzroku")
    hearing = models.CharField(max_length=50, blank=True, verbose_name="Zaburzenia słuchu")
    
    # Zalecenia
    recommendations = models.TextField(blank=True, verbose_name="Zalecenia")
    diet = models.TextField(blank=True, verbose_name="Dieta/Witaminy")
    diagnostic_tests = models.TextField(blank=True, verbose_name="Zlecone badania diagnostyczne")
    consultations = models.TextField(blank=True, verbose_name="Zlecone konsultacje")
    health_problems = models.TextField(blank=True, verbose_name="Problemy zdrowotne")
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