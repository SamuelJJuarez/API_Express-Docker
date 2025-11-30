"""
Vista de reporte: DVDs No Devueltos
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from controllers.reportes_controller import ReportesController

class NoDevueltosReporteView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reportes_controller = ReportesController()
        self.init_ui()
        self.cargar_reporte()
    
    def init_ui(self):
        """
        Inicializa la interfaz de usuario
        """
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("⚠️ Reporte: DVDs No Devueltos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Resumen
        self.label_resumen = QLabel("Cargando...")
        self.label_resumen.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(self.label_resumen)
        
        # Botón actualizar
        btn_actualizar = QPushButton("🔄 Actualizar Reporte")
        btn_actualizar.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        btn_actualizar.clicked.connect(self.cargar_reporte)
        layout.addWidget(btn_actualizar)
        
        # Tabla de rentas no devueltas
        self.tabla_rentas = QTableWidget()
        self.tabla_rentas.setColumnCount(7)
        self.tabla_rentas.setHorizontalHeaderLabels([
            "ID Renta", "Cliente", "DVD", "Staff",
            "Fecha Renta", "Fecha Dev. Esperada", "Días de Retraso"
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
    
    def cargar_reporte(self):
        """
        Carga el reporte de DVDs no devueltos
        """
        exito, resultado = self.reportes_controller.obtener_dvds_no_devueltos()
        
        if not exito:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el reporte:\n{resultado}")
            return
        
        # Actualizar resumen
        total_no_devueltos = len(resultado)
        con_retraso = sum(1 for r in resultado if r.calcular_dias_retraso() > 0)
        
        self.label_resumen.setText(
            f"Total DVDs No Devueltos: {total_no_devueltos} | "
            f"Con Retraso: {con_retraso} | "
            f"A Tiempo: {total_no_devueltos - con_retraso}"
        )
        
        # Llenar tabla
        self.tabla_rentas.setRowCount(0)
        
        for renta in resultado:
            row = self.tabla_rentas.rowCount()
            self.tabla_rentas.insertRow(row)
            
            cliente_nombre = renta.cliente.nombre if renta.cliente else f"ID: {renta.customer_id}"
            dvd_titulo = renta.dvd.titulo if renta.dvd else f"ID: {renta.dvd_id}"
            staff_nombre = renta.staff.nombre if renta.staff else f"ID: {renta.staff_id}"
            dias_retraso = renta.calcular_dias_retraso()
            
            self.tabla_rentas.setItem(row, 0, QTableWidgetItem(str(renta.id)))
            self.tabla_rentas.setItem(row, 1, QTableWidgetItem(cliente_nombre))
            self.tabla_rentas.setItem(row, 2, QTableWidgetItem(dvd_titulo))
            self.tabla_rentas.setItem(row, 3, QTableWidgetItem(staff_nombre))
            self.tabla_rentas.setItem(row, 4, QTableWidgetItem(renta.fecha_renta))
            self.tabla_rentas.setItem(row, 5, QTableWidgetItem(renta.fecha_devolucion_esperada))
            
            # Colorear días de retraso
            item_retraso = QTableWidgetItem(f"{dias_retraso} días" if dias_retraso > 0 else "A tiempo")
            if dias_retraso > 7:
                item_retraso.setBackground(Qt.GlobalColor.red)
                item_retraso.setForeground(Qt.GlobalColor.white)
            elif dias_retraso > 0:
                item_retraso.setBackground(Qt.GlobalColor.yellow)
            else:
                item_retraso.setBackground(Qt.GlobalColor.green)
            
            self.tabla_rentas.setItem(row, 6, item_retraso)
        
        if not resultado:
            QMessageBox.information(self, "Sin Rentas", "¡Excelente! No hay DVDs pendientes de devolución")
    
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
                "reporte_no_devueltos.csv",
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