from django.shortcuts import render, redirect
from .models import Child, Vaccination, HealthCheck, HealthCheckSchedule, create_health_check_schedule
from .forms import ChildForm, VaccinationForm, HealthCheckForm

# lista wszystkich dzieci
def child_list(request):
    children = Child.objects.all()
    return render(request, 'medical_record/child_list.html', {'children': children})

# jedno dziecka
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
def add_child(request):
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save()
            create_health_check_schedule(child)
            return redirect('child_list')
    else:
        form = ChildForm()
    return render(request, 'medical_record/add_child.html', {'form': form})

# edycja dziecka
def edit_child(request, pk):
    child = Child.objects.get(id=pk)
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            # przelicz daty w harmonogramie
            from dateutil.relativedelta import relativedelta
            schedule_items = child.schedule.all()
            for item in schedule_items:
                item.due_date = child.birth_date + relativedelta(months=item.age_months)
                item.save()
            return redirect('child_detail', pk=pk)
    else:
        form = ChildForm(instance=child)
    return render(request, 'medical_record/edit_child.html', {'form': form, 'child': child})

# dodawanie bilansu zdrowia
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
def health_check_detail(request, pk):
    health_check = HealthCheck.objects.get(id=pk)
    child = health_check.child
    return render(request, 'medical_record/health_check_detail.html', {'health_check': health_check, 'child': child})