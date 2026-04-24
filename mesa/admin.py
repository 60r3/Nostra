from django.contrib import admin
from .models import Restaurante

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dueno', 'esta_activo')
    list_filter = ('esta_activo',)
    search_fields = ('nombre', 'dueno__username')