from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Child, Vaccination, HealthCheck, HealthCheckSchedule, create_health_check_schedule
from .forms import ChildForm, VaccinationForm, HealthCheckForm

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