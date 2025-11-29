"""
Configuración de la aplicación
"""

# URL base del backend API
API_BASE_URL = "http://localhost:3000"

# Timeout para peticiones HTTP (en segundos)
REQUEST_TIMEOUT = 10

# Endpoints del API
ENDPOINTS = {
    # Gestión de Rentas
    'crear_renta': '/rentals',                          # POST /rentals
    'devolver_renta': '/rentals/{id}/return',           # PUT /rentals/:rental_id/return
    'cancelar_renta': '/rentals/{id}',                  # DELETE /rentals/:rental_id
    
    # Reportes
    # ⚠️ CAMBIO CRÍTICO: Rentas por cliente ahora usa /reports/customer-rentals
    'rentas_cliente': '/reports/customer-rentals/{id}', # GET /reports/customer-rentals/:customer_id ✅
    'no_devueltos': '/reports/unreturned-dvds',         # GET /reports/unreturned-dvds
    'mas_rentados': '/reports/most-rented',             # GET /reports/most-rented
    'ganancias_staff': '/reports/staff-revenue',        # GET /reports/staff-revenue
    
    # Catálogos (TODAS SIN /api)
    'clientes': '/customers',                           # GET /customers
    'dvds': '/films',                                   # GET /films
    'staff': '/staff'                                   # GET /staff
}

# Configuración de la interfaz
APP_TITLE = "Sistema de Renta de DVDs"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Mensajes de la aplicación
MESSAGES = {
    'connection_error': 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.',
    'timeout_error': 'La petición tardó demasiado tiempo. Intenta de nuevo.',
    'success_renta': 'Renta registrada exitosamente',
    'success_devolucion': 'Devolución procesada exitosamente',
    'success_cancelacion': 'Renta cancelada exitosamente',
    'error_general': 'Ocurrió un error. Por favor intenta de nuevo.',
    'confirm_cancelacion': '¿Estás seguro de cancelar esta renta?'
}