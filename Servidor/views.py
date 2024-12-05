# Servidor/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
from .models import Empleado, Asistencia, Vacacion, VacacionTomada, Salario, Prestamo, Abono, Pago
from .serializers import (
    EmpleadoSerializer, AsistenciaSerializer, VacacionSerializer, VacacionTomadaSerializer,
    SalarioSerializer, PrestamoSerializer, AbonoSerializer, PagoSerializer
)
from django.shortcuts import get_object_or_404

#Pagos por fechas
@api_view(['GET'])
def pagos_por_fecha(request, fecha):
    """
    Filtra los pagos por una fecha proporcionada en la URL y los serializa.
    """
    try:
        fecha_parsed = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Formato de fecha inválido. Use 'YYYY-MM-DD'."}, status=400)

    pagos = Pago.objects.filter(fecha_pago=fecha_parsed).order_by('id')
    serializer = PagoSerializer(pagos, many=True)

    return Response({
        "fecha": str(fecha_parsed),
        "pagos": serializer.data
    })


    # Convertir el defaultdict a un diccionario estándar
    data = {str(fecha): pagos for fecha, pagos in pagos_agrupados.items()}
    return JsonResponse(data)


#Generar Pago
@api_view(['POST'])
# Función para registrar pago
def registrar_pago(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return Response({"error": "Empleado no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Obtener el salario semanal del empleado
    try:
        salario = empleado.salario_set.latest('created_at')  # Asumiendo que hay un salario activo
    except Salario.DoesNotExist:
        return Response({"error": "No se encontró salario registrado para el empleado."}, status=status.HTTP_404_NOT_FOUND)

    # Calcular faltas (de miércoles a lunes) excluyendo el martes como día de descanso
    fecha_fin = date.today() - timedelta(days=1)  # Día anterior al pago (lunes)
    fecha_inicio = fecha_fin - timedelta(days=4)  # Miércoles anterior
    asistencias = Asistencia.objects.filter(empleado=empleado, fecha__range=(fecha_inicio, fecha_fin)).exclude(
        fecha__week_day=3  # Excluir martes (día 3 en datetime.weekday)
    )
    faltas = asistencias.filter(asistencia=False).count()
    descuento_por_faltas = faltas * (salario.sueldo_semanal / Decimal(6))  # Sueldo dividido por 6 días laborables

    # Calcular abonos a préstamos
    prestamos_activos = Prestamo.objects.filter(empleado=empleado, estatus='True')
    total_abonos = Decimal(0)
    detalle_prestamos = []
    for prestamo in prestamos_activos:
        abono = prestamo.abono_semanal

        if prestamo.deuda_restante <= abono:
            abono = prestamo.deuda_restante  # Ajustar abono si es mayor a la deuda restante
            prestamo.deuda_restante = Decimal(0)  # La deuda queda saldada
            prestamo.estatus = 'False'  # Cambiar estado a saldado
        else:
            prestamo.deuda_restante -= abono  # Reducir deuda restante

        # Guardar cambios en el préstamo
        prestamo.save()

        # Crear registro de abono con la deuda restante actualizada
        Abono.objects.create(
            prestamo=prestamo,
            empleado=empleado,
            monto_abono=abono,
            fecha_abono=date.today(),
            deuda_restante=prestamo.deuda_restante  # Usar el valor actual de deuda restante
        )

        # Registrar detalle para reporte
        total_abonos += abono
        detalle_prestamos.append({
            "prestamo_id": prestamo.id,
            "monto_abonado": str(abono),
            "monto_restante": str(prestamo.deuda_restante),
            "razon": prestamo.razon
        })

    # Calcular monto total del pago
    monto_a_pagar = salario.sueldo_semanal - descuento_por_faltas - total_abonos

    # Generar desglose
    detalle = {
        "faltas": {
            "dias_faltados": faltas,
            "descuento": str(descuento_por_faltas)
        },
        "prestamos": detalle_prestamos,
        "total_abonos": str(total_abonos),
        "sueldo_base": str(salario.sueldo_semanal),
        "total_pagado": str(monto_a_pagar)
    }

    # Guardar el pago
    pago = Pago.objects.create(
        empleado=empleado,
        monto_a_pagar=monto_a_pagar,
        fecha_pago=date.today(),
        detalle=detalle
    )

    return Response({
        "mensaje": "Pago registrado correctamente.",
        "pago": {
            "id": pago.id,
            "monto_a_pagar": pago.monto_a_pagar,
            "detalle": pago.detalle,
            "fecha_pago": pago.fecha_pago
        }
    }, status=status.HTTP_201_CREATED)



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
