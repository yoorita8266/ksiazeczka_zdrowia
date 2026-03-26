from django.urls import path
from . import views

urlpatterns = [
    path('', views.child_list, name='child_list'),
    path('child/<int:pk>/', views.child_detail, name='child_detail'),
    path('add/', views.add_child, name='add_child'),
]