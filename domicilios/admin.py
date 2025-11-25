from django.contrib import admin
from .models import Cliente, Repartidor, Pedido, HistorialEstados, ReporteEntregas

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombres', 'apellidos', 'telefono', 'zona', 'discapacidad', 'fecha_registro']
    search_fields = ['cedula', 'nombres', 'apellidos', 'telefono']
    list_filter = ['zona', 'discapacidad', 'fecha_registro']
    readonly_fields = ['fecha_registro']

@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombres', 'apellidos', 'telefono', 'vehiculo', 'disponible', 'zona_asignada']
    list_filter = ['vehiculo', 'disponible', 'activo', 'zona_asignada']
    search_fields = ['cedula', 'nombres', 'apellidos']
    list_editable = ['disponible']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido_id', 'cliente', 'repartidor', 'estado', 'prioridad', 'zona_entrega', 'fecha_pedido']
    list_filter = ['estado', 'prioridad', 'zona_entrega', 'fecha_pedido']
    search_fields = ['cliente__nombres', 'cliente__apellidos', 'pedido_id']
    readonly_fields = ['fecha_pedido']
    raw_id_fields = ['cliente', 'repartidor']

@admin.register(HistorialEstados)
class HistorialEstadosAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario']
    readonly_fields = ['fecha_cambio']
    list_filter = ['fecha_cambio', 'estado_nuevo']

@admin.register(ReporteEntregas)
class ReporteEntregasAdmin(admin.ModelAdmin):
    list_display = ['reporte_id', 'pedido', 'repartidor', 'estado_entrega', 'fecha_reporte', 'calificacion']
    list_filter = ['estado_entrega', 'fecha_reporte']
    search_fields = ['pedido__pedido_id', 'repartidor__nombres']