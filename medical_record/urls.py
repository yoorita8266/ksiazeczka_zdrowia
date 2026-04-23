from django.urls import path
from . import views

urlpatterns = [
    path('', views.child_list, name='child_list'),
    path('child/<int:pk>/', views.child_detail, name='child_detail'),
    path('add/', views.add_child, name='add_child'),
    path('child/<int:pk>/add_health_check/', views.add_health_check, name='add_health_check'),
    path('health_check/<int:pk>/edit/', views.edit_health_check, name='edit_health_check'),
    path('child/<int:pk>/edit/', views.edit_child, name='edit_child'),
    path('health_check/<int:pk>/', views.health_check_detail, name='health_check_detail'),
]
