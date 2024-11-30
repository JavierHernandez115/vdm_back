from django.urls import path, include
from . import views

urlpatterns = [
    # CRUD para Empleados
    path('empleados/', views.empleado_list, name='empleado-list'),
    path('empleados/<int:pk>/', views.empleado_detail, name='empleado-detail'),

    # CRUD para Asistencias
    path('asistencias/', views.asistencia_list, name='asistencia-list'),
    path('asistencias/<int:pk>/', views.asistencia_detail, name='asistencia-detail'),

    # CRUD para Vacaciones
    path('vacaciones/', views.vacacion_list, name='vacacion-list'),
    path('vacaciones/<int:pk>/', views.vacacion_detail, name='vacacion-detail'),

    # CRUD para Vacaciones Tomadas
    path('vacaciones_tomadas/', views.vacacion_tomada_list, name='vacacion-tomada-list'),
    path('vacaciones_tomadas/<int:pk>/', views.vacacion_tomada_detail, name='vacacion-tomada-detail'),

    # CRUD para Salarios
    path('salarios/', views.salario_list, name='salario-list'),
    path('salarios/<int:pk>/', views.salario_detail, name='salario-detail'),

    # CRUD para Préstamos
    path('prestamos/', views.prestamo_list, name='prestamo-list'),
    path('prestamos/<int:pk>/', views.prestamo_detail, name='prestamo-detail'),

    # CRUD para Abonos
    path('abonos/', views.abono_list, name='abono-list'),
    path('abonos/<int:pk>/', views.abono_detail, name='abono-detail'),

    # CRUD para Pagos
    path('pagos/', views.pago_list, name='pago-list'),
    path('pagos/<int:pk>/', views.pago_detail, name='pago-detail'),
]
