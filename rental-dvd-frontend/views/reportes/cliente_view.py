"""
Vista de reporte: Rentas por Cliente
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox
)
from PyQt6.QtCore import Qt
from controllers.reportes_controller import ReportesController
from controllers.renta_controller import RentaController

class ClienteReporteView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reportes_controller = ReportesController()
        self.renta_controller = RentaController()
        self.init_ui()
        self.cargar_clientes()
    
    def init_ui(self):
        """
        Inicializa la interfaz de usuario
        """
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("📋 Reporte: Rentas por Cliente")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Grupo de búsqueda
        busqueda_group = QGroupBox("Seleccionar Cliente")
        busqueda_layout = QHBoxLayout()
        
        # Opción 1: Combo de clientes
        self.combo_cliente = QComboBox()
        busqueda_layout.addWidget(QLabel("Cliente:"))
        busqueda_layout.addWidget(self.combo_cliente)
        
        # Opción 2: Input manual de ID
        self.input_cliente_id = QLineEdit()
        self.input_cliente_id.setPlaceholderText("O ingresa ID manualmente")
        self.input_cliente_id.setMaximumWidth(200)
        busqueda_layout.addWidget(QLabel("ID:"))
        busqueda_layout.addWidget(self.input_cliente_id)
        
        btn_consultar = QPushButton("🔍 Consultar")
        btn_consultar.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        btn_consultar.clicked.connect(self.consultar_rentas)
        busqueda_layout.addWidget(btn_consultar)
        
        busqueda_group.setLayout(busqueda_layout)
        layout.addWidget(busqueda_group)
        
        # Resumen
        self.label_resumen = QLabel("Selecciona un cliente para ver sus rentas")
        self.label_resumen.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(self.label_resumen)
        
        # Tabla de rentas
        self.tabla_rentas = QTableWidget()
        self.tabla_rentas.setColumnCount(9)
        self.tabla_rentas.setHorizontalHeaderLabels([
            "ID", "DVD", "Staff", "Fecha Renta", 
            "Fecha Dev. Esperada", "Fecha Dev. Real", 
            "Monto", "Estado", "Retraso"
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
        
        btn_exportar = QPushButton("📄 Exportar a CSV")
        btn_exportar.clicked.connect(self.exportar_csv)
        botones_layout.addWidget(btn_exportar)
        
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)
    
    def cargar_clientes(self):
        """
        Carga la lista de clientes en el combo
        """
        exito, resultado = self.renta_controller.obtener_clientes()
        
        if exito:
            self.combo_cliente.clear()
            self.combo_cliente.addItem("-- Seleccionar Cliente --", None)
            for cliente in resultado:
                self.combo_cliente.addItem(f"{cliente.nombre} - {cliente.email}", cliente.id)
        else:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los clientes:\n{resultado}")
    
    def consultar_rentas(self):
        """
        Consulta las rentas del cliente seleccionado
        """
        # Obtener ID del cliente (combo o input manual)
        cliente_id = None
        
        # Prioridad al input manual
        if self.input_cliente_id.text().strip():
            try:
                cliente_id = int(self.input_cliente_id.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Validación", "El ID debe ser un número válido")
                return
        else:
            cliente_id = self.combo_cliente.currentData()
        
        if not cliente_id:
            QMessageBox.warning(self, "Validación", "Por favor selecciona o ingresa un cliente")
            return
        
        # Consultar rentas
        exito, resultado = self.reportes_controller.obtener_rentas_cliente(cliente_id)
        
        if not exito:
            QMessageBox.critical(self, "Error", f"No se pudieron obtener las rentas:\n{resultado}")
            return
        
        # ✅ MEJORADO: Manejar conversión de tipos
        total_rentas = len(resultado)
        activas = sum(1 for r in resultado if r.estado == 'activa')
        devueltas = sum(1 for r in resultado if r.estado == 'devuelta')
        canceladas = sum(1 for r in resultado if r.estado == 'cancelada')
        
        # ✅ CORRECCIÓN: Convertir monto a float para evitar errores
        try:
            total_gastado = sum(float(r.monto) if r.monto else 0.0 for r in resultado)
        except (ValueError, TypeError):
            total_gastado = 0.0
        
        self.label_resumen.setText(
            f"Total de Rentas: {total_rentas} | "
            f"Activas: {activas} | Devueltas: {devueltas} | Canceladas: {canceladas} | "
            f"Total Gastado: ${total_gastado:.2f}"
        )
        
        # Llenar tabla
        self.tabla_rentas.setRowCount(0)
        
        # ✅ CORRECCIÓN CRÍTICA: Procesar cada renta individualmente
        for renta in resultado:
            row = self.tabla_rentas.rowCount()
            self.tabla_rentas.insertRow(row)
            
            # Columna 0: ID
            item_id = QTableWidgetItem(str(renta.id))
            
            # Columna 1: DVD
            dvd_titulo = renta.dvd.titulo if renta.dvd else (renta.title or f"ID: {renta.film_id}")
            item_dvd = QTableWidgetItem(dvd_titulo)
            
            # ✅ Columna 2: Staff (CORREGIDO)
            if renta.staff:
                staff_nombre = renta.staff.nombre
            elif renta.staff_name:
                staff_nombre = renta.staff_name
            elif renta.staff_id:
                staff_nombre = f"ID: {renta.staff_id}"
            else:
                staff_nombre = "N/A"
            item_staff = QTableWidgetItem(staff_nombre)
            
            # Columna 3: Fecha Renta
            item_fecha_renta = QTableWidgetItem(str(renta.fecha_renta) if renta.fecha_renta else "N/A")
            
            # Columna 4: Fecha Devolución Esperada
            fecha_esp = renta.fecha_devolucion_esperada if renta.fecha_devolucion_esperada else "N/A"
            item_fecha_esp = QTableWidgetItem(str(fecha_esp))
            
            # Columna 5: Fecha Devolución Real
            fecha_real = renta.fecha_devolucion_real if renta.fecha_devolucion_real else "Pendiente"
            item_fecha_real = QTableWidgetItem(str(fecha_real))
            
            # Columna 6: Monto
            try:
                monto_valor = float(renta.monto) if renta.monto else 0.0
            except (ValueError, TypeError):
                monto_valor = 0.0
            item_monto = QTableWidgetItem(f"${monto_valor:.2f}")
            
            # Columna 7: Estado
            estado_texto = renta.estado.capitalize()
            item_estado = QTableWidgetItem(estado_texto)
            
            # Columna 8: Retraso
            if renta.estado == 'activa':
                dias_retraso = renta.calcular_dias_retraso()
                if dias_retraso > 0:
                    item_retraso = QTableWidgetItem(f"{dias_retraso} días")
                else:
                    item_retraso = QTableWidgetItem("A tiempo")
            else:
                item_retraso = QTableWidgetItem("-")
            
            # Insertar items en la tabla
            self.tabla_rentas.setItem(row, 0, item_id)
            self.tabla_rentas.setItem(row, 1, item_dvd)
            self.tabla_rentas.setItem(row, 2, item_staff)
            self.tabla_rentas.setItem(row, 3, item_fecha_renta)
            self.tabla_rentas.setItem(row, 4, item_fecha_esp)
            self.tabla_rentas.setItem(row, 5, item_fecha_real)
            self.tabla_rentas.setItem(row, 6, item_monto)
            self.tabla_rentas.setItem(row, 7, item_estado)
            self.tabla_rentas.setItem(row, 8, item_retraso)
        
        if not resultado:
            QMessageBox.information(self, "Sin Rentas", "Este cliente no tiene rentas registradas")
    
    def exportar_csv(self):
        """
        Exporta los datos de la tabla a CSV
        """
        if self.tabla_rentas.rowCount() == 0:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para exportar")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            import csv
            
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte",
                "reporte_cliente.csv",
                "CSV Files (*.csv)"
            )
            
            if archivo:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    headers = []
                    for col in range(self.tabla_rentas.columnCount()):
                        headers.append(self.tabla_rentas.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    for row in range(self.tabla_rentas.rowCount()):
                        row_data = []
                        for col in range(self.tabla_rentas.columnCount()):
                            item = self.tabla_rentas.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Éxito", f"Reporte exportado a:\n{archivo}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo:\n{str(e)}")
    
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