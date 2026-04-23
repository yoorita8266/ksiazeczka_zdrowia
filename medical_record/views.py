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
            
            # powiąż z harmonogramem jeśli podano
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