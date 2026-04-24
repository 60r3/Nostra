from django.db import models
from config import settings
from django.core.exceptions import ValidationError
import secrets
import string
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

class Establecimiento(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    dueño = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Cupos diarios por categoría
    cupo_desayuno = models.PositiveIntegerField(default=5)
    cupo_comida = models.PositiveIntegerField(default=5)
    cupo_cena = models.PositiveIntegerField(default=5)
    cupo_afterwork = models.PositiveIntegerField(default=5)

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
    duracion_dias = models.PositiveIntegerField(default=30)
    
    # --- CAMBIOS DEL PASO 1: Definición de la oferta del plan ---
    incluye_desayunos = models.PositiveIntegerField(default=0)
    incluye_comidas = models.PositiveIntegerField(default=0)
    incluye_cenas = models.PositiveIntegerField(default=0)
    incluye_afterworks = models.PositiveIntegerField(default=0)
    # ------------------------------------------------------------

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
    
    # --- CAMBIOS DEL PASO 2: Contadores independientes ---
    usos_desayuno = models.PositiveIntegerField(default=0)
    usos_comida = models.PositiveIntegerField(default=0)
    usos_cena = models.PositiveIntegerField(default=0)
    usos_afterwork = models.PositiveIntegerField(default=0)
    
    esta_activa = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Si es la primera vez que se crea la suscripción, 
        # copiamos la oferta exacta del plan a la cartera del usuario
        if not self.pk:
            self.usos_desayuno = self.plan.incluye_desayunos
            self.usos_comida = self.plan.incluye_comidas
            self.usos_cena = self.plan.incluye_cenas
            self.usos_afterwork = self.plan.incluye_afterworks
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.email} - {self.plan.nombre}"
    

class TicketCanje(models.Model):
    class Estado(models.TextChoices):
        RESERVADO = 'RESERVADO', 'Reservado'
        CANJEADO = 'CANJEADO', 'Canjeado'
        CADUCADO = 'CADUCADO', 'Caducado/No-Show'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(
        Establecimiento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    categoria = models.CharField(max_length=20, choices=PlanSuscripcion.Categoria.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.RESERVADO)
    
    # Tiempos (null=True para que las filas viejas no den error al migrar)
    fecha_reserva = models.DateTimeField(auto_now_add=True, null=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    
    # Seguridad (Unique + Null=True es la clave para migrar sin errores)
    token_qr = models.CharField(max_length=100, unique=True, null=True, blank=True)
    codigo_manual = models.CharField(max_length=6, unique=True, null=True, blank=True)
    
    # Campos financieros
    precio_suscripcion_momento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    comision_calculada = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    datos_extra = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:  
            self.fecha_limite = timezone.now() + timedelta(hours=1)
            
            if not self.codigo_manual:
                self.codigo_manual = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            
            if not self.token_qr:
                self.token_qr = secrets.token_urlsafe(32)

            self.descontar_uso_suscripcion()

        super().save(*args, **kwargs)

    def descontar_uso_suscripcion(self):
        with transaction.atomic():
            suscripcion = SuscripcionUsuario.objects.select_for_update().filter(
                usuario=self.usuario, 
                esta_activa=True
            ).first()
            
            if suscripcion:
                if self.categoria == 'DESAYUNO': suscripcion.usos_desayuno -= 1
                elif self.categoria == 'COMIDA': suscripcion.usos_comida -= 1
                elif self.categoria == 'CENA': suscripcion.usos_cena -= 1
                elif self.categoria == 'AFTERWORK': suscripcion.usos_afterwork -= 1
                suscripcion.save()

    def __str__(self):
        nombre_est = self.establecimiento.nombre if self.establecimiento else "Sin local"
        return f"{self.estado} - {self.usuario.email} en {nombre_est}"