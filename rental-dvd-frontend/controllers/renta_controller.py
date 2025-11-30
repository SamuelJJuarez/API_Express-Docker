"""
Controlador para gestión de rentas
"""
from services.api_service import APIService
from utils.validators import (
    validar_campo_vacio, 
    validar_numero_positivo, 
    validar_id,
    validar_fecha_futura
)
from models.renta import Renta
from datetime import datetime, timedelta
import requests

class RentaController:
    def __init__(self):
        self.api_service = APIService()
    
    def validar_datos_renta(self, cliente_id, dvd_id, staff_id, fecha_devolucion, monto):
        """
        Valida los datos antes de crear una renta
        """
        # Validar cliente_id
        valido, msg = validar_id(cliente_id, "ID de Cliente")
        if not valido:
            return False, msg
        
        # Validar dvd_id
        valido, msg = validar_id(dvd_id, "ID de DVD")
        if not valido:
            return False, msg
        
        # Validar staff_id
        valido, msg = validar_id(staff_id, "ID de Staff")
        if not valido:
            return False, msg
        
        return True, ""
    
    def crear_renta(self, cliente_id, film_id, staff_id, fecha_devolucion_esperada, monto):
        """
        Crea una nueva renta
        
        Args:
            cliente_id: ID del cliente
            film_id: ID del film (película)
            staff_id: ID del empleado
            fecha_devolucion_esperada: No se usa (backend lo calcula)
            monto: No se usa (backend lo calcula)
        
        Returns:
            tuple: (exito, mensaje, datos_renta)
        """
        try:
            # Validar datos
            valido, msg_error = self.validar_datos_renta(
                cliente_id, film_id, staff_id, fecha_devolucion_esperada, monto
            )
            if not valido:
                return False, msg_error, None
            
            # ✅ LLAMAR AL SERVICIO CORREGIDO
            response_data = self.api_service.crear_renta(cliente_id, film_id, staff_id)
            
            # Verificar respuesta
            if not response_data.get('success'):
                error_msg = response_data.get('message', 'Error desconocido al crear renta')
                return False, error_msg, None
            
            # Obtener datos de la renta
            renta_data = response_data.get('data', {})
            
            # ✅ AGREGAR expected_return_date si el backend lo envía
            if 'expected_return_date' in renta_data:
                expected_date = renta_data['expected_return_date']
            elif 'rental_duration' in renta_data and 'rental_date' in renta_data:
                # Calcular en el frontend si el backend no lo envía
                rental_date = datetime.fromisoformat(renta_data['rental_date'].replace('Z', '+00:00'))
                rental_duration = renta_data['rental_duration']
                expected_date = (rental_date + timedelta(days=rental_duration)).isoformat()
                renta_data['expected_return_date'] = expected_date
            
            # Convertir respuesta a modelo
            renta = Renta.from_dict(renta_data)
            
            mensaje_exito = f"Renta creada exitosamente\n"
            mensaje_exito += f"ID: {renta_data.get('rental_id')}\n"
            mensaje_exito += f"Película: {renta_data.get('film_title')}\n"
            if 'expected_return_date' in renta_data:
                mensaje_exito += f"Fecha devolución esperada: {expected_date}\n"
            
            return True, mensaje_exito, renta
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor del API.", None
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo.", None
        except Exception as e:
            return False, f"Error al crear la renta: {str(e)}", None
    
    def devolver_renta(self, renta_id):
        """
        Marca una renta como devuelta
        """
        try:
            valido, msg_error = validar_id(renta_id, "ID de Renta")
            if not valido:
                return False, msg_error, None
            
            response_data = self.api_service.devolver_renta(renta_id)
            
            if not response_data.get('success'):
                error_msg = response_data.get('message', 'Error al procesar devolución')
                return False, error_msg, None
            
            renta_data = response_data.get('data', {})
            renta = Renta.from_dict(renta_data)
            
            mensaje = "Devolución procesada exitosamente\n"
            mensaje += f"Días rentados: {renta_data.get('days_rented', 'N/A')}\n"
            mensaje += f"Monto total: ${renta_data.get('total_amount', 0):.2f}"
            
            return True, mensaje, renta
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor.", None
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo.", None
        except Exception as e:
            return False, f"Error al procesar la devolución: {str(e)}", None
    
    def cancelar_renta(self, renta_id):
        """
        Cancela una renta
        """
        try:
            valido, msg_error = validar_id(renta_id, "ID de Renta")
            if not valido:
                return False, msg_error
            
            response_data = self.api_service.cancelar_renta(renta_id)
            
            if not response_data.get('success'):
                error_msg = response_data.get('message', 'Error al cancelar renta')
                return False, error_msg
            
            # ✅ AHORA EL BACKEND ENVÍA INFO COMPLETA
            cancel_data = response_data.get('data', {})
            
            mensaje = "Renta cancelada exitosamente\n\n"
            mensaje += f"ID Renta: {cancel_data.get('rental_id', 'N/A')}\n"
            
            if 'film' in cancel_data:
                mensaje += f"Película: {cancel_data['film'].get('title', 'N/A')}\n"
            
            if 'customer' in cancel_data:
                mensaje += f"Cliente: {cancel_data['customer'].get('name', 'N/A')}\n"
            
            if 'staff' in cancel_data:
                mensaje += f"Atendido por: {cancel_data['staff'].get('name', 'N/A')}\n"
            
            return True, mensaje
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo."
        except Exception as e:
            return False, f"Error al cancelar la renta: {str(e)}"
    
    def obtener_clientes(self):
        """
        Obtiene la lista de clientes disponibles
        """
        try:
            response_data = self.api_service.obtener_clientes()
            
            if isinstance(response_data, list):
                from models.cliente import Cliente
                clientes = [Cliente.from_dict(c) for c in response_data]
                return True, clientes
            
            if isinstance(response_data, dict):
                clientes_data = response_data.get('data', response_data.get('clientes', []))
                from models.cliente import Cliente
                clientes = [Cliente.from_dict(c) for c in clientes_data]
                return True, clientes
            
            return True, []
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except Exception as e:
            return False, f"Error al obtener clientes: {str(e)}"
    
    def obtener_dvds(self):
        """
        Obtiene la lista de DVDs disponibles
        """
        try:
            response_data = self.api_service.obtener_dvds()
            
            if isinstance(response_data, dict):
                films_data = response_data.get('data', [])
            else:
                films_data = response_data
            
            from models.dvd import DVD
            dvds = [DVD.from_dict(film) for film in films_data]
            
            return True, dvds
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except Exception as e:
            return False, f"Error al obtener DVDs: {str(e)}"
    
    def obtener_staff(self):
        """
        Obtiene la lista de staff disponible
        """
        try:
            response_data = self.api_service.obtener_staff()
            
            if isinstance(response_data, list):
                from models.staff import Staff
                staff_list = [Staff.from_dict(s) for s in response_data]
                return True, staff_list
            
            if isinstance(response_data, dict):
                staff_data = response_data.get('data', response_data.get('staff', []))
                from models.staff import Staff
                staff_list = [Staff.from_dict(s) for s in staff_data]
                return True, staff_list
            
            return True, []
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except Exception as e:
            return False, f"Error al obtener staff: {str(e)}"