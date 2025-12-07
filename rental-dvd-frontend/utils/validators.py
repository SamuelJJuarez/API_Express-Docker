"""
Validadores para formularios
"""
from datetime import datetime

def validar_campo_vacio(valor, nombre_campo):
    """
    Valida que un campo no esté vacío
    
    Args:
        valor: El valor a validar
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if not valor or str(valor).strip() == "":
        return False, f"El campo '{nombre_campo}' es obligatorio"
    return True, ""

def validar_numero_positivo(valor, nombre_campo):
    """
    Valida que un valor sea un número positivo
    
    Args:
        valor: El valor a validar
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        numero = float(valor)
        if numero <= 0:
            return False, f"El campo '{nombre_campo}' debe ser mayor a 0"
        return True, ""
    except (ValueError, TypeError):
        return False, f"El campo '{nombre_campo}' debe ser un número válido"

def validar_id(valor, nombre_campo):
    """
    Valida que un ID sea un número entero positivo
    
    Args:
        valor: El valor a validar
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        id_num = int(valor)
        if id_num <= 0:
            return False, f"El '{nombre_campo}' debe ser mayor a 0"
        return True, ""
    except (ValueError, TypeError):
        return False, f"El '{nombre_campo}' debe ser un número válido"

def validar_fecha(fecha_str, nombre_campo):
    """
    Valida que una fecha tenga formato válido
    
    Args:
        fecha_str: String de fecha en formato YYYY-MM-DD
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe tener formato YYYY-MM-DD"

def validar_fecha_futura(fecha_str, nombre_campo):
    """
    Valida que una fecha sea futura (posterior a hoy)
    
    Args:
        fecha_str: String de fecha en formato YYYY-MM-DD
        nombre_campo: Nombre del campo para el mensaje de error
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        if fecha.date() <= datetime.now().date():
            return False, f"El campo '{nombre_campo}' debe ser una fecha futura"
        return True, ""
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe tener formato YYYY-MM-DD"