"""
8-PSK Views - Django
"""

from django.shortcuts import render
from .utils.psk8_calculator import calculator

# Caché simple para imágenes generadas
_image_cache = {}

def get_cached_image(key, generator_func):
    """Obtiene imagen de caché o la genera si no existe"""
    if key not in _image_cache:
        _image_cache[key] = generator_func()
    return _image_cache[key]


def home(request):
    # Obtener estilo seleccionado (neon o serious)
    style = request.GET.get('style', 'neon')
    
    # Usar caché para las imágenes
    if style == 'serious':
        constellation = get_cached_image('constellation_serious', 
            calculator.generate_constellation_diagram_serious)
        phasor = get_cached_image('phasor_serious', 
            calculator.generate_phasor_diagram_serious)
        modulated = get_cached_image('modulated_serious', 
            calculator.generate_modulated_output_serious)
    else:
        constellation = get_cached_image('constellation_neon', 
            calculator.generate_constellation_diagram)
        phasor = get_cached_image('phasor_neon', 
            calculator.generate_phasor_diagram)
        modulated = get_cached_image('modulated_neon', 
            calculator.generate_modulated_output)
    
    context = {
        'title': 'Modulación 8-PSK',
        'style': style,
        
        # Tablas de convertidores
        'converter_tables': calculator.get_converter_tables(),
        
        # Todos los desarrollos matemáticos
        'all_developments': calculator.get_all_developments(),
        
        # Tabla de fases
        'table_data': calculator.get_table_data(),
        
        # Imágenes (desde caché)
        'constellation_image': constellation,
        'phasor_image': phasor,
        'modulated_image': modulated,
    }
    
    return render(request, 'home.html', context)