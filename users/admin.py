from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Nostra', {'fields': ('es_comensal', 'es_hostelero', 'telefono')}),
    )
    list_display = ['username', 'email', 'es_comensal', 'es_hostelero', 'is_staff']

admin.site.register(User, CustomUserAdmin)