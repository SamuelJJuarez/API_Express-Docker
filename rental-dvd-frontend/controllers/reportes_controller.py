"""
Controlador para reportes
"""
from services.api_service import APIService
from utils.validators import validar_id
from models.renta import Renta
import requests

class ReportesController:
    def __init__(self):
        self.api_service = APIService()
    
    def obtener_rentas_cliente(self, customer_id):
        """
        Obtiene todas las rentas de un cliente específico
        
        Args:
            customer_id: ID del cliente
        
        Returns:
            tuple: (exito, lista_rentas/mensaje_error)
        """
        try:
            # Validar ID
            valido, msg_error = validar_id(customer_id, "ID de Cliente")
            if not valido:
                return False, msg_error
            
            # Llamar al API
            response_data = self.api_service.obtener_rentas_cliente(customer_id)
            
            # ✅ MEJORADO: Manejar la respuesta correcta del backend
            if isinstance(response_data, dict):
                # El backend devuelve: {success, customer, total_rentals, rentals}
                if not response_data.get('success', False):
                    error_msg = response_data.get('message', 'Error al obtener rentas')
                    return False, error_msg
                
                # Obtener las rentas del campo 'rentals'
                rentals_data = response_data.get('rentals', [])
                
                # Convertir a objetos Renta
                rentas = []
                for rental_dict in rentals_data:
                    try:
                        renta = Renta.from_dict(rental_dict)
                        rentas.append(renta)
                    except Exception as e:
                        print(f"Error al convertir renta: {e}")
                        continue
                
                return True, rentas
            
            # Fallback si viene como lista directamente
            if isinstance(response_data, list):
                rentas = [Renta.from_dict(r) for r in response_data]
                return True, rentas
            
            return True, []
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo."
        except Exception as e:
            return False, f"Error al obtener las rentas: {str(e)}"
    
    def obtener_dvds_no_devueltos(self):
        """
        Obtiene la lista de DVDs que no se han devuelto (rentas activas)
        
        Returns:
            tuple: (exito, lista_rentas_activas/mensaje_error)
        """
        try:
            # Llamar al API
            response_data = self.api_service.obtener_dvds_no_devueltos()
            
            # Procesar respuesta
            if isinstance(response_data, dict):
                if not response_data.get('success', False):
                    error_msg = response_data.get('message', 'Error al obtener DVDs no devueltos')
                    return False, error_msg
                
                rentas_data = response_data.get('data', [])
                rentas = [Renta.from_dict(r) for r in rentas_data]
                return True, rentas
            
            if isinstance(response_data, list):
                rentas = [Renta.from_dict(r) for r in response_data]
                return True, rentas
            
            return True, []
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo."
        except Exception as e:
            return False, f"Error al obtener DVDs no devueltos: {str(e)}"
    
    def obtener_dvds_mas_rentados(self):
        """
        Obtiene el ranking de DVDs más rentados
        
        Returns:
            tuple: (exito, lista_ranking/mensaje_error)
        """
        try:
            # ✅ MEJORADO: Llamar con parámetro limit
            response_data = self.api_service.obtener_dvds_mas_rentados(limit=10)
            
            # Procesar respuesta
            if isinstance(response_data, dict):
                if not response_data.get('success', False):
                    error_msg = response_data.get('message', 'Error al obtener DVDs más rentados')
                    return False, error_msg
                
                # El backend devuelve: {success, count, generated_at, data}
                ranking_data = response_data.get('data', [])
                
                # ✅ Procesar los datos correctamente
                ranking_procesado = []
                for item in ranking_data:
                    ranking_procesado.append({
                        'titulo': item.get('title', 'N/A'),
                        'genero': item.get('category', 'N/A'),
                        'total_rentas': item.get('total_rentals', 0),
                        'film_id': item.get('film_id'),
                        'rental_rate': item.get('rental_rate'),
                        'total_revenue': item.get('total_revenue', 0)
                    })
                
                return True, ranking_procesado
            
            if isinstance(response_data, list):
                return True, response_data
            
            return True, []
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo."
        except Exception as e:
            return False, f"Error al obtener DVDs más rentados: {str(e)}"
    
    def obtener_ganancias_staff(self):
        """
        Obtiene las ganancias generadas por cada miembro del staff
        
        Returns:
            tuple: (exito, lista_ganancias/mensaje_error)
        """
        try:
            # Llamar al API
            response_data = self.api_service.obtener_ganancias_staff()
            
            # ✅ MEJORADO: Procesar respuesta correcta del backend
            if isinstance(response_data, dict):
                if not response_data.get('success', False):
                    error_msg = response_data.get('message', 'Error al obtener ganancias')
                    return False, error_msg
                
                # El backend devuelve: {success, count, total_revenue_all_staff, data}
                ganancias_data = response_data.get('data', [])
                
                # ✅ Procesar los datos correctamente
                ganancias_procesadas = []
                for item in ganancias_data:
                    ganancias_procesadas.append({
                        'nombre': item.get('staff_name', 'N/A'),
                        'staff_id': item.get('staff_id'),
                        'email': item.get('email', ''),
                        'total_rentas': item.get('total_rentals', 0),
                        'total_pagos': item.get('total_payments', 0),
                        'ganancia_total': float(item.get('total_revenue', 0)),
                        'promedio_pago': float(item.get('average_payment', 0))
                    })
                
                return True, ganancias_procesadas
            
            if isinstance(response_data, list):
                return True, response_data
            
            return True, []
            
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar con el servidor."
        except requests.exceptions.Timeout:
            return False, "La petición tardó demasiado tiempo."
        except Exception as e:
            return False, f"Error al obtener ganancias del staff: {str(e)}"
    
    def formatear_datos_tabla_rentas(self, rentals):
        """
        Formatea una lista de rentas para mostrar en una tabla
        
        Args:
            rentals: Lista de objetos Rental
        
        Returns:
            list: Lista de listas con datos formateados para tabla
        """
        datos_tabla = []
        
        for renta in rentals:
            # Obtener nombres de entidades relacionadas
            cliente_nombre = renta.cliente.nombre if renta.cliente else f"ID: {renta.customer_id}"
            dvd_titulo = renta.dvd.titulo if renta.dvd else f"ID: {renta.film_id}"
            staff_nombre = renta.staff.nombre if renta.staff else f"ID: {renta.staff_id}"
            
            # Calcular días de retraso si aplica
            dias_retraso = ""
            if renta.estado == 'activa':
                dias = renta.calcular_dias_retraso()
                if dias > 0:
                    dias_retraso = f"{dias} días"
            
            # Formato de fecha de devolución real
            fecha_devolucion = renta.fecha_devolucion_real if renta.fecha_devolucion_real else "Pendiente"
            
            datos_tabla.append([
                renta.id,
                dvd_titulo,
                staff_nombre,
                renta.fecha_renta,
                renta.fecha_devolucion_esperada,
                fecha_devolucion,
                f"${renta.monto:.2f}",
                renta.estado.capitalize(),
                dias_retraso
            ])
        
        return datos_tabla
    
    def formatear_datos_tabla_ranking(self, ranking_data):
        """
        Formatea los datos del ranking de DVDs para tabla
        
        Args:
            ranking_data: Lista de diccionarios con datos del ranking
        
        Returns:
            list: Lista de listas con datos formateados
        """
        datos_tabla = []
        
        for item in ranking_data:
            # ✅ MEJORADO: Usar los campos correctos del backend
            if isinstance(item, dict):
                titulo = item.get('titulo', item.get('title', 'N/A'))
                genero = item.get('genero', item.get('category', 'N/A'))
                
                # ✅ CRÍTICO: Convertir total_rentas a int
                total_rentas_raw = item.get('total_rentas', item.get('total_rentals', 0))
                try:
                    total_rentas = int(total_rentas_raw)
                except (ValueError, TypeError):
                    total_rentas = 0
                
                datos_tabla.append([
                    titulo,
                    genero,
                    total_rentas
                ])
        
        return datos_tabla
    
    def formatear_datos_tabla_ganancias(self, ganancias_data):
        """
        Formatea los datos de ganancias del staff para tabla
        
        Args:
            ganancias_data: Lista de diccionarios con datos de ganancias
        
        Returns:
            list: Lista de listas con datos formateados
        """
        datos_tabla = []
        
        for item in ganancias_data:
            # ✅ MEJORADO: Usar los campos correctos del backend
            if isinstance(item, dict):
                nombre = item.get('nombre', item.get('staff_name', 'N/A'))
                
                # ✅ CRÍTICO: Convertir total_rentas a int
                total_rentas_raw = item.get('total_rentas', item.get('total_rentals', 0))
                try:
                    total_rentas = int(total_rentas_raw)
                except (ValueError, TypeError):
                    total_rentas = 0
                
                # ✅ CRÍTICO: Convertir ganancia_total a float
                ganancia_raw = item.get('ganancia_total', item.get('total_revenue', 0))
                try:
                    ganancia_total = float(ganancia_raw)
                except (ValueError, TypeError):
                    ganancia_total = 0.0
                
                datos_tabla.append([
                    nombre,
                    total_rentas,
                    f"${ganancia_total:.2f}"
                ])
        
        return datos_tabla