from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    cliente_id = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, blank=True, null=True)
    discapacidad = models.BooleanField(default=False)
    zona = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'CLIENTE'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.cedula}"

class Repartidor(models.Model):
    repartidor_id = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    vehiculo = models.CharField(max_length=50, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    zona_asignada = models.CharField(max_length=50)
    capacidad_entregas = models.IntegerField(default=5)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'REPARTIDOR'
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.vehiculo}"

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignado', 'Asignado'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    pedido_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    repartidor = models.ForeignKey(Repartidor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pedido = models.DateTimeField(default=timezone.now)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega_estimada = models.DateTimeField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_entrega = models.CharField(max_length=255)
    zona_entrega = models.CharField(max_length=50)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='normal')
    tiempo_estimado_minutos = models.IntegerField()
    tiempo_real_minutos = models.IntegerField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'PEDIDO'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['zona_entrega']),
            models.Index(fields=['fecha_pedido']),
        ]

    def __str__(self):
        return f"Pedido {self.pedido_id} - {self.cliente.nombres}"

class HistorialEstados(models.Model):
    historial_id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=50, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=50)
    fecha_cambio = models.DateTimeField(default=timezone.now)
    usuario = models.CharField(max_length=100)

    class Meta:
        db_table = 'HISTORIAL_ESTADOS'
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        indexes = [
            models.Index(fields=['pedido', 'fecha_cambio']),
        ]

    def __str__(self):
        return f"Historial {self.historial_id} - {self.pedido.pedido_id}"

class ReporteEntregas(models.Model):
    ESTADO_ENTREGA_CHOICES = [
        ('exitosa', 'Exitosa'),
        ('fallida', 'Fallida'),
        ('reprogramada', 'Reprogramada'),
    ]

    reporte_id = models.AutoField(primary_key=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    repartidor = models.ForeignKey(Repartidor, on_delete=models.CASCADE)
    fecha_reporte = models.DateField()
    hora_salida = models.TimeField(null=True, blank=True)
    hora_llegada = models.TimeField(null=True, blank=True)
    hora_entrega = models.TimeField(null=True, blank=True)
    tiempo_transito = models.IntegerField(null=True, blank=True)
    tiempo_total = models.IntegerField(null=True, blank=True)
    estado_entrega = models.CharField(max_length=15, choices=ESTADO_ENTREGA_CHOICES)
    motivo_falla = models.TextField(blank=True, null=True)
    calificacion = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    comentarios_cliente = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'REPORTE_ENTREGAS'
        verbose_name = 'Reporte de Entrega'
        verbose_name_plural = 'Reportes de Entrega'

    def __str__(self):
        return f"Reporte {self.reporte_id} - Pedido {self.pedido.pedido_id}"