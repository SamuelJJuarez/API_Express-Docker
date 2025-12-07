"""
Servicio para comunicación con el API REST del backend
"""
import requests
import json
from typing import List, Dict, Optional
from utils.config import API_BASE_URL, ENDPOINTS, REQUEST_TIMEOUT

class APIService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = REQUEST_TIMEOUT
    
    def _build_url(self, endpoint_key, **kwargs):
        """
        Construye la URL completa para un endpoint
        
        Args:
            endpoint_key: Clave del endpoint en el config
            **kwargs: Parámetros para reemplazar en la URL (ej: id=5)
        
        Returns:
            str: URL completa
        """
        endpoint = ENDPOINTS.get(endpoint_key, '')
        url = self.base_url + endpoint.format(**kwargs)
        return url
    
    def _handle_response(self, response):
        """
        Maneja la respuesta del API
        
        Args:
            response: Objeto Response de requests
        
        Returns:
            dict: Datos de la respuesta
        
        Raises:
            Exception: Si hay error en la petición
        """
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'success': True}
        else:
            error_msg = f"Error {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('message', error_msg)
            except:
                pass
            raise Exception(error_msg)
    
    # ==================== GESTIÓN DE RENTAS ====================
    
    def crear_renta(self, cliente_id, film_id, staff_id):
        """
        Crea una nueva renta
        
        Args:
            cliente_id: ID del cliente
            film_id: ID de la película
            staff_id: ID del empleado
        
        Returns:
            dict: Datos de la renta creada
        """
        url = self._build_url('crear_renta')
        data = {
            'customer_id': cliente_id,  # ✅ CAMBIO: customer_id en lugar de cliente_id
            'film_id': film_id,         # ✅ CORRECTO
            'staff_id': staff_id        # ✅ CORRECTO
        }
        
        response = requests.post(url, json=data, timeout=self.timeout)
        return self._handle_response(response)
    
    def devolver_renta(self, renta_id):
        """
        Marca una renta como devuelta
        
        Args:
            renta_id: ID de la renta
        
        Returns:
            dict: Datos actualizados de la renta
        """
        url = self._build_url('devolver_renta', id=renta_id)
        response = requests.put(url, timeout=self.timeout)
        return self._handle_response(response)
    
    def cancelar_renta(self, renta_id):
        """
        Cancela una renta
        
        Args:
            renta_id: ID de la renta
        
        Returns:
            dict: Confirmación de cancelación
        """
        url = self._build_url('cancelar_renta', id=renta_id)
        response = requests.delete(url, timeout=self.timeout)
        return self._handle_response(response)
    
    # ==================== REPORTES ====================
    
    def obtener_rentas_cliente(self, cliente_id):
        """
        Obtiene todas las rentas de un cliente
        
        Args:
            cliente_id: ID del cliente
        
        Returns:
            dict: Respuesta con rentas del cliente
        """
        # ✅ CAMBIO CRÍTICO: Usar /reports/customer-rentals en lugar de /rentals/customer
        url = f"{self.base_url}/reports/customer-rentals/{cliente_id}"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)
    
    def obtener_dvds_no_devueltos(self):
        """
        Obtiene la lista de DVDs que no se han devuelto (rentas activas)
        
        Returns:
            dict: Respuesta con rentas activas
        """
        url = self._build_url('no_devueltos')
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)
    
    def obtener_dvds_mas_rentados(self, limit=10):
        """
        Obtiene el ranking de DVDs más rentados
        
        Args:
            limit: Número máximo de resultados
        
        Returns:
            dict: Respuesta con DVDs más rentados
        """
        # ✅ AGREGAR parámetro limit
        url = f"{self.base_url}/reports/most-rented?limit={limit}"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)
    
    def obtener_ganancias_staff(self, staff_id=None):
        """
        Obtiene las ganancias generadas por cada miembro del staff
        
        Args:
            staff_id: ID del staff específico (opcional)
        
        Returns:
            dict: Respuesta con ganancias del staff
        """
        if staff_id:
            url = f"{self.base_url}/reports/staff-revenue/{staff_id}"
        else:
            url = f"{self.base_url}/reports/staff-revenue"
        
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)
    
    # ==================== CATÁLOGOS (OPCIONAL) ====================
    
    def obtener_clientes(self):
        """
        Obtiene la lista de todos los clientes
        """
        # ✅ Solicitar límite alto para obtener todos
        url = f"{self.base_url}/customers?limit=1000"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)

    def obtener_dvds(self):
        """
        Obtiene la lista de todos los DVDs
        """
        # ✅ Solicitar límite alto para obtener todos
        url = f"{self.base_url}/films?limit=1000"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)

    def obtener_staff(self):
        """
        Obtiene la lista de todos los empleados
        """
        # ✅ Solicitar límite alto
        url = f"{self.base_url}/staff?limit=100"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)