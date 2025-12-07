"""
Paquete de vistas de reportes
"""
from .cliente_view import ClienteReporteView
from .no_devueltos_view import NoDevueltosReporteView
from .mas_rentados_view import MasRentadosReporteView
from .ganancias_view import GananciasReporteView

__all__ = [
    'ClienteReporteView',
    'NoDevueltosReporteView', 
    'MasRentadosReporteView',
    'GananciasReporteView'
]

