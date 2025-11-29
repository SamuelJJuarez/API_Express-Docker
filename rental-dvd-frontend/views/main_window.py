"""
Ventana principal de la aplicación
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QMenuBar, QMenu, QMessageBox,
    QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from utils.config import APP_TITLE, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} - v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Widget central con stack para cambiar entre vistas
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Stack de widgets para las diferentes vistas
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Crear la página de inicio
        self.crear_pagina_inicio()
        
        # Crear menú
        self.crear_menu()
        
        # Barra de estado
        self.statusBar().showMessage("Listo")
    
    def crear_pagina_inicio(self):
        """
        Crea la página de inicio/bienvenida
        """
        inicio_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        titulo = QLabel(APP_TITLE)
        titulo_font = QFont()
        titulo_font.setPointSize(24)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel(f"Versión {APP_VERSION}")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)
        
        # Espacio
        layout.addSpacing(50)
        
        # Botones principales
        btn_nueva_renta = QPushButton("📀 Nueva Renta")
        btn_nueva_renta.setMinimumHeight(50)
        btn_nueva_renta.clicked.connect(self.abrir_nueva_renta)
        layout.addWidget(btn_nueva_renta)
        
        btn_devolucion = QPushButton("↩️ Procesar Devolución")
        btn_devolucion.setMinimumHeight(50)
        btn_devolucion.clicked.connect(self.abrir_devolucion)
        layout.addWidget(btn_devolucion)
        
        btn_cancelar = QPushButton("❌ Cancelar Renta")
        btn_cancelar.setMinimumHeight(50)
        btn_cancelar.clicked.connect(self.abrir_cancelar_renta)
        layout.addWidget(btn_cancelar)
        
        btn_reportes = QPushButton("📊 Ver Reportes")
        btn_reportes.setMinimumHeight(50)
        btn_reportes.clicked.connect(self.mostrar_menu_reportes)
        layout.addWidget(btn_reportes)
        
        # Añadir stretch para centrar
        layout.addStretch()
        
        inicio_widget.setLayout(layout)
        self.stacked_widget.addWidget(inicio_widget)
        self.pagina_inicio = inicio_widget
    
    def crear_menu(self):
        """
        Crea el menú de la aplicación
        """
        menubar = self.menuBar()
        
        # Menú Rentas
        menu_rentas = menubar.addMenu("&Rentas")
        
        accion_nueva_renta = QAction("Nueva Renta", self)
        accion_nueva_renta.setShortcut("Ctrl+N")
        accion_nueva_renta.triggered.connect(self.abrir_nueva_renta)
        menu_rentas.addAction(accion_nueva_renta)
        
        accion_devolucion = QAction("Procesar Devolución", self)
        accion_devolucion.setShortcut("Ctrl+D")
        accion_devolucion.triggered.connect(self.abrir_devolucion)
        menu_rentas.addAction(accion_devolucion)
        
        accion_cancelar = QAction("Cancelar Renta", self)
        accion_cancelar.setShortcut("Ctrl+X")
        accion_cancelar.triggered.connect(self.abrir_cancelar_renta)
        menu_rentas.addAction(accion_cancelar)
        
        menu_rentas.addSeparator()
        
        accion_salir = QAction("Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.triggered.connect(self.close)
        menu_rentas.addAction(accion_salir)
        
        # Menú Reportes
        menu_reportes = menubar.addMenu("&Reportes")
        
        accion_rentas_cliente = QAction("Rentas por Cliente", self)
        accion_rentas_cliente.triggered.connect(self.abrir_reporte_cliente)
        menu_reportes.addAction(accion_rentas_cliente)
        
        accion_no_devueltos = QAction("DVDs No Devueltos", self)
        accion_no_devueltos.triggered.connect(self.abrir_reporte_no_devueltos)
        menu_reportes.addAction(accion_no_devueltos)
        
        accion_mas_rentados = QAction("DVDs Más Rentados", self)
        accion_mas_rentados.triggered.connect(self.abrir_reporte_mas_rentados)
        menu_reportes.addAction(accion_mas_rentados)
        
        accion_ganancias = QAction("Ganancias por Staff", self)
        accion_ganancias.triggered.connect(self.abrir_reporte_ganancias)
        menu_reportes.addAction(accion_ganancias)
        
        # Menú Ayuda
        menu_ayuda = menubar.addMenu("&Ayuda")
        
        accion_inicio = QAction("Ir al Inicio", self)
        accion_inicio.setShortcut("Ctrl+H")
        accion_inicio.triggered.connect(self.ir_a_inicio)
        menu_ayuda.addAction(accion_inicio)
        
        accion_acerca_de = QAction("Acerca de", self)
        accion_acerca_de.triggered.connect(self.mostrar_acerca_de)
        menu_ayuda.addAction(accion_acerca_de)
    
    def ir_a_inicio(self):
        """
        Regresa a la página de inicio
        """
        self.stacked_widget.setCurrentWidget(self.pagina_inicio)
        self.statusBar().showMessage("Inicio")
    
    def abrir_nueva_renta(self):
        """
        Abre la ventana para crear una nueva renta
        """
        from views.renta_view import RentaView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), RentaView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Nueva Renta")
                return
        
        # Crear nueva vista
        renta_view = RentaView(self)
        self.stacked_widget.addWidget(renta_view)
        self.stacked_widget.setCurrentWidget(renta_view)
        self.statusBar().showMessage("Nueva Renta")
    
    def abrir_devolucion(self):
        """
        Abre la ventana para procesar devoluciones
        """
        from views.devolucion_view import DevolucionView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), DevolucionView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Procesar Devolución")
                return
        
        # Crear nueva vista
        devolucion_view = DevolucionView(self)
        self.stacked_widget.addWidget(devolucion_view)
        self.stacked_widget.setCurrentWidget(devolucion_view)
        self.statusBar().showMessage("Procesar Devolución")
    
    def abrir_cancelar_renta(self):
        """
        Abre la ventana para cancelar rentas
        """
        from views.cancelar_view import CancelarView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), CancelarView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Cancelar Renta")
                return
        
        # Crear nueva vista
        cancelar_view = CancelarView(self)
        self.stacked_widget.addWidget(cancelar_view)
        self.stacked_widget.setCurrentWidget(cancelar_view)
        self.statusBar().showMessage("Cancelar Renta")
    
    def mostrar_menu_reportes(self):
        """
        Muestra un diálogo con opciones de reportes
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Reportes Disponibles")
        msg.setText("Selecciona un reporte del menú 'Reportes' en la barra superior")
        msg.setInformativeText(
            "• Rentas por Cliente\n"
            "• DVDs No Devueltos\n"
            "• DVDs Más Rentados\n"
            "• Ganancias por Staff"
        )
        msg.exec()
    
    def abrir_reporte_cliente(self):
        """
        Abre el reporte de rentas por cliente
        """
        from views.reportes.cliente_view import ClienteReporteView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), ClienteReporteView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Reporte: Rentas por Cliente")
                return
        
        # Crear nueva vista
        reporte_view = ClienteReporteView(self)
        self.stacked_widget.addWidget(reporte_view)
        self.stacked_widget.setCurrentWidget(reporte_view)
        self.statusBar().showMessage("Reporte: Rentas por Cliente")
    
    def abrir_reporte_no_devueltos(self):
        """
        Abre el reporte de DVDs no devueltos
        """
        from views.reportes.no_devueltos_view import NoDevueltosReporteView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), NoDevueltosReporteView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Reporte: DVDs No Devueltos")
                return
        
        # Crear nueva vista
        reporte_view = NoDevueltosReporteView(self)
        self.stacked_widget.addWidget(reporte_view)
        self.stacked_widget.setCurrentWidget(reporte_view)
        self.statusBar().showMessage("Reporte: DVDs No Devueltos")
    
    def abrir_reporte_mas_rentados(self):
        """
        Abre el reporte de DVDs más rentados
        """
        from views.reportes.mas_rentados_view import MasRentadosReporteView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), MasRentadosReporteView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Reporte: DVDs Más Rentados")
                return
        
        # Crear nueva vista
        reporte_view = MasRentadosReporteView(self)
        self.stacked_widget.addWidget(reporte_view)
        self.stacked_widget.setCurrentWidget(reporte_view)
        self.statusBar().showMessage("Reporte: DVDs Más Rentados")
    
    def abrir_reporte_ganancias(self):
        """
        Abre el reporte de ganancias por staff
        """
        from views.reportes.ganancias_view import GananciasReporteView
        
        # Verificar si ya existe la vista
        for i in range(self.stacked_widget.count()):
            if isinstance(self.stacked_widget.widget(i), GananciasReporteView):
                self.stacked_widget.setCurrentIndex(i)
                self.statusBar().showMessage("Reporte: Ganancias por Staff")
                return
        
        # Crear nueva vista
        reporte_view = GananciasReporteView(self)
        self.stacked_widget.addWidget(reporte_view)
        self.stacked_widget.setCurrentWidget(reporte_view)
        self.statusBar().showMessage("Reporte: Ganancias por Staff")
    
    def mostrar_acerca_de(self):
        """
        Muestra información acerca de la aplicación
        """
        QMessageBox.about(
            self,
            "Acerca de",
            f"<h2>{APP_TITLE}</h2>"
            f"<p>Versión {APP_VERSION}</p>"
            "<p>Sistema de gestión de rentas de DVDs</p>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Gestión de rentas</li>"
            "<li>Devoluciones y cancelaciones</li>"
            "<li>Reportes detallados</li>"
            "</ul>"
        )