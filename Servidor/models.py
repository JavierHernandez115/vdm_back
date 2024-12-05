from django.db import models
from decimal import Decimal
# Create your models here.
class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    fecha_entrada = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Empleado: {self.nombre}"

class Asistencia(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField()
    asistencia = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Vacacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    dias_restantes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VacacionTomada(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_tomados = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Salario(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    sueldo_semanal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Prestamo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    monto_prestamo = models.DecimalField(max_digits=10, decimal_places=2)
    deuda_restante = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    abono_semanal = models.DecimalField(max_digits=10, decimal_places=2)
    razon = models.TextField()
    fecha_prestamo = models.DateField()
    estatus = models.BooleanField(default=True)  # Indica si el préstamo sigue vigente
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Solo inicializar deuda_restante al monto_prestamo al crear un nuevo préstamo
        if not self.pk and self.deuda_restante == 0.00:  # Si no existe en la BD (nuevo préstamo)
            self.deuda_restante = self.monto_prestamo
        super().save(*args, **kwargs)

class Abono(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE)
    monto_abono = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_abono = models.DateField()
    deuda_restante = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))  # Nuevo campo

from django.db import models
from django.contrib.postgres.fields import JSONField  # Para PostgreSQL, o usa TextField para otros

class Pago(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    monto_a_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    detalle = models.JSONField(default=list)  # Contiene el desglose del pago
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
