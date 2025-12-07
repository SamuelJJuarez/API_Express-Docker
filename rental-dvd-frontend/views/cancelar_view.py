"""
Vista para cancelar rentas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from controllers.renta_controller import RentaController
from controllers.reportes_controller import ReportesController

class CancelarView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = RentaController()
        self.reportes_controller = ReportesController()
        self.renta_actual = None
        self.init_ui()
    
    def init_ui(self):
        """
        Inicializa la interfaz de usuario
        """
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("❌ Cancelar Renta")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Advertencia
        advertencia = QLabel("⚠️ ADVERTENCIA: Esta acción no se puede deshacer")
        advertencia.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
        layout.addWidget(advertencia)
        
        # Grupo de búsqueda
        busqueda_group = QGroupBox("Buscar Renta a Cancelar")
        busqueda_layout = QHBoxLayout()
        
        self.input_renta_id = QLineEdit()
        self.input_renta_id.setPlaceholderText("Ingresa el ID de la renta")
        busqueda_layout.addWidget(QLabel("ID de Renta:"))
        busqueda_layout.addWidget(self.input_renta_id)
        
        btn_buscar = QPushButton("🔍 Buscar")
        btn_buscar.clicked.connect(self.buscar_renta)
        busqueda_layout.addWidget(btn_buscar)
        
        busqueda_group.setLayout(busqueda_layout)
        layout.addWidget(busqueda_group)
        
        # Detalles de la renta
        detalles_group = QGroupBox("Detalles de la Renta")
        detalles_layout = QVBoxLayout()
        
        self.text_detalles = QTextEdit()
        self.text_detalles.setReadOnly(True)
        self.text_detalles.setMaximumHeight(200)
        self.text_detalles.setText("Busca una renta para ver sus detalles...")
        detalles_layout.addWidget(self.text_detalles)
        
        detalles_group.setLayout(detalles_layout)
        layout.addWidget(detalles_group)
        
        # Motivo de cancelación
        motivo_group = QGroupBox("Motivo de Cancelación (opcional)")
        motivo_layout = QVBoxLayout()
        
        self.text_motivo = QTextEdit()
        self.text_motivo.setPlaceholderText("Ingresa el motivo de la cancelación...")
        self.text_motivo.setMaximumHeight(100)
        motivo_layout.addWidget(self.text_motivo)
        
        motivo_group.setLayout(motivo_layout)
        layout.addWidget(motivo_group)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        
        btn_inicio = QPushButton("🏠 Volver al Inicio")
        btn_inicio.clicked.connect(self.volver_inicio)
        botones_layout.addWidget(btn_inicio)
        
        botones_layout.addStretch()
        
        btn_limpiar = QPushButton("🔄 Limpiar")
        btn_limpiar.clicked.connect(self.limpiar)
        botones_layout.addWidget(btn_limpiar)
        
        self.btn_cancelar = QPushButton("❌ CANCELAR RENTA")
        self.btn_cancelar.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-weight: bold;")
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.clicked.connect(self.cancelar_renta)
        botones_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(botones_layout)
        
        # Espacio adicional
        layout.addStretch()
        
        self.setLayout(layout)
    
    def buscar_renta(self):
        """
        Busca una renta por ID y muestra sus detalles
        """
        renta_id = self.input_renta_id.text().strip()
        
        if not renta_id:
            QMessageBox.warning(self, "Validación", "Por favor ingresa un ID de renta")
            return
        
        try:
            renta_id = int(renta_id)
        except ValueError:
            QMessageBox.warning(self, "Validación", "El ID debe ser un número válido")
            return
        
        # Buscar la renta en las rentas activas
        exito, resultado = self.reportes_controller.obtener_dvds_no_devueltos()
        
        if not exito:
            QMessageBox.critical(self, "Error", f"No se pudo buscar la renta:\n{resultado}")
            return
        
        # Buscar en los resultados
        renta_encontrada = None
        for renta in resultado:
            if renta.id == renta_id:
                renta_encontrada = renta
                break
        
        if not renta_encontrada:
            QMessageBox.warning(
                self, 
                "No encontrada", 
                f"No se encontró una renta activa con ID {renta_id}\n\n"
                "Solo se pueden cancelar rentas activas (no devueltas)."
            )
            self.limpiar()
            return
        
        # Guardar renta actual
        self.renta_actual = renta_encontrada
        
        # Mostrar detalles
        cliente_nombre = renta_encontrada.cliente.nombre if renta_encontrada.cliente else f"ID: {renta_encontrada.customer_id}"
        dvd_titulo = renta_encontrada.dvd.titulo if renta_encontrada.dvd else f"ID: {renta_encontrada.dvd_id}"
        staff_nombre = renta_encontrada.staff.nombre if renta_encontrada.staff else f"ID: {renta_encontrada.staff_id}"
        
        detalles_html = f"""
        <h3>Renta #{renta_encontrada.id}</h3>
        <p><b>Cliente:</b> {cliente_nombre}</p>
        <p><b>DVD:</b> {dvd_titulo}</p>
        <p><b>Atendido por:</b> {staff_nombre}</p>
        <p><b>Fecha de Renta:</b> {renta_encontrada.fecha_renta}</p>
        <p><b>Fecha de Devolución Esperada:</b> {renta_encontrada.fecha_devolucion_esperada}</p>
        <p><b>Monto:</b> ${renta_encontrada.monto:.2f}</p>
        <p><b>Estado:</b> {renta_encontrada.estado.upper()}</p>
        """
        
        self.text_detalles.setHtml(detalles_html)
        self.btn_cancelar.setEnabled(True)
    
    def cancelar_renta(self):
        """
        Cancela la renta actual
        """
        if not self.renta_actual:
            QMessageBox.warning(self, "Error", "No hay una renta seleccionada")
            return
        
        # Obtener motivo (opcional)
        motivo = self.text_motivo.toPlainText().strip()
        
        # Confirmación doble
        respuesta = QMessageBox.warning(
            self,
            "⚠️ CONFIRMAR CANCELACIÓN",
            f"¿Estás SEGURO de que quieres cancelar la Renta #{self.renta_actual.id}?\n\n"
            f"Esta acción NO se puede deshacer.\n\n"
            f"Cliente: {self.renta_actual.cliente.nombre if self.renta_actual.cliente else 'N/A'}\n"
            f"DVD: {self.renta_actual.dvd.titulo if self.renta_actual.dvd else 'N/A'}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # Segunda confirmación
            respuesta2 = QMessageBox.question(
                self,
                "Última Confirmación",
                "¿Confirmas la cancelación? Esta es tu última oportunidad para cancelar.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if respuesta2 == QMessageBox.StandardButton.Yes:
                # Procesar cancelación
                exito, mensaje = self.controller.cancelar_renta(self.renta_actual.id)
                
                if exito:
                    info_msg = f"{mensaje}"
                    if motivo:
                        info_msg += f"\n\nMotivo registrado: {motivo}"
                    
                    QMessageBox.information(self, "Éxito", info_msg)
                    self.limpiar()
                else:
                    QMessageBox.critical(self, "Error", mensaje)
    
    def limpiar(self):
        """
        Limpia el formulario
        """
        self.input_renta_id.clear()
        self.text_detalles.setText("Busca una renta para ver sus detalles...")
        self.text_motivo.clear()
        self.renta_actual = None
        self.btn_cancelar.setEnabled(False)
    
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