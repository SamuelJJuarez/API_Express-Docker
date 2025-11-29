"""
Vista de reporte: Ganancias por Staff
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from controllers.reportes_controller import ReportesController

class GananciasReporteView(QWidget):
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
        titulo = QLabel("💰 Reporte: Ganancias por Staff")
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
        
        # Tabla de ganancias
        self.tabla_ganancias = QTableWidget()
        self.tabla_ganancias.setColumnCount(3)
        self.tabla_ganancias.setHorizontalHeaderLabels([
            "Nombre del Staff", "Total de Rentas Gestionadas", "Ganancia Total"
        ])
        self.tabla_ganancias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ganancias.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ganancias.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_ganancias)
        
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
            Carga el reporte de ganancias por staff
            """
            exito, resultado = self.reportes_controller.obtener_ganancias_staff()
            
            if not exito:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el reporte:\n{resultado}")
                return
            
            # Actualizar resumen
            total_staff = len(resultado)
            if total_staff > 0:
                # ✅ CORRECCIÓN: Convertir a int/float para evitar error de tipos
                try:
                    total_rentas = sum(int(item.get('total_rentas', 0)) for item in resultado)
                except (ValueError, TypeError):
                    total_rentas = 0
                
                try:
                    total_ganancias = sum(float(item.get('ganancia_total', 0.0)) for item in resultado)
                except (ValueError, TypeError):
                    total_ganancias = 0.0
                
                self.label_resumen.setText(
                    f"Total de Empleados: {total_staff} | "
                    f"Total Rentas Gestionadas: {total_rentas} | "
                    f"Ganancias Totales: ${total_ganancias:.2f}"
                )
            else:
                self.label_resumen.setText("No hay datos disponibles")
            
            # Llenar tabla
            self.tabla_ganancias.setRowCount(0)
            
            datos_tabla = self.reportes_controller.formatear_datos_tabla_ganancias(resultado)
            
            for datos_fila in datos_tabla:
                row = self.tabla_ganancias.rowCount()
                self.tabla_ganancias.insertRow(row)
                
                # Nombre del staff
                self.tabla_ganancias.setItem(row, 0, QTableWidgetItem(str(datos_fila[0])))
                
                # Total de rentas
                item_rentas = QTableWidgetItem(str(datos_fila[1]))
                item_rentas.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_ganancias.setItem(row, 1, item_rentas)
                
                # Ganancia total
                ganancia_texto = str(datos_fila[2])
                item_ganancia = QTableWidgetItem(ganancia_texto)
                item_ganancia.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                
                # Colorear según ganancia
                try:
                    # Remover el símbolo $ y convertir a float
                    ganancia_limpia = ganancia_texto.replace('$', '').strip()
                    ganancia_valor = float(ganancia_limpia)
                    
                    if ganancia_valor >= 1000:
                        item_ganancia.setBackground(Qt.GlobalColor.green)
                        item_ganancia.setForeground(Qt.GlobalColor.white)
                    elif ganancia_valor >= 500:
                        item_ganancia.setBackground(Qt.GlobalColor.yellow)
                except (ValueError, TypeError):
                    # Si hay error en la conversión, simplemente no colorear
                    pass
                
                self.tabla_ganancias.setItem(row, 2, item_ganancia)
            
            if not resultado:
                QMessageBox.information(self, "Sin Datos", "No hay información de ganancias disponible")
    
    def exportar_csv(self):
        """
        Exporta los datos de la tabla a CSV
        """
        if self.tabla_ganancias.rowCount() == 0:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para exportar")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            import csv
            
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte",
                "reporte_ganancias_staff.csv",
                "CSV Files (*.csv)"
            )
            
            if archivo:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Escribir encabezados
                    headers = []
                    for col in range(self.tabla_ganancias.columnCount()):
                        headers.append(self.tabla_ganancias.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for row in range(self.tabla_ganancias.rowCount()):
                        row_data = []
                        for col in range(self.tabla_ganancias.columnCount()):
                            item = self.tabla_ganancias.item(row, col)
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