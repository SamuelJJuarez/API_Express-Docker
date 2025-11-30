"""
Modelo de Staff (Empleado)
"""

class Staff:
    def __init__(self, id=None, first_name="", last_name="", email="", 
                 active=True, username="", store_id=None, address=None,
                 staff_id=None):
        
        # Usar staff_id si se proporciona, sino usar id
        self.id = staff_id or id
        self.staff_id = self.id
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.active = active
        self.username = username
        self.store_id = store_id
        self.address = address
        
        # Propiedades de compatibilidad
        self.nombre = f"{first_name} {last_name}".strip()
        self.comision = 0.0  # No existe en la BD estándar
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Staff desde un diccionario (respuesta del API)
        """
        if not data:
            return None
        
        # ✅ Manejar múltiples formatos de ID
        staff_id = data.get('staff_id') or data.get('id')
        
        # ✅ Manejar nombre completo o first_name/last_name
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Si viene 'name' en lugar de first_name/last_name
        if 'name' in data and not first_name:
            parts = data['name'].split(' ', 1)
            first_name = parts[0] if len(parts) > 0 else ''
            last_name = parts[1] if len(parts) > 1 else ''
        
        # ✅ Si viene 'staff_name' (como en algunos reportes)
        if 'staff_name' in data and not first_name:
            parts = data['staff_name'].split(' ', 1)
            first_name = parts[0] if len(parts) > 0 else ''
            last_name = parts[1] if len(parts) > 1 else ''
        
        return cls(
            id=staff_id,
            first_name=first_name,
            last_name=last_name,
            email=data.get('email', ''),
            active=data.get('active', True),
            username=data.get('username', ''),
            store_id=data.get('store_id'),
            address=data.get('address')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a diccionario (para enviar al API)
        """
        return {
            'staff_id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'active': self.active,
            'username': self.username,
            'store_id': self.store_id
        }
    
    def __str__(self):
        return self.nombre if self.nombre else f"Staff #{self.id}"
    
    def __repr__(self):
        return f"Staff(id={self.id}, nombre='{self.nombre}')"