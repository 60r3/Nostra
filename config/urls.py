from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('experiencias/', include('cata.urls')), # Cambiado de 'catas/' a 'experiencias/'
]