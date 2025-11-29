"""
Vista para crear una nueva renta
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from controllers.renta_controller import RentaController

class RentaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = RentaController()
        self.init_ui()
        self.cargar_datos_iniciales()
    
    def init_ui(self):
        """
        Inicializa la interfaz de usuario
        """
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("💿 Nueva Renta de DVD")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Grupo de formulario
        form_group = QGroupBox("Datos de la Renta")
        form_layout = QFormLayout()
        
        # Cliente
        self.combo_cliente = QComboBox()
        self.combo_cliente.setEditable(False)
        form_layout.addRow("Cliente:", self.combo_cliente)
        
        # DVD
        self.combo_dvd = QComboBox()
        self.combo_dvd.setEditable(False)
        self.combo_dvd.currentIndexChanged.connect(self.actualizar_info_dvd)
        form_layout.addRow("DVD:", self.combo_dvd)
        
        # Staff
        self.combo_staff = QComboBox()
        self.combo_staff.setEditable(False)
        form_layout.addRow("Atendido por:", self.combo_staff)
        
        # ✅ ELIMINADO: Selector de fecha de devolución
        # Ahora se muestra solo como información (read-only)
        
        # ✅ NUEVO: Información del DVD seleccionado
        self.lbl_duracion = QLabel("Selecciona un DVD para ver la duración de renta")
        self.lbl_duracion.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        form_layout.addRow("Duración de renta:", self.lbl_duracion)
        
        # Monto (read-only)
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("0.00")
        self.input_monto.setReadOnly(True)
        self.input_monto.setStyleSheet("background-color: #2a2a2a;")
        form_layout.addRow("Monto por día:", self.input_monto)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Información adicional
        info_label = QLabel("ℹ️ La fecha de devolución se calculará automáticamente según la duración de renta de la película.")
        info_label.setStyleSheet("color: #4CAF50; padding: 10px; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_inicio = QPushButton("🏠 Volver al Inicio")
        btn_inicio.clicked.connect(self.volver_inicio)
        botones_layout.addWidget(btn_inicio)
        
        botones_layout.addStretch()
        
        btn_limpiar = QPushButton("🔄 Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        botones_layout.addWidget(btn_limpiar)
        
        btn_registrar = QPushButton("✅ Registrar Renta")
        btn_registrar.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        btn_registrar.clicked.connect(self.registrar_renta)
        botones_layout.addWidget(btn_registrar)
        
        layout.addLayout(botones_layout)
        
        # Espacio adicional
        layout.addStretch()
        
        self.setLayout(layout)
    
    def cargar_datos_iniciales(self):
        """
        Carga los datos de clientes, DVDs y staff desde el backend
        """
        # Cargar clientes
        exito, resultado = self.controller.obtener_clientes()
        if exito:
            self.combo_cliente.clear()
            self.combo_cliente.addItem("-- Seleccionar Cliente --", None)
            for cliente in resultado:
                self.combo_cliente.addItem(str(cliente), cliente.id)
        else:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los clientes:\n{resultado}")
        
        # Cargar DVDs
        exito, resultado = self.controller.obtener_dvds()
        if exito:
            self.combo_dvd.clear()
            self.combo_dvd.addItem("-- Seleccionar DVD --", None)
            for dvd in resultado:
                self.combo_dvd.addItem(str(dvd), dvd)
        else:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los DVDs:\n{resultado}")
        
        # Cargar staff
        exito, resultado = self.controller.obtener_staff()
        if exito:
            self.combo_staff.clear()
            self.combo_staff.addItem("-- Seleccionar Staff --", None)
            for staff in resultado:
                self.combo_staff.addItem(str(staff), staff.id)
        else:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar el staff:\n{resultado}")
    
    def actualizar_info_dvd(self):
        """
        Actualiza la información del DVD seleccionado (monto y duración)
        """
        dvd = self.combo_dvd.currentData()
        if dvd:
            # Actualizar monto
            self.input_monto.setText(f"${dvd.precio_renta:.2f}")
            
            # ✅ NUEVO: Mostrar duración de renta
            duracion = getattr(dvd, 'rental_duration', getattr(dvd, 'duracion_renta', 3))
            self.lbl_duracion.setText(f"{duracion} días")
            self.lbl_duracion.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
        else:
            self.input_monto.clear()
            self.lbl_duracion.setText("Selecciona un DVD para ver la duración de renta")
            self.lbl_duracion.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
    
    def limpiar_formulario(self):
        """
        Limpia todos los campos del formulario
        """
        self.combo_cliente.setCurrentIndex(0)
        self.combo_dvd.setCurrentIndex(0)
        self.combo_staff.setCurrentIndex(0)
        self.input_monto.clear()
        self.lbl_duracion.setText("Selecciona un DVD para ver la duración de renta")
        self.lbl_duracion.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
    
    def registrar_renta(self):
        """
        Registra una nueva renta
        """
        # Obtener valores
        cliente_id = self.combo_cliente.currentData()
        dvd = self.combo_dvd.currentData()
        staff_id = self.combo_staff.currentData()
        
        # Validar que se hayan seleccionado todos los campos
        if not cliente_id:
            QMessageBox.warning(self, "Validación", "Por favor selecciona un cliente")
            return
        
        if not dvd:
            QMessageBox.warning(self, "Validación", "Por favor selecciona un DVD")
            return
        
        if not staff_id:
            QMessageBox.warning(self, "Validación", "Por favor selecciona un staff")
            return
        
        # ✅ Llamar al controlador (sin fecha ni monto, el backend los calcula)
        exito, mensaje, renta = self.controller.crear_renta(
            cliente_id, 
            dvd.id,
            staff_id,
            None,  # fecha_devolucion_esperada (no se usa)
            None   # monto (no se usa)
        )
        
        if exito:
            # ✅ MEJORADO: Mostrar información completa en el mensaje
            info_completa = f"{mensaje}\n"
            
            if renta:
                # Agregar información adicional si está disponible
                if hasattr(renta, 'fecha_devolucion_esperada') and renta.fecha_devolucion_esperada:
                    info_completa += f"\nRecuerda devolverlo antes de: {renta.fecha_devolucion_esperada}"
            
            QMessageBox.information(self, "Éxito", info_completa)
            self.limpiar_formulario()
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