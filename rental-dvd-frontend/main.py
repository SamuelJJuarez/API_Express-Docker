"""
Sistema de Renta de DVDs - Aplicación de Escritorio
Punto de entrada de la aplicación
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from views.main_window import MainWindow
from utils.config import APP_TITLE

def main():
    """
    Función principal que inicia la aplicación
    """
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    
    # Configurar el estilo (opcional, pero mejora la apariencia)
    app.setStyle('Fusion')
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar el loop de eventos de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()