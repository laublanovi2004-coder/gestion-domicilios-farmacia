from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from .models import Cliente, Repartidor, Pedido, HistorialEstados, ReporteEntregas
from django.contrib.auth.models import User

# ✅ FUNCIÓN PARA VERIFICAR SI ES CLIENTE
def es_cliente(user):
    return hasattr(user, 'cliente')

# ✅ FUNCIÓN PARA CREAR REPORTE AUTOMÁTICO
def crear_reporte_entrega(pedido):
    try:
        if ReporteEntregas.objects.filter(pedido=pedido).exists():
            return
        hora_actual = timezone.now().time()
        reporte = ReporteEntregas(
            pedido=pedido,
            repartidor=pedido.repartidor if pedido.repartidor else None,
            fecha_reporte=timezone.now().date(),
            hora_salida=pedido.fecha_asignacion.time() if pedido.fecha_asignacion else hora_actual,
            hora_llegada=hora_actual,
            hora_entrega=hora_actual,
            tiempo_transito=30,
            tiempo_total=pedido.tiempo_real_minutos if pedido.tiempo_real_minutos else 45,
            estado_entrega='exitosa',
            calificacion=5,
            comentarios_cliente='Entrega exitosa'
        )
        reporte.save()
    except Exception as e:
        print(f"Error al crear reporte automático: {str(e)}")

# ✅ VISTAS PÚBLICAS
def registro_cliente(request):
    if request.method == 'POST':
        try:
            # Crear usuario
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe')
                return render(request, 'registration/registro_cliente.html')
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            # Crear cliente
            cliente = Cliente(
                usuario=user,
                cedula=request.POST.get('cedula'),
                nombres=request.POST.get('nombres'),
                apellidos=request.POST.get('apellidos'),
                telefono=request.POST.get('telefono'),
                direccion=request.POST.get('direccion'),
                email=email,
                zona=request.POST.get('zona'),
                discapacidad=request.POST.get('discapacidad') == 'on'
            )
            cliente.save()
            # Autenticar y loguear al usuario
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Registro exitoso! Bienvenido a nuestro sistema.')
                return redirect('cliente_dashboard')
        except Exception as e:
            messages.error(request, f'Error en el registro: {str(e)}')
    return render(request, 'registration/registro_cliente.html')

# ✅ VISTAS PARA CLIENTES
@login_required
@user_passes_test(es_cliente, login_url='/login/')
def cliente_dashboard(request):
    cliente = request.user.cliente
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
    context = {
        'cliente': cliente,
        'pedidos': pedidos,
        'total_pedidos': pedidos.count(),
        'pedidos_pendientes': pedidos.filter(estado='pendiente').count(),
        'pedidos_entregados': pedidos.filter(estado='entregado').count(),
    }
    return render(request, 'clientes/cliente_dashboard.html', context)

@login_required
@user_passes_test(es_cliente, login_url='/login/')
def cliente_crear_pedido(request):
    cliente = request.user.cliente
    if request.method == 'POST':
        try:
            direccion_entrega = request.POST.get('direccion_entrega')
            zona_entrega = request.POST.get('zona_entrega')
            tiempo_estimado_minutos = request.POST.get('tiempo_estimado_minutos')
            observaciones = request.POST.get('observaciones')
            pedido = Pedido(
                cliente=cliente,
                direccion_entrega=direccion_entrega,
                zona_entrega=zona_entrega,
                tiempo_estimado_minutos=tiempo_estimado_minutos,
                observaciones=observaciones
            )
            pedido.save()
            # Registrar estado inicial
            HistorialEstados.objects.create(
                pedido=pedido,
                estado_nuevo='pendiente',
                usuario=request.user.username
            )
            messages.success(request, f'Pedido #{pedido.pedido_id} creado exitosamente!')
            return redirect('cliente_dashboard')
        except Exception as e:
            messages.error(request, f'Error al crear pedido: {str(e)}')
    return render(request, 'clientes/cliente_crear_pedido.html', {'cliente': cliente})

@login_required
@user_passes_test(es_cliente, login_url='/login/')
def cliente_editar_perfil(request):
    cliente = request.user.cliente
    if request.method == 'POST':
        try:
            cliente.nombres = request.POST.get('nombres')
            cliente.apellidos = request.POST.get('apellidos')
            cliente.telefono = request.POST.get('telefono')
            cliente.direccion = request.POST.get('direccion')
            cliente.email = request.POST.get('email')
            cliente.zona = request.POST.get('zona')
            cliente.discapacidad = request.POST.get('discapacidad') == 'on'
            cliente.save()
            # Actualizar usuario
            user = request.user
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Perfil actualizado exitosamente!')
            return redirect('cliente_dashboard')
        except Exception as e:
            messages.error(request, f'Error al actualizar perfil: {str(e)}')
    return render(request, 'clientes/cliente_editar_perfil.html', {'cliente': cliente})

# ✅ VISTAS PRINCIPALES DEL SISTEMA
@login_required
def index(request):
    if hasattr(request.user, 'cliente'):
        return redirect('cliente_dashboard')
    total_clientes = Cliente.objects.count()
    total_repartidores = Repartidor.objects.filter(activo=True).count()
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_recientes = Pedido.objects.select_related('cliente', 'repartidor').order_by('-fecha_pedido')[:5]
    context = {
        'total_clientes': total_clientes,
        'total_repartidores': total_repartidores,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_recientes': pedidos_recientes,
    }
    return render(request, 'index.html', context)

# ✅ VISTAS DE CLIENTES (ADMIN)
@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})

@login_required
def crear_cliente(request):
    if request.method == 'POST':
        try:
            cedula = request.POST.get('cedula')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            email = request.POST.get('email')
            zona = request.POST.get('zona')
            discapacidad = request.POST.get('discapacidad') == 'on'
            if not cedula or not nombres or not apellidos or not telefono or not direccion or not zona:
                messages.error(request, 'Todos los campos marcados con * son requeridos')
                return render(request, 'clientes/form_cliente.html')
            if Cliente.objects.filter(cedula=cedula).exists():
                messages.error(request, 'Ya existe un cliente con esta cédula')
                return render(request, 'clientes/form_cliente.html')
            cliente = Cliente(
                cedula=cedula,
                nombres=nombres,
                apellidos=apellidos,
                telefono=telefono,
                direccion=direccion,
                email=email if email else None,
                zona=zona,
                discapacidad=discapacidad
            )
            cliente.save()
            messages.success(request, f'Cliente {nombres} {apellidos} creado exitosamente!')
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    return render(request, 'clientes/form_cliente.html')

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        try:
            cliente.cedula = request.POST.get('cedula')
            cliente.nombres = request.POST.get('nombres')
            cliente.apellidos = request.POST.get('apellidos')
            cliente.telefono = request.POST.get('telefono')
            cliente.direccion = request.POST.get('direccion')
            cliente.email = request.POST.get('email')
            cliente.zona = request.POST.get('zona')
            cliente.discapacidad = request.POST.get('discapacidad') == 'on'
            cliente.save()
            messages.success(request, f'Cliente {cliente.nombres} actualizado exitosamente!')
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f'Error al actualizar cliente: {str(e)}')
    return render(request, 'clientes/editar_cliente.html', {'cliente': cliente})

@login_required
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        try:
            # Eliminar usuario asociado si existe
            if cliente.usuario:
                cliente.usuario.delete()
            else:
                cliente.delete()
            messages.success(request, 'Cliente eliminado exitosamente!')
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f'Error al eliminar cliente: {str(e)}')
    return render(request, 'clientes/eliminar_cliente.html', {'cliente': cliente})

# ✅ VISTAS DE REPARTIDORES
@login_required
def lista_repartidores(request):
    repartidores = Repartidor.objects.all().order_by('-activo', 'nombres')
    return render(request, 'repartidores/lista_repartidores.html', {'repartidores': repartidores})

@login_required
def crear_repartidor(request):
    if request.method == 'POST':
        try:
            cedula = request.POST.get('cedula')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            telefono = request.POST.get('telefono')
            vehiculo = request.POST.get('vehiculo')
            zona_asignada = request.POST.get('zona_asignada')
            capacidad_entregas = request.POST.get('capacidad_entregas', 5)
            disponible = request.POST.get('disponible') == 'on'
            activo = request.POST.get('activo') == 'on'
            if not cedula or not nombres or not apellidos or not telefono or not zona_asignada:
                messages.error(request, 'Todos los campos marcados con * son requeridos')
                return render(request, 'repartidores/form_repartidor.html')
            if Repartidor.objects.filter(cedula=cedula).exists():
                messages.error(request, 'Ya existe un repartidor con esta cédula')
                return render(request, 'repartidores/form_repartidor.html')
            repartidor = Repartidor(
                cedula=cedula,
                nombres=nombres,
                apellidos=apellidos,
                telefono=telefono,
                vehiculo=vehiculo,
                zona_asignada=zona_asignada,
                capacidad_entregas=capacidad_entregas,
                disponible=disponible,
                activo=activo
            )
            repartidor.save()
            messages.success(request, f'Repartidor {nombres} {apellidos} creado exitosamente!')
            return redirect('lista_repartidores')
        except Exception as e:
            messages.error(request, f'Error al crear repartidor: {str(e)}')
    return render(request, 'repartidores/form_repartidor.html')

@login_required
def editar_repartidor(request, repartidor_id):
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    if request.method == 'POST':
        try:
            repartidor.cedula = request.POST.get('cedula')
            repartidor.nombres = request.POST.get('nombres')
            repartidor.apellidos = request.POST.get('apellidos')
            repartidor.telefono = request.POST.get('telefono')
            repartidor.vehiculo = request.POST.get('vehiculo')
            repartidor.zona_asignada = request.POST.get('zona_asignada')
            repartidor.capacidad_entregas = request.POST.get('capacidad_entregas')
            repartidor.disponible = request.POST.get('disponible') == 'on'
            repartidor.activo = request.POST.get('activo') == 'on'
            repartidor.save()
            messages.success(request, f'Repartidor {repartidor.nombres} actualizado exitosamente!')
            return redirect('lista_repartidores')
        except Exception as e:
            messages.error(request, f'Error al actualizar repartidor: {str(e)}')
    return render(request, 'repartidores/editar_repartidor.html', {'repartidor': repartidor})

@login_required
def eliminar_repartidor(request, repartidor_id):
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    if request.method == 'POST':
        try:
            repartidor.delete()
            messages.success(request, 'Repartidor eliminado exitosamente!')
            return redirect('lista_repartidores')
        except Exception as e:
            messages.error(request, f'Error al eliminar repartidor: {str(e)}')
    return render(request, 'repartidores/eliminar_repartidor.html', {'repartidor': repartidor})

# ✅ VISTAS DE PEDIDOS
@login_required
def lista_pedidos(request):
    estado = request.GET.get('estado', '')
    if estado:
        pedidos = Pedido.objects.filter(estado=estado).select_related('cliente', 'repartidor').order_by('-fecha_pedido')
    else:
        pedidos = Pedido.objects.select_related('cliente', 'repartidor').order_by('-fecha_pedido')
    return render(request, 'pedidos/lista_pedidos.html', {
        'pedidos': pedidos,
        'estado_filtro': estado
    })

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        try:
            cliente_id = request.POST.get('cliente')
            repartidor_id = request.POST.get('repartidor')
            direccion_entrega = request.POST.get('direccion_entrega')
            zona_entrega = request.POST.get('zona_entrega')
            estado = request.POST.get('estado', 'pendiente')
            prioridad = request.POST.get('prioridad', 'normal')
            tiempo_estimado_minutos = request.POST.get('tiempo_estimado_minutos')
            observaciones = request.POST.get('observaciones')
            if not cliente_id or not direccion_entrega or not zona_entrega or not tiempo_estimado_minutos:
                messages.error(request, 'Todos los campos marcados con * son requeridos')
                return render(request, 'pedidos/form_pedido.html', {
                    'clientes': Cliente.objects.all(),
                    'repartidores': Repartidor.objects.filter(activo=True, disponible=True)
                })
            cliente = Cliente.objects.get(pk=cliente_id)
            repartidor = Repartidor.objects.get(pk=repartidor_id) if repartidor_id else None
            pedido = Pedido(
                cliente=cliente,
                repartidor=repartidor,
                direccion_entrega=direccion_entrega,
                zona_entrega=zona_entrega,
                estado=estado,
                prioridad=prioridad,
                tiempo_estimado_minutos=tiempo_estimado_minutos,
                observaciones=observaciones
            )
            pedido.save()
            HistorialEstados.objects.create(
                pedido=pedido,
                estado_nuevo=estado,
                usuario=request.user.username
            )
            messages.success(request, f'Pedido #{pedido.pedido_id} creado exitosamente!')
            return redirect('lista_pedidos')
        except Exception as e:
            messages.error(request, f'Error al crear pedido: {str(e)}')
    return render(request, 'pedidos/form_pedido.html', {
        'clientes': Cliente.objects.all(),
        'repartidores': Repartidor.objects.filter(activo=True, disponible=True)
    })

@login_required
def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        try:
            pedido.cliente_id = request.POST.get('cliente')
            pedido.repartidor_id = request.POST.get('repartidor')
            pedido.direccion_entrega = request.POST.get('direccion_entrega')
            pedido.zona_entrega = request.POST.get('zona_entrega')
            pedido.estado = request.POST.get('estado')
            pedido.prioridad = request.POST.get('prioridad')
            pedido.tiempo_estimado_minutos = request.POST.get('tiempo_estimado_minutos')
            pedido.observaciones = request.POST.get('observaciones')
            pedido.save()
            messages.success(request, f'Pedido #{pedido_id} actualizado exitosamente!')
            return redirect('lista_pedidos')
        except Exception as e:
            messages.error(request, f'Error al actualizar pedido: {str(e)}')
    return render(request, 'pedidos/editar_pedido.html', {
        'pedido': pedido,
        'clientes': Cliente.objects.all(),
        'repartidores': Repartidor.objects.filter(activo=True)
    })

@login_required
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        try:
            pedido.delete()
            messages.success(request, 'Pedido eliminado exitosamente!')
            return redirect('lista_pedidos')
        except Exception as e:
            messages.error(request, f'Error al eliminar pedido: {str(e)}')
    return render(request, 'pedidos/eliminar_pedido.html', {'pedido': pedido})

@login_required
def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    repartidores_disponibles = Repartidor.objects.filter(activo=True, disponible=True)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        repartidor_id = request.POST.get('repartidor_id')
        if nuevo_estado:
            estado_anterior = pedido.estado
            pedido.estado = nuevo_estado
            if nuevo_estado == 'asignado' and repartidor_id:
                repartidor = Repartidor.objects.get(pk=repartidor_id)
                pedido.repartidor = repartidor
                pedido.fecha_asignacion = timezone.now()
            if nuevo_estado == 'asignado' and not pedido.fecha_asignacion:
                pedido.fecha_asignacion = timezone.now()
            elif nuevo_estado == 'entregado' and not pedido.fecha_entrega_real:
                pedido.fecha_entrega_real = timezone.now()
                if pedido.fecha_pedido and pedido.fecha_entrega_real:
                    diferencia = pedido.fecha_entrega_real - pedido.fecha_pedido
                    pedido.tiempo_real_minutos = int(diferencia.total_seconds() // 60)
                crear_reporte_entrega(pedido)
            pedido.save()
            HistorialEstados.objects.create(
                pedido=pedido,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario=request.user.username
            )
            messages.success(request, f'✅ Estado del pedido #{pedido_id} actualizado a "{pedido.get_estado_display()}"')
            return redirect('lista_pedidos')
    return render(request, 'pedidos/cambiar_estado.html', {
        'pedido': pedido,
        'repartidores_disponibles': repartidores_disponibles
    })

@login_required
def historial_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    historial = HistorialEstados.objects.filter(pedido=pedido).order_by('-fecha_cambio')
    return render(request, 'pedidos/historial_pedido.html', {
        'pedido': pedido,
        'historial': historial
    })

# ✅ ASIGNACIÓN MANUAL DE REPARTIDORES
@login_required
def asignar_repartidor_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    repartidores_disponibles = Repartidor.objects.filter(activo=True, disponible=True)
    
    if request.method == 'POST':
        repartidor_id = request.POST.get('repartidor_id')
        
        if repartidor_id:
            repartidor = Repartidor.objects.get(pk=repartidor_id)
            
            # Asignar repartidor al pedido
            pedido.repartidor = repartidor
            pedido.estado = 'asignado'
            pedido.fecha_asignacion = timezone.now()
            pedido.save()
            
            # Reducir capacidad del repartidor
            repartidor.capacidad_entregas -= 1
            if repartidor.capacidad_entregas <= 0:
                repartidor.disponible = False
            repartidor.save()
            
            # Registrar en historial
            HistorialEstados.objects.create(
                pedido=pedido,
                estado_anterior='pendiente',
                estado_nuevo='asignado',
                usuario=request.user.username
            )
            
            messages.success(request, f'✅ Repartidor {repartidor.nombres} asignado al pedido #{pedido_id}')
            return redirect('lista_pedidos')
    
    return render(request, 'pedidos/asignar_repartidor.html', {
        'pedido': pedido,
        'repartidores_disponibles': repartidores_disponibles
    })

@login_required
def reasignar_repartidor_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    repartidores_disponibles = Repartidor.objects.filter(activo=True, disponible=True)
    
    if request.method == 'POST':
        repartidor_id = request.POST.get('repartidor_id')
        
        if repartidor_id:
            nuevo_repartidor = Repartidor.objects.get(pk=repartidor_id)
            repartidor_anterior = pedido.repartidor
            
            # Liberar capacidad del repartidor anterior
            if repartidor_anterior:
                repartidor_anterior.capacidad_entregas += 1
                repartidor_anterior.disponible = True
                repartidor_anterior.save()
            
            # Asignar nuevo repartidor
            pedido.repartidor = nuevo_repartidor
            pedido.save()
            
            # Reducir capacidad del nuevo repartidor
            nuevo_repartidor.capacidad_entregas -= 1
            if nuevo_repartidor.capacidad_entregas <= 0:
                nuevo_repartidor.disponible = False
            nuevo_repartidor.save()
            
            messages.success(request, f'✅ Pedido #{pedido_id} reasignado a {nuevo_repartidor.nombres}')
            return redirect('lista_pedidos')
    
    return render(request, 'pedidos/reasignar_repartidor.html', {
        'pedido': pedido,
        'repartidores_disponibles': repartidores_disponibles
    })

# ✅ ASIGNACIÓN AUTOMÁTICA DE REPARTIDORES
@login_required
def asignar_repartidores_automaticos(request):
    if request.method == 'POST':
        try:
            pedidos_pendientes = Pedido.objects.filter(
                estado='pendiente',
                repartidor__isnull=True
            )
            repartidores_disponibles = Repartidor.objects.filter(
                activo=True,
                disponible=True
            ).order_by('capacidad_entregas')
            asignaciones = 0
            for pedido in pedidos_pendientes:
                for repartidor in repartidores_disponibles:
                    if repartidor.capacidad_entregas > 0:
                        pedido.repartidor = repartidor
                        pedido.estado = 'asignado'
                        pedido.fecha_asignacion = timezone.now()
                        pedido.save()
                        repartidor.capacidad_entregas -= 1
                        if repartidor.capacidad_entregas <= 0:
                            repartidor.disponible = False
                        repartidor.save()
                        HistorialEstados.objects.create(
                            pedido=pedido,
                            estado_anterior='pendiente',
                            estado_nuevo='asignado',
                            usuario=request.user.username
                        )
                        asignaciones += 1
                        break
            messages.success(request, f'✅ Se asignaron {asignaciones} pedidos a repartidores disponibles')
            return redirect('lista_pedidos')
        except Exception as e:
            messages.error(request, f'❌ Error en asignación automática: {str(e)}')
    return redirect('lista_pedidos')

# ✅ VISTAS DE REPORTES
@login_required
def reportes_entregas(request):
    reportes = ReporteEntregas.objects.select_related('pedido', 'repartidor').order_by('-fecha_reporte')
    total_entregas = reportes.count()
    entregas_exitosas = reportes.filter(estado_entrega='exitosa').count()
    entregas_fallidas = reportes.filter(estado_entrega='fallida').count()
    entregas_reprogramadas = reportes.filter(estado_entrega='reprogramada').count()
    promedio_calificacion = reportes.filter(calificacion__isnull=False).aggregate(
        avg_calificacion=Avg('calificacion')
    )['avg_calificacion'] or 0
    pedidos_entregados_sin_reporte = Pedido.objects.filter(
        estado='entregado'
    ).exclude(
        pedido_id__in=ReporteEntregas.objects.values('pedido_id')
    ).select_related('cliente')
    context = {
        'reportes': reportes,
        'total_entregas': total_entregas,
        'entregas_exitosas': entregas_exitosas,
        'entregas_fallidas': entregas_fallidas,
        'entregas_reprogramadas': entregas_reprogramadas,
        'promedio_calificacion': round(promedio_calificacion, 2),
        'pedidos_sin_reporte': pedidos_entregados_sin_reporte.count(),
        'pedidos_entregados_sin_reporte': pedidos_entregados_sin_reporte,
    }
    return render(request, 'reportes/lista_reportes.html', context)

@login_required
def crear_reporte_manual(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if pedido.estado != 'entregado':
        messages.error(request, 'Solo se pueden crear reportes para pedidos entregados')
        return redirect('lista_pedidos')
    if ReporteEntregas.objects.filter(pedido=pedido).exists():
        messages.warning(request, 'Ya existe un reporte para este pedido')
        return redirect('reportes_entregas')
    if request.method == 'POST':
        try:
            fecha_reporte = request.POST.get('fecha_reporte')
            hora_salida = request.POST.get('hora_salida')
            hora_llegada = request.POST.get('hora_llegada')
            hora_entrega = request.POST.get('hora_entrega')
            tiempo_transito = request.POST.get('tiempo_transito')
            tiempo_total = request.POST.get('tiempo_total')
            estado_entrega = request.POST.get('estado_entrega')
            calificacion = request.POST.get('calificacion')
            comentarios_cliente = request.POST.get('comentarios_cliente')
            motivo_falla = request.POST.get('motivo_falla')
            reporte = ReporteEntregas(
                pedido=pedido,
                repartidor=pedido.repartidor,
                fecha_reporte=fecha_reporte,
                hora_salida=hora_salida,
                hora_llegada=hora_llegada,
                hora_entrega=hora_entrega,
                tiempo_transito=tiempo_transito,
                tiempo_total=tiempo_total,
                estado_entrega=estado_entrega,
                calificacion=calificacion,
                comentarios_cliente=comentarios_cliente,
                motivo_falla=motivo_falla if estado_entrega == 'fallida' else None
            )
            reporte.save()
            messages.success(request, f'Reporte de entrega creado para pedido #{pedido_id}')
            return redirect('reportes_entregas')
        except Exception as e:
            messages.error(request, f'Error al crear reporte: {str(e)}')
    return render(request, 'reportes/crear_reporte.html', {
        'pedido': pedido
    })

@login_required
def editar_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteEntregas, pk=reporte_id)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del reporte
            reporte.fecha_reporte = request.POST.get('fecha_reporte')
            reporte.hora_salida = request.POST.get('hora_salida') or None
            reporte.hora_llegada = request.POST.get('hora_llegada') or None
            reporte.hora_entrega = request.POST.get('hora_entrega') or None
            reporte.tiempo_transito = request.POST.get('tiempo_transito') or None
            reporte.tiempo_total = request.POST.get('tiempo_total') or None
            reporte.estado_entrega = request.POST.get('estado_entrega')
            reporte.calificacion = request.POST.get('calificacion') or None
            reporte.comentarios_cliente = request.POST.get('comentarios_cliente')
            
            # Manejar motivo de falla
            if request.POST.get('estado_entrega') == 'fallida':
                reporte.motivo_falla = request.POST.get('motivo_falla')
            else:
                reporte.motivo_falla = None
            
            reporte.save()
            
            messages.success(request, '✅ Reporte actualizado exitosamente')
            return redirect('reportes_entregas')
            
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar reporte: {str(e)}')
    
    return render(request, 'reportes/editar_reporte.html', {
        'reporte': reporte
    })

@login_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteEntregas, pk=reporte_id)
    return render(request, 'reportes/detalle_reporte.html', {
        'reporte': reporte
    })

@login_required
def eliminar_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteEntregas, pk=reporte_id)
    if request.method == 'POST':
        try:
            reporte.delete()
            messages.success(request, 'Reporte eliminado exitosamente!')
            return redirect('reportes_entregas')
        except Exception as e:
            messages.error(request, f'Error al eliminar reporte: {str(e)}')
    return render(request, 'reportes/eliminar_reporte.html', {'reporte': reporte})

# ✅ DASHBOARD
@login_required
def dashboard(request):
    pedidos_por_estado = Pedido.objects.values('estado').annotate(total=Count('estado'))
    top_repartidores = Repartidor.objects.annotate(
        total_entregas=Count('pedido')
    ).filter(total_entregas__gt=0).order_by('-total_entregas')[:5]
    hoy = timezone.now().date()
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    reportes_hoy = ReporteEntregas.objects.filter(fecha_reporte=hoy).count()
    context = {
        'pedidos_por_estado': list(pedidos_por_estado),
        'top_repartidores': top_repartidores,
        'pedidos_hoy': pedidos_hoy,
        'reportes_hoy': reportes_hoy,
    }
    return render(request, 'dashboard.html', context)