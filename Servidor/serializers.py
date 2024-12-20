from rest_framework import serializers
from .models import Empleado, Asistencia, Vacacion, VacacionTomada, Salario, Prestamo, Abono, Pago

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'

class AsistenciaSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    empleado=serializers.PrimaryKeyRelatedField(queryset=Empleado.objects.all())
    class Meta:
        model = Asistencia
        fields = '__all__'

class VacacionSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    class Meta:
        model = Vacacion
        fields = '__all__'

class VacacionTomadaSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    class Meta:
        model = VacacionTomada
        fields = '__all__'

class SalarioSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    class Meta:
        model = Salario
        fields = '__all__'

class PrestamoSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    class Meta:

        model = Prestamo
        fields = '__all__'

class AbonoSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    razon_prestamo = serializers.CharField(source='prestamo.razon', read_only=True)  # Agrega la razón del préstamo
    class Meta:
        model = Abono
        fields = '__all__'
        extra_fields = ['razon_prestamo']

class PagoSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    detalle = serializers.JSONField()
    class Meta:
        model = Pago
        fields = '__all__'
