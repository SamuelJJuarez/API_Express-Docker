"""
Modelo de Renta
"""
from datetime import datetime, timedelta

class Renta:
    def __init__(self, id=None, rental_date=None, return_date=None, 
                 customer_id=None, staff_id=None, film_id=None,
                 title=None, rental_rate=None, estado="activa",
                 expected_return_date=None, rental_duration=3,
                 estimated_amount=None, days_rented=0,
                 customer_name=None, staff_name=None):
        
        self.id = id
        self.rental_id = id  # Alias
        
        # Fechas
        self.rental_date = rental_date
        self.return_date = return_date
        self.fecha_renta = self._format_date(rental_date)
        self.fecha_devolucion_real = self._format_date(return_date) if return_date else None
        
        # ✅ CRÍTICO: Fecha de devolución esperada
        self.expected_return_date = expected_return_date
        self.fecha_devolucion_esperada = self._format_date(expected_return_date) if expected_return_date else None
        
        # IDs
        self.customer_id = customer_id
        self.staff_id = staff_id
        self.film_id = film_id
        self.dvd_id = film_id  # Alias
        
        # Información de película
        self.title = title
        self.rental_rate = float(rental_rate) if rental_rate else 0.0
        self.precio_renta = self.rental_rate
        self.rental_duration = int(rental_duration) if rental_duration else 3
        
        # ✅ CRÍTICO: Monto
        if estimated_amount is not None:
            self.monto = float(estimated_amount)
        elif rental_rate is not None:
            self.monto = float(rental_rate)
        else:
            self.monto = 0.0
        
        self.estimated_amount = self.monto
        
        # Estado
        self.estado = "devuelta" if return_date else estado
        self.days_rented = int(days_rented) if days_rented else 0
        
        # Nombres directos (fallback si no vienen objetos)
        self.customer_name = customer_name
        self.staff_name = staff_name
        
        # Objetos relacionados (se llenan en from_dict)
        self.cliente = None
        self.dvd = None
        self.staff = None
    
    def _format_date(self, date_value):
        """
        Formatea una fecha para mostrar en el frontend
        """
        if not date_value:
            return None
        
        if isinstance(date_value, str):
            try:
                # Parsear fecha ISO: 2025-11-28T15:45:03.641Z
                dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                try:
                    # Intentar solo la fecha
                    dt = datetime.strptime(date_value[:10], '%Y-%m-%d')
                    return dt.strftime('%Y-%m-%d')
                except:
                    return date_value
        
        return str(date_value)
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Renta desde un diccionario (respuesta del API)
        """
        from models.cliente import Cliente
        from models.dvd import DVD
        from models.staff import Staff
        
        if not data:
            return None
        
        # ✅ Extraer datos básicos
        rental_id = data.get('rental_id') or data.get('id')
        rental_date = data.get('rental_date')
        return_date = data.get('return_date')
        customer_id = data.get('customer_id')
        staff_id = data.get('staff_id')
        
        # ✅ Film ID puede venir en varios lugares
        film_id = data.get('film_id')
        if not film_id and 'film' in data and isinstance(data['film'], dict):
            film_id = data['film'].get('film_id')
        
        # ✅ CRÍTICO: Expected return date
        expected_return_date = data.get('expected_return_date')
        
        # Si no viene, calcular basado en rental_duration
        if not expected_return_date and rental_date:
            rental_duration = data.get('rental_duration', 3)
            if 'film' in data and isinstance(data['film'], dict):
                rental_duration = data['film'].get('rental_duration', rental_duration)
            
            try:
                dt = datetime.fromisoformat(rental_date.replace('Z', '+00:00'))
                expected_dt = dt + timedelta(days=int(rental_duration))
                expected_return_date = expected_dt.isoformat()
            except:
                pass
        
        # ✅ Información financiera
        rental_rate = data.get('rental_rate')
        if not rental_rate and 'film' in data and isinstance(data['film'], dict):
            rental_rate = data['film'].get('rental_rate')
        
        estimated_amount = data.get('estimated_amount')
        if not estimated_amount:
            estimated_amount = data.get('total_amount')
        
        rental_duration = data.get('rental_duration', 3)
        if 'film' in data and isinstance(data['film'], dict):
            rental_duration = data['film'].get('rental_duration', rental_duration)
        
        # ✅ Título
        title = data.get('title')
        if not title and 'film' in data and isinstance(data['film'], dict):
            title = data['film'].get('title')
        
        # ✅ Días rentados
        days_rented = data.get('days_rented', 0)
        
        # ✅ Nombres directos
        customer_name = data.get('customer_name')
        staff_name = data.get('staff_name')
        
        # Crear instancia
        renta = cls(
            id=rental_id,
            rental_date=rental_date,
            return_date=return_date,
            customer_id=customer_id,
            staff_id=staff_id,
            film_id=film_id,
            title=title,
            rental_rate=rental_rate,
            estado="activa",
            expected_return_date=expected_return_date,
            rental_duration=rental_duration,
            estimated_amount=estimated_amount,
            days_rented=days_rented,
            customer_name=customer_name,
            staff_name=staff_name
        )
        
        # ✅ CRÍTICO: Crear objetos relacionados
        
        # Cliente
        if 'customer' in data and isinstance(data['customer'], dict):
            renta.cliente = Cliente.from_dict(data['customer'])
        elif customer_id:
            # Crear objeto mínimo si solo tenemos el nombre
            if customer_name:
                parts = customer_name.split(' ', 1)
                renta.cliente = Cliente(
                    id=customer_id,
                    first_name=parts[0] if len(parts) > 0 else '',
                    last_name=parts[1] if len(parts) > 1 else '',
                    email=data.get('email', data.get('customer_email', ''))
                )
        
        # DVD/Film
        if 'film' in data and isinstance(data['film'], dict):
            renta.dvd = DVD.from_dict(data['film'])
        elif film_id and title:
            # Crear objeto mínimo
            renta.dvd = DVD(
                id=film_id,
                title=title,
                rental_rate=rental_rate or 0.0
            )
        
        # Staff
        if 'staff' in data and isinstance(data['staff'], dict):
            renta.staff = Staff.from_dict(data['staff'])
        elif staff_id:
            # Crear objeto mínimo si solo tenemos el nombre
            if staff_name:
                parts = staff_name.split(' ', 1)
                renta.staff = Staff(
                    id=staff_id,
                    first_name=parts[0] if len(parts) > 0 else '',
                    last_name=parts[1] if len(parts) > 1 else '',
                    email=data.get('staff_email', '')
                )
        
        return renta
    
    def to_dict(self):
        """
        Convierte la instancia a diccionario (para enviar al API)
        """
        return {
            'rental_id': self.id,
            'customer_id': self.customer_id,
            'film_id': self.film_id,
            'staff_id': self.staff_id,
            'rental_date': self.rental_date,
            'return_date': self.return_date
        }
    
    def calcular_dias_retraso(self):
        """
        Calcula los días de retraso si la renta no se ha devuelto
        """
        if self.return_date or not self.fecha_devolucion_esperada:
            return 0
        
        try:
            # Parsear fecha esperada
            if isinstance(self.fecha_devolucion_esperada, str):
                fecha_esperada = datetime.strptime(
                    self.fecha_devolucion_esperada[:10], 
                    '%Y-%m-%d'
                )
            else:
                fecha_esperada = self.fecha_devolucion_esperada
            
            # Comparar con hoy
            hoy = datetime.now()
            dias_retraso = (hoy - fecha_esperada).days
            
            return max(0, dias_retraso)
        except Exception as e:
            print(f"Error calculando días de retraso: {e}")
            return 0
    
    def calcular_dias_desde_renta(self):
        """
        Calcula los días desde que se realizó la renta
        """
        if not self.rental_date:
            return 0
        
        try:
            if isinstance(self.rental_date, str):
                fecha_renta = datetime.fromisoformat(self.rental_date.replace('Z', '+00:00'))
            else:
                fecha_renta = self.rental_date
            
            hoy = datetime.now()
            dias = (hoy - fecha_renta.replace(tzinfo=None)).days
            
            return max(0, dias)
        except Exception as e:
            print(f"Error calculando días desde renta: {e}")
            return 0
    
    def __str__(self):
        cliente_str = self.cliente.nombre if self.cliente else (self.customer_name or f"ID: {self.customer_id}")
        dvd_str = self.dvd.titulo if self.dvd else (self.title or f"ID: {self.film_id}")
        return f"Renta #{self.id} - {dvd_str} - {cliente_str} - {self.estado}"
    
    def __repr__(self):
        return f"Renta(id={self.id}, customer_id={self.customer_id}, estado='{self.estado}')"