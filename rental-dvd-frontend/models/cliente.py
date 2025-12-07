"""
Modelo de Cliente
"""

class Cliente:
    def __init__(self, id=None, first_name="", last_name="", email="", 
                 active=1, create_date=None, customer_id=None):
        # Usar customer_id si se proporciona, sino usar id
        self.id = customer_id or id
        self.customer_id = self.id
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.active = active
        self.create_date = create_date
        
        # Propiedades de compatibilidad
        self.nombre = f"{first_name} {last_name}".strip()
        self.telefono = ""  # No existe en la BD DVD Rental
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Cliente desde un diccionario (respuesta del API)
        """
        if not data:
            return None
        
        # ✅ Manejar múltiples formatos de ID
        customer_id = data.get('customer_id') or data.get('id')
        
        # ✅ Manejar nombre completo o first_name/last_name
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Si viene 'name' en lugar de first_name/last_name
        if 'name' in data and not first_name:
            parts = data['name'].split(' ', 1)
            first_name = parts[0] if len(parts) > 0 else ''
            last_name = parts[1] if len(parts) > 1 else ''
        
        return cls(
            id=customer_id,
            first_name=first_name,
            last_name=last_name,
            email=data.get('email', ''),
            active=data.get('active', 1),
            create_date=data.get('create_date')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a diccionario (para enviar al API)
        """
        return {
            'customer_id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'active': self.active
        }
    
    def __str__(self):
        return f"{self.nombre} ({self.email})" if self.email else self.nombre
    
    def __repr__(self):
        return f"Cliente(id={self.id}, nombre='{self.nombre}')"