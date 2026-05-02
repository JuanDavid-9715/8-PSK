"""
8-PSK Views - Django
"""

from django.shortcuts import render
from .utils.psk8_calculator import calculator


def home(request):
    # Obtener estilo seleccionado (neon o serious)
    style = request.GET.get('style', 'neon')
    
    # Seleccionar métodos según el estilo
    if style == 'serious':
        constellation = calculator.generate_constellation_diagram_serious()
        phasor = calculator.generate_phasor_diagram_serious()
        modulated = calculator.generate_modulated_output_serious()
    else:
        constellation = calculator.generate_constellation_diagram()
        phasor = calculator.generate_phasor_diagram()
        modulated = calculator.generate_modulated_output()
    
    context = {
        'title': 'Modulación 8-PSK',
        'style': style,
        
        # Tablas de convertidores
        'converter_tables': calculator.get_converter_tables(),
        
        # Todos los desarrollos matemáticos
        'all_developments': calculator.get_all_developments(),
        
        # Tabla de fases
        'table_data': calculator.get_table_data(),
        
        # Imágenes
        'constellation_image': constellation,
        'phasor_image': phasor,
        'modulated_image': modulated,
    }
    
    return render(request, 'home.html', context)
