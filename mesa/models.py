from django.db import models
from config import settings
from django.core.exceptions import ValidationError

class Establecimiento(models.Model):
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
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    fecha_canje = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(max_length=20, choices=PlanSuscripcion.Categoria.choices)

    def clean(self):
        # 1. Buscamos la suscripción activa
        suscripcion = SuscripcionUsuario.objects.filter(
            usuario=self.usuario, 
            esta_activa=True
        ).first()
        
        if not suscripcion:
            raise ValidationError("Este usuario no tiene ninguna suscripción activa.")
        
        # 2. Bloqueamos "TRIAL" (el ticket debe ser de lo que se come realmente)
        if self.categoria == 'TRIAL':
            raise ValidationError("El ticket debe ser para Desayuno, Comida, Cena o Afterwork; no 'Trial'.")

        # 3. Comprobamos los saldos
        usos = {
            'DESAYUNO': suscripcion.usos_desayuno,
            'COMIDA': suscripcion.usos_comida,
            'CENA': suscripcion.usos_cena,
            'AFTERWORK': suscripcion.usos_afterwork,
        }
        
        if usos.get(self.categoria, 0) <= 0:
            raise ValidationError(f"Al usuario no le quedan usos de {self.get_categoria_display()}.")

    def save(self, *args, **kwargs):
        # Forzamos la validación antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Descontamos el uso automáticamente
        suscripcion = SuscripcionUsuario.objects.filter(
            usuario=self.usuario, 
            esta_activa=True
        ).first()
        
        if self.categoria == 'DESAYUNO': suscripcion.usos_desayuno -= 1
        elif self.categoria == 'COMIDA': suscripcion.usos_comida -= 1
        elif self.categoria == 'CENA': suscripcion.usos_cena -= 1
        elif self.categoria == 'AFTERWORK': suscripcion.usos_afterwork -= 1
        
        suscripcion.save()

    def __str__(self):
        return f"{self.usuario.email} en {self.establecimiento.nombre} ({self.get_categoria_display()})"