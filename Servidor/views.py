# Servidor/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Empleado, Asistencia, Vacacion, VacacionTomada, Salario, Prestamo, Abono, Pago
from .serializers import (
    EmpleadoSerializer, AsistenciaSerializer, VacacionSerializer, VacacionTomadaSerializer,
    SalarioSerializer, PrestamoSerializer, AbonoSerializer, PagoSerializer
)
from django.shortcuts import get_object_or_404

#Pagos por empleados
@api_view(['GET'])
def pagos_por_empleado(request,empleado_id):
    try:
        # Verificar que el empleado existe
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return Response(
            {"error": "Empleado no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Filtrar los préstamos relacionados con el empleado
    pagos = Pago.objects.filter(empleado=empleado)
    
    # Serializar los datos
    serializer = PagoSerializer(pagos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#Vacaciones Tomadas por empleado
@api_view(['GET'])
def vacaciones_tomadas_por_empleado(request,empleado_id):
    try:
        # Verificar que el empleado existe
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return Response(
            {"error": "Empleado no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Filtrar los préstamos relacionados con el empleado
    vacaciones_tomadas = VacacionTomada.objects.filter(empleado=empleado)
    
    # Serializar los datos
    serializer = VacacionTomadaSerializer(vacaciones_tomadas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#Abonos de cada empleado
@api_view(['GET'])
def abonos_por_empleado(request,empleado_id):
    try:
        # Verificar que el empleado existe
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return Response(
            {"error": "Empleado no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Filtrar los préstamos relacionados con el empleado
    abonos = Abono.objects.filter(empleado=empleado)
    
    # Serializar los datos
    serializer = AbonoSerializer(abonos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



#Prestamos de cada empleado
@api_view(['GET'])
def prestamos_por_empleado(request, empleado_id):
    try:
        # Verificar que el empleado existe
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return Response(
            {"error": "Empleado no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Filtrar los préstamos relacionados con el empleado
    prestamos = Prestamo.objects.filter(empleado=empleado)
    
    # Serializar los datos
    serializer = PrestamoSerializer(prestamos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#Asistencias por fechas
@api_view(['GET'])
def asistencia_por_fecha(request, fecha):
    try:
        # Convertir la fecha del parámetro a un objeto datetime para mayor seguridad
        fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {"error": "El formato de la fecha debe ser YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Filtrar las asistencias por la fecha específica
    asistencias = Asistencia.objects.filter(fecha=fecha_objeto)
    serializer = AsistenciaSerializer(asistencias, many=True)
    return Response(serializer.data)


# CRUD para Empleados
@api_view(['GET', 'POST'])
def empleado_list(request):
    if request.method == 'GET':
        empleados = Empleado.objects.all()
        serializer = EmpleadoSerializer(empleados, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = EmpleadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def empleado_detail(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'GET':
        serializer = EmpleadoSerializer(empleado)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = EmpleadoSerializer(empleado, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        empleado.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Asistencias
@api_view(['GET', 'POST'])
def asistencia_list(request):
    if request.method == 'GET':
        asistencias = Asistencia.objects.all()
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = AsistenciaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def asistencia_detail(request, pk):
    asistencia = get_object_or_404(Asistencia, pk=pk)
    
    if request.method == 'GET':
        serializer = AsistenciaSerializer(asistencia)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AsistenciaSerializer(asistencia, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        asistencia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Vacaciones
@api_view(['GET', 'POST'])
def vacacion_list(request):
    if request.method == 'GET':
        vacaciones = Vacacion.objects.all()
        serializer = VacacionSerializer(vacaciones, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = VacacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def vacacion_detail(request, pk):
    vacacion = get_object_or_404(Vacacion, pk=pk)
    
    if request.method == 'GET':
        serializer = VacacionSerializer(vacacion)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = VacacionSerializer(vacacion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        vacacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Vacaciones Tomadas
@api_view(['GET', 'POST'])
def vacacion_tomada_list(request):
    if request.method == 'GET':
        vacaciones_tomadas = VacacionTomada.objects.all()
        serializer = VacacionTomadaSerializer(vacaciones_tomadas, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = VacacionTomadaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def vacacion_tomada_detail(request, pk):
    vacacion_tomada = get_object_or_404(VacacionTomada, pk=pk)
    
    if request.method == 'GET':
        serializer = VacacionTomadaSerializer(vacacion_tomada)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = VacacionTomadaSerializer(vacacion_tomada, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        vacacion_tomada.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Salarios
@api_view(['GET', 'POST'])
def salario_list(request):
    if request.method == 'GET':
        salarios = Salario.objects.all()
        serializer = SalarioSerializer(salarios, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = SalarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def salario_detail(request, pk):
    salario = get_object_or_404(Salario, pk=pk)
    
    if request.method == 'GET':
        serializer = SalarioSerializer(salario)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SalarioSerializer(salario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        salario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Préstamos
@api_view(['GET', 'POST'])
def prestamo_list(request):
    if request.method == 'GET':
        prestamos = Prestamo.objects.all()
        serializer = PrestamoSerializer(prestamos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PrestamoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def prestamo_detail(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    
    if request.method == 'GET':
        serializer = PrestamoSerializer(prestamo)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PrestamoSerializer(prestamo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        prestamo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Abonos
@api_view(['GET', 'POST'])
def abono_list(request):
    if request.method == 'GET':
        abonos = Abono.objects.all()
        serializer = AbonoSerializer(abonos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = AbonoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def abono_detail(request, pk):
    abono = get_object_or_404(Abono, pk=pk)
    
    if request.method == 'GET':
        serializer = AbonoSerializer(abono)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AbonoSerializer(abono, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        abono.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD para Pagos
@api_view(['GET', 'POST'])
def pago_list(request):
    if request.method == 'GET':
        pagos = Pago.objects.all()
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PagoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def pago_detail(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    
    if request.method == 'GET':
        serializer = PagoSerializer(pago)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PagoSerializer(pago, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        pago.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
