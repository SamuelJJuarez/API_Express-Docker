"""
Modelo de DVD
"""

class DVD:
    def __init__(self, id=None, title="", description="", rating="", 
                 rental_rate=0.0, release_year=None, length=None, 
                 rental_duration=3, film_id=None, category=None):
        
        # Usar film_id si se proporciona, sino usar id
        self.id = film_id or id
        self.film_id = self.id
        
        self.title = title
        self.description = description
        self.rating = rating
        self.rental_rate = float(rental_rate) if rental_rate else 0.0
        self.release_year = release_year
        self.length = length
        self.rental_duration = int(rental_duration) if rental_duration else 3
        self.category = category
        
        # Propiedades de compatibilidad con el frontend español
        self.titulo = title
        self.genero = category or rating
        self.precio_renta = self.rental_rate
        self.anio = release_year
        self.duracion_renta = self.rental_duration
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de DVD desde un diccionario (respuesta del API)
        """
        if not data:
            return None
        
        # ✅ Manejar múltiples formatos de ID
        film_id = data.get('film_id') or data.get('id')
        
        return cls(
            id=film_id,
            title=data.get('title', ''),
            description=data.get('description', ''),
            rating=data.get('rating', ''),
            rental_rate=data.get('rental_rate', 0.0),
            release_year=data.get('release_year'),
            length=data.get('length'),
            rental_duration=data.get('rental_duration', 3),
            category=data.get('category')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a diccionario (para enviar al API)
        """
        return {
            'film_id': self.id,
            'title': self.title,
            'description': self.description,
            'rating': self.rating,
            'rental_rate': self.rental_rate,
            'release_year': self.release_year,
            'length': self.length,
            'rental_duration': self.rental_duration
        }
    
    def __str__(self):
        return f"{self.title} ({self.release_year}) - ${self.rental_rate}/día"
    
    def __repr__(self):
        return f"DVD(id={self.id}, title='{self.title}')"