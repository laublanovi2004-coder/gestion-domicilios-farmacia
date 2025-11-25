"""
URL configuration for gestion_domicilios project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from domicilios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_cliente, name='registro_cliente'),
    
    # URLs para clientes
    path('cliente/', include([
        path('dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
        path('pedidos/crear/', views.cliente_crear_pedido, name='cliente_crear_pedido'),
        path('perfil/editar/', views.cliente_editar_perfil, name='cliente_editar_perfil'),
    ])),
    
    # URLs de clientes (admin)
    path('clientes/', include([
        path('', views.lista_clientes, name='lista_clientes'),
        path('crear/', views.crear_cliente, name='crear_cliente'),
        path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
        path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    ])),
    
    # URLs de repartidores
    path('repartidores/', include([
        path('', views.lista_repartidores, name='lista_repartidores'),
        path('crear/', views.crear_repartidor, name='crear_repartidor'),
        path('editar/<int:repartidor_id>/', views.editar_repartidor, name='editar_repartidor'),
        path('eliminar/<int:repartidor_id>/', views.eliminar_repartidor, name='eliminar_repartidor'),
    ])),
    
    # URLs de pedidos
    path('pedidos/', include([
        path('', views.lista_pedidos, name='lista_pedidos'),
        path('crear/', views.crear_pedido, name='crear_pedido'),
        path('editar/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),
        path('eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
        path('<int:pedido_id>/cambiar-estado/', views.actualizar_estado_pedido, name='cambiar_estado_pedido'),
        path('<int:pedido_id>/historial/', views.historial_pedido, name='historial_pedido'),
        path('asignar-automaticos/', views.asignar_repartidores_automaticos, name='asignar_automaticos'),
        # Nuevas URLs para asignación manual
        path('asignar-repartidor/<int:pedido_id>/', views.asignar_repartidor_pedido, name='asignar_repartidor'),
        path('reasignar-repartidor/<int:pedido_id>/', views.reasignar_repartidor_pedido, name='reasignar_repartidor'),
    ])),
    
    # URLs de reportes
    path('reportes/', include([
        path('', views.reportes_entregas, name='reportes_entregas'),
        path('crear/<int:pedido_id>/', views.crear_reporte_manual, name='crear_reporte_manual'),
        path('editar/<int:reporte_id>/', views.editar_reporte, name='editar_reporte'),
        path('detalle/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
        path('eliminar/<int:reporte_id>/', views.eliminar_reporte, name='eliminar_reporte'),
    ])),
]