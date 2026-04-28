from django.contrib import admin
from .models import Cata

@admin.register(Cata)
class CataAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'get_ubicacion', 'precio', 'cupo_maximo', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('titulo', 'nombre_lugar_manual', 'direccion_manual')
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'slug', 'descripcion')
        }),
        ('Logística y Precio', {
            'fields': ('fecha', 'precio', 'cupo_maximo')
        }),
        ('Ubicación', {
            'fields': ('establecimiento', 'nombre_lugar_manual', 'direccion_manual', 'google_maps_url')
        }),
        ('Control', {
            'fields': ('estado',)
        }),
    )
    prepopulated_fields = {"slug": ("titulo",)}
