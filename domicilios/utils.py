def calcular_tiempo_entrega(zona, prioridad):
    """
    Calcula el tiempo estimado de entrega basado en zona y prioridad
    """
    tiempos_base = {
        'Norte': 30,
        'Sur': 45,
        'Este': 35,
        'Oeste': 40,
        'Centro': 25
    }
    
    multiplicadores_prioridad = {
        'normal': 1.0,
        'alta': 0.8,
        'urgente': 0.6
    }
    
    tiempo_base = tiempos_base.get(zona, 30)
    multiplicador = multiplicadores_prioridad.get(prioridad, 1.0)
    
    return int(tiempo_base * multiplicador)

def obtener_repartidores_disponibles(zona):
    """
    Retorna repartidores disponibles para una zona específica
    """
    from .models import Repartidor
    return Repartidor.objects.filter(
        zona_asignada=zona,
        disponible=True,
        activo=True
    )