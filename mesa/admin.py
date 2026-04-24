from django.contrib import admin
from .models import Establecimiento, PlanSuscripcion, SuscripcionUsuario, TicketCanje

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'dueño')

@admin.register(PlanSuscripcion)
class PlanSuscripcionAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 
        'categoria', 
        'precio', 
        'duracion_dias', 
        'incluye_desayunos', 
        'incluye_comidas', 
        'incluye_cenas',
        'incluye_afterworks'
    )
    list_filter = ('categoria',)

@admin.register(SuscripcionUsuario)
class SuscripcionUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 
        'plan', 
        'usos_desayuno', 
        'usos_comida', 
        'usos_cena', 
        'usos_afterwork',
        'esta_activa'
    )
    list_filter = ('esta_activa', 'plan__categoria')

@admin.register(TicketCanje)
class TicketCanjeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'establecimiento', 'categoria', 'fecha_reserva', 'estado')
    list_filter = ('estado', 'categoria', 'establecimiento')