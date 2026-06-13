from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Child, Vaccination, HealthCheck, HealthCheckSchedule, create_health_check_schedule
from .forms import ChildForm, VaccinationForm, HealthCheckForm
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime

# logowanie
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('child_list')
    else:
        form = AuthenticationForm()
    return render(request, 'medical_record/login.html', {'form': form})

# wylogowanie
def logout_view(request):
    logout(request)
    return redirect('login')

# rejestracja
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('child_list')
    else:
        form = UserCreationForm()
    return render(request, 'medical_record/register.html', {'form': form})

# lista wszystkich dzieci
@login_required(login_url='login')
def child_list(request):
    children = Child.objects.filter(owner=request.user)
    return render(request, 'medical_record/child_list.html', {'children': children})

# jedno dziecka
@login_required(login_url='login')
def child_detail(request, pk):
    child = Child.objects.get(id=pk)
    vaccinations = child.vaccinations.all()
    health_checks = child.health_checks.all()
    schedule = child.schedule.all().order_by('age_months')
    
    context = {
        'child': child,
        'vaccinations': vaccinations,
        'health_checks': health_checks,
        'schedule': schedule
    }
    return render(request, 'medical_record/child_detail.html', context)

# dodawanie dziecka
@login_required(login_url='login')
def add_child(request):
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.owner = request.user
            child.save()
            create_health_check_schedule(child)
            return redirect('child_list')
    else:
        form = ChildForm()
    return render(request, 'medical_record/add_child.html', {'form': form})

# edycja dziecka
@login_required(login_url='login')
def edit_child(request, pk):
    child = Child.objects.get(id=pk)
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            from dateutil.relativedelta import relativedelta
            schedule_items = child.schedule.all()
            for item in schedule_items:
                item.due_date = child.birth_date + relativedelta(months=item.age_months)
                item.save()
            return redirect('child_detail', pk=pk)
    else:
        form = ChildForm(instance=child)
    return render(request, 'medical_record/edit_child.html', {'form': form, 'child': child})

# usuwanie dziecka
@login_required(login_url='login')
def delete_child(request, pk):
    child = Child.objects.get(id=pk)
    child.delete()
    return redirect('child_list')

# dodawanie bilansu zdrowia
@login_required(login_url='login')
def add_health_check(request, pk):
    child = Child.objects.get(id=pk)
    schedule_pk = request.GET.get('schedule')
    
    if request.method == "POST":
        form = HealthCheckForm(request.POST)
        if form.is_valid():
            health_check = form.save(commit=False)
            health_check.child = child
            health_check.save()
            
            if schedule_pk:
                try:
                    schedule_item = HealthCheckSchedule.objects.get(pk=schedule_pk)
                    schedule_item.health_check = health_check
                    schedule_item.is_done = True
                    schedule_item.save()
                except HealthCheckSchedule.DoesNotExist:
                    pass
            
            return redirect('child_detail', pk=pk)
    else:
        form = HealthCheckForm()
    return render(request, 'medical_record/add_health_check.html', {'form': form, 'child': child})

# edycja bilansu zdrowia
@login_required(login_url='login')
def edit_health_check(request, pk):
    health_check = HealthCheck.objects.get(id=pk)
    child = health_check.child
    if request.method == "POST":
        form = HealthCheckForm(request.POST, instance=health_check)
        if form.is_valid():
            form.save()
            return redirect('child_detail', pk=child.pk)
    else:
        form = HealthCheckForm(instance=health_check)
    return render(request, 'medical_record/edit_health_check.html', {'form': form, 'child': child, 'health_check': health_check})

# podgląd bilansu
@login_required(login_url='login')
def health_check_detail(request, pk):
    health_check = HealthCheck.objects.get(id=pk)
    child = health_check.child
    return render(request, 'medical_record/health_check_detail.html', {'health_check': health_check, 'child': child})

# lista wszystkich bilansów zdrowia z paginacją
@login_required(login_url='login')
def health_check_list(request):
    health_checks = HealthCheckSchedule.objects.filter(
    child=child
).order_by('age_months')

    per_page = int(request.GET.get('per_page', 5))
    page_number = request.GET.get('page', 1)

    paginator = Paginator(health_checks, per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'medical_record/health_check_list.html', {
        'page_obj': page_obj,
        'per_page': per_page,
    })

# lista bilansów konkretnego dziecka z paginacją
@login_required(login_url='login')
def child_health_check_list(request, pk):
    child = Child.objects.get(id=pk, owner=request.user)

    health_checks = HealthCheckSchedule.objects.filter(child=child).order_by('age_months')

    status_filter = request.GET.get('status', '')
    min_age_filter = request.GET.get('min_age', '')

    if status_filter == 'done':
        health_checks = health_checks.filter(is_done=True)
    elif status_filter == 'pending':
        health_checks = health_checks.filter(is_done=False)

    if min_age_filter.isdigit():
        health_checks = health_checks.filter(age_months__gte=int(min_age_filter))

    per_page = int(request.GET.get('per_page', 5))
    page_number = request.GET.get('page', 1)

    paginator = Paginator(health_checks, per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'medical_record/child_health_check_list.html', {
        'child': child,
        'page_obj': page_obj,
        'per_page': per_page,
        'status_filter': status_filter, 
        'min_age_filter': min_age_filter,
    })

# eksportowanie bilansów do pliku CSV 
@login_required(login_url='login')
def export_health_checks_csv(request, pk):
    child = Child.objects.get(id=pk, owner=request.user)
    health_checks = HealthCheckSchedule.objects.filter(child=child).order_by('age_months')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="bilanse_dziecka_{child.id}.csv"'

    writer = csv.writer(response, delimiter=';')

    writer.writerow(['Data harmonogramu', 'Wiek (miesiace)', 'Wykonano', 'Waga (kg)', 'Wzrost (cm)'])

    for item in health_checks:
        weight = item.health_check.weight if item.health_check else 'Brak danych'
        height = item.health_check.height if item.health_check else 'Brak danych'
        status = 'Tak' if item.is_done else 'Nie'
        
        writer.writerow([item.due_date, item.age_months, status, weight, height])

    return response

# generowanie wykresu 
@login_required(login_url='login')
def child_weight_chart(request, pk):
    child = Child.objects.get(id=pk, owner=request.user)
    health_checks = HealthCheckSchedule.objects.filter(
        child=child, 
        is_done=True, 
        health_check__isnull=False
    ).order_by('age_months')

    ages = []
    weights = []

    for item in health_checks:
        if item.health_check.weight:
            ages.append(item.age_months)
            weights.append(float(item.health_check.weight))

    plt.figure(figsize=(8, 4))
    if ages and weights:
        plt.plot(ages, weights, marker='o', linestyle='-', color='g')
        plt.title(f'Wykres wagi {child.name}')
        plt.xlabel('Wiek (miesiące)')
        plt.ylabel('Waga (kg)')
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, 'Brak danych z wagi do wygenerowania wykresu', 
                 horizontalalignment='center', verticalalignment='center')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')

# dodawanie szczepienia
@login_required(login_url='login')
def add_vaccination(request, pk):
    child = Child.objects.get(id=pk, owner=request.user)
    if request.method == "POST":
        form = VaccinationForm(request.POST)
        if form.is_valid():
            vaccination = form.save(commit=False)
            vaccination.child = child
            vaccination.save()
            return redirect('child_detail', pk=child.pk)
    else:
        form = VaccinationForm()
    return render(request, 'medical_record/add_vaccination.html', {'form': form, 'child': child})

# importowanie szczepień z pliku CSV z zapisem do bazy 
@login_required(login_url='login')
def import_medical_data(request, pk):
    child = Child.objects.get(id=pk, owner=request.user)
    extracted_data = []
    error_message = None

    if request.method == 'POST':
        uploaded_file = request.FILES.get('data_file')
        if uploaded_file:
            if not uploaded_file.name.endswith('.csv'):
                error_message = "Dozwolone są tylko pliki .csv!"
            else:
                try:
                    decoded_file = uploaded_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(decoded_file, delimiter=';')
                    
                    for row in reader:
                        if len(row) >= 3:
                            v_name = row[0].strip()
                            v_date_str = row[1].strip()
                            v_status_str = row[2].strip().lower()

                            v_date = datetime.strptime(v_date_str, '%Y-%m-%d').date()
                            v_status = True if v_status_str in ['tak', 'true', '1'] else False
                            
                            Vaccination.objects.create(
                                child=child,
                                vaccine_name=v_name,
                                date=v_date,
                                status=v_status
                            )
                            extracted_data.append(f"Zapisano do bazy: {v_name} z datą {v_date}")
                except Exception as e:
                    error_message = f"Błąd odczytu pliku. Wzór linijki to: WZW B;2023-01-15;Tak. Szczegóły: {str(e)}"
        else:
            error_message = "Nie wybrano żadnego pliku."

    return render(request, 'medical_record/import_data.html', {
        'child': child,
        'extracted_data': extracted_data,
        'error_message': error_message
    })