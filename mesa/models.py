from django.db import models
from config import settings

class Restaurante(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    dueno = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'es_hostelero': True}
    )
    esta_activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class PlanSuscripcion(models.Model):
    class Categoria(models.TextChoices):
        DESAYUNO = 'DESAYUNO', 'Desayuno'
        COMIDA = 'COMIDA', 'Comida'
        CENA = 'CENA', 'Cena'
        AFTERWORK = 'AFTERWORK', 'Afterwork'
        TRIAL = 'TRIAL', 'Trial'

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.COMIDA
    )
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    usos_maximos = models.PositiveIntegerField(
        default=1, 
        help_text="Número de usos permitidos por ciclo de facturación"
    )
    duracion_dias = models.PositiveIntegerField(default=30)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"
    
class SuscripcionUsuario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='suscripciones'
    )
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField()
    usos_restantes = models.PositiveIntegerField(
        help_text="Cantidad de usos disponibles para el periodo actual"
    )
    esta_activa = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Si es la primera vez que se crea la suscripción, 
        # copiamos los usos máximos del plan a los usos restantes.
        if not self.pk:
            self.usos_restantes = self.plan.usos_maximos
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.email} - {self.plan.nombre}"