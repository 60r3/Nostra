from django.shortcuts import render, get_object_or_404
from .models import Cata


def detalle_cata(request, slug):
    cata = get_object_or_404(Cata, slug=slug)
    ubicacion = cata.get_ubicacion()
    return render(request, 'cata/detalle.html', {
        'cata': cata,
        'ubicacion': ubicacion,
    })
