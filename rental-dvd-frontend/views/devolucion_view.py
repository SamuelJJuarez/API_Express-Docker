"""
Vista para procesar devoluciones de DVDs
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from controllers.renta_controller import RentaController
from controllers.reportes_controller import ReportesController

class DevolucionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = RentaController()
        self.reportes_controller = ReportesController()
        self.rentas_activas = []
        self.init_ui()
    
    def init_ui(self):
        """
        Inicializa la interfaz de usuario
        """
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("↩️ Procesar Devolución de DVD")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Grupo de búsqueda
        busqueda_group = QGroupBox("Buscar Renta")
        busqueda_layout = QHBoxLayout()
        
        self.input_renta_id = QLineEdit()
        self.input_renta_id.setPlaceholderText("Ingresa el ID de la renta")
        busqueda_layout.addWidget(QLabel("ID de Renta:"))
        busqueda_layout.addWidget(self.input_renta_id)
        
        btn_buscar = QPushButton("🔍 Buscar")
        btn_buscar.clicked.connect(self.buscar_renta)
        busqueda_layout.addWidget(btn_buscar)
        
        btn_ver_todas = QPushButton("📋 Ver Todas las Rentas Activas")
        btn_ver_todas.clicked.connect(self.cargar_rentas_activas)
        busqueda_layout.addWidget(btn_ver_todas)
        
        busqueda_group.setLayout(busqueda_layout)
        layout.addWidget(busqueda_group)
        
        # Tabla de rentas activas
        self.tabla_rentas = QTableWidget()
        self.tabla_rentas.setColumnCount(6)
        self.tabla_rentas.setHorizontalHeaderLabels([
            "ID", "Cliente", "DVD", "Fecha Renta", 
            "Fecha Devolución Esperada", "Días de Retraso"
        ])
        self.tabla_rentas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_rentas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_rentas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_rentas)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        
        btn_inicio = QPushButton("🏠 Volver al Inicio")
        btn_inicio.clicked.connect(self.volver_inicio)
        botones_layout.addWidget(btn_inicio)
        
        botones_layout.addStretch()
        
        btn_devolver = QPushButton("✅ Procesar Devolución")
        btn_devolver.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        btn_devolver.clicked.connect(self.procesar_devolucion)
        botones_layout.addWidget(btn_devolver)
        
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)
    
    def buscar_renta(self):
        """
        Busca una renta específica por ID
        """
        renta_id = self.input_renta_id.text().strip()
        
        if not renta_id:
            QMessageBox.warning(self, "Validación", "Por favor ingresa un ID de renta")
            return
        
        # Cargar todas las rentas activas y filtrar
        self.cargar_rentas_activas(filtrar_id=renta_id)
    
    def cargar_rentas_activas(self, filtrar_id=None):
        """
        Carga todas las rentas activas en la tabla
        
        Args:
            filtrar_id: Si se proporciona, filtra por este ID
        """
        exito, resultado = self.reportes_controller.obtener_dvds_no_devueltos()
        
        if not exito:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las rentas:\n{resultado}")
            return
        
        self.rentas_activas = resultado
        
        # Filtrar si se especificó un ID
        if filtrar_id:
            try:
                filtrar_id = int(filtrar_id)
                self.rentas_activas = [r for r in self.rentas_activas if r.id == filtrar_id]
                if not self.rentas_activas:
                    QMessageBox.information(self, "No encontrado", f"No se encontró una renta activa con ID {filtrar_id}")
            except ValueError:
                QMessageBox.warning(self, "Error", "El ID debe ser un número")
                return
        
        # Limpiar tabla
        self.tabla_rentas.setRowCount(0)
        
        # Llenar tabla
        for renta in self.rentas_activas:
            row = self.tabla_rentas.rowCount()
            self.tabla_rentas.insertRow(row)
            
            cliente_nombre = renta.cliente.nombre if renta.cliente else f"ID: {renta.customer_id}"
            dvd_titulo = renta.dvd.titulo if renta.dvd else f"ID: {renta.dvd_id}"
            dias_retraso = renta.calcular_dias_retraso()
            
            self.tabla_rentas.setItem(row, 0, QTableWidgetItem(str(renta.id)))
            self.tabla_rentas.setItem(row, 1, QTableWidgetItem(cliente_nombre))
            self.tabla_rentas.setItem(row, 2, QTableWidgetItem(dvd_titulo))
            self.tabla_rentas.setItem(row, 3, QTableWidgetItem(renta.fecha_renta))
            self.tabla_rentas.setItem(row, 4, QTableWidgetItem(renta.fecha_devolucion_esperada))
            
            # Colorear días de retraso
            item_retraso = QTableWidgetItem(f"{dias_retraso} días" if dias_retraso > 0 else "A tiempo")
            if dias_retraso > 0:
                item_retraso.setBackground(Qt.GlobalColor.red)
                item_retraso.setForeground(Qt.GlobalColor.white)
            self.tabla_rentas.setItem(row, 5, item_retraso)
        
        if not self.rentas_activas:
            QMessageBox.information(self, "Sin Rentas", "No hay rentas activas en este momento")
    
    def procesar_devolucion(self):
        """
        Procesa la devolución de la renta seleccionada
        """
        # Obtener fila seleccionada
        filas_seleccionadas = self.tabla_rentas.selectedItems()
        if not filas_seleccionadas:
            QMessageBox.warning(self, "Validación", "Por favor selecciona una renta de la tabla")
            return
        
        # Obtener ID de la renta seleccionada
        fila = self.tabla_rentas.currentRow()
        renta_id = int(self.tabla_rentas.item(fila, 0).text())
        
        # Confirmar
        respuesta = QMessageBox.question(
            self,
            "Confirmar Devolución",
            f"¿Confirmas la devolución de la renta #{renta_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # Procesar devolución
            exito, mensaje, renta = self.controller.devolver_renta(renta_id)
            
            if exito:
                QMessageBox.information(self, "Éxito", mensaje)
                # Recargar tabla
                self.cargar_rentas_activas()
                self.input_renta_id.clear()
            else:
                QMessageBox.critical(self, "Error", mensaje)
    
    def volver_inicio(self):
        """
        Regresa a la pantalla de inicio
        """
        # Buscar la ventana principal (MainWindow)
        widget = self
        while widget:
            widget = widget.parent()
            if widget and widget.__class__.__name__ == 'MainWindow':
                if hasattr(widget, 'ir_a_inicio'):
                    widget.ir_a_inicio()
                break