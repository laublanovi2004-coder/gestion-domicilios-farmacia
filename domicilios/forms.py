from django import forms
from .models import Cliente, Repartidor, Pedido, ReporteEntregas

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'zona': forms.TextInput(attrs={'class': 'form-control'}),
            'discapacidad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RepartidorForm(forms.ModelForm):
    class Meta:
        model = Repartidor
        fields = '__all__'
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'zona_asignada': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad_entregas': forms.NumberInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = '__all__'
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'repartidor': forms.Select(attrs={'class': 'form-control'}),
            'direccion_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'zona_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'tiempo_estimado_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_entrega_estimada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class ReporteEntregaForm(forms.ModelForm):
    class Meta:
        model = ReporteEntregas
        fields = '__all__'
        widgets = {
            'pedido': forms.Select(attrs={'class': 'form-control'}),
            'repartidor': forms.Select(attrs={'class': 'form-control'}),
            'fecha_reporte': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_salida': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_llegada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_entrega': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'estado_entrega': forms.Select(attrs={'class': 'form-control'}),
            'calificacion': forms.Select(attrs={'class': 'form-control'}),
            'motivo_falla': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comentarios_cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }