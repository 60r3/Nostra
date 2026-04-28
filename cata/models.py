from django.db import models
from django.utils.text import slugify
from mesa.models import Establecimiento

# Create your models here.
class Cata(models.Model):
    ESTADO_CHOICES = [
        ('Borrador', 'Borrador'),
        ('Publicado', 'Publicado'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado'),
    ]

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    cupo_maximo = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Borrador'
    )
    
    # Ubicación híbrida
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_lugar_manual = models.CharField(max_length=200, null=True, blank=True)
    direccion_manual = models.CharField(max_length=255, null=True, blank=True)
    google_maps_url = models.URLField(max_length=500, null=True, blank=True)

    def get_ubicacion(self):
        if self.establecimiento:
            return {
                'nombre': self.establecimiento.nombre,
                'direccion': self.establecimiento.direccion,
                'maps_url': getattr(self.establecimiento, 'google_maps_url', None)
            }
        return {
            'nombre': self.nombre_lugar_manual,
            'direccion': self.direccion_manual,
            'maps_url': self.google_maps_url
        }

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
