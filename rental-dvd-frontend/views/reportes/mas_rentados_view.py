"""
Vista de reporte: DVDs Más Rentados
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from controllers.reportes_controller import ReportesController

class MasRentadosReporteView(QWidget):
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
        titulo = QLabel("🏆 Reporte: DVDs Más Rentados")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Resumen
        self.label_resumen = QLabel("Cargando...")
        self.label_resumen.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(self.label_resumen)
        
        # Botón actualizar
        btn_actualizar = QPushButton("🔄 Actualizar Ranking")
        btn_actualizar.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        btn_actualizar.clicked.connect(self.cargar_reporte)
        layout.addWidget(btn_actualizar)
        
        # Tabla de ranking
        self.tabla_ranking = QTableWidget()
        self.tabla_ranking.setColumnCount(4)
        self.tabla_ranking.setHorizontalHeaderLabels([
            "Posición", "Título del DVD", "Género", "Total de Rentas"
        ])
        self.tabla_ranking.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ranking.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ranking.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_ranking)
        
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
            Carga el reporte de DVDs más rentados
            """
            exito, resultado = self.reportes_controller.obtener_dvds_mas_rentados()
            
            if not exito:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el reporte:\n{resultado}")
                return
            
            # Actualizar resumen
            total_dvds = len(resultado)
            if total_dvds > 0:
                # ✅ CORRECCIÓN: Convertir a int para evitar error de tipos
                try:
                    total_rentas = sum(int(item.get('total_rentas', 0)) for item in resultado)
                except (ValueError, TypeError):
                    total_rentas = 0
                
                self.label_resumen.setText(
                    f"Total de DVDs: {total_dvds} | "
                    f"Total de Rentas: {total_rentas}"
                )
            else:
                self.label_resumen.setText("No hay datos disponibles")
            
            # Llenar tabla
            self.tabla_ranking.setRowCount(0)
            
            datos_tabla = self.reportes_controller.formatear_datos_tabla_ranking(resultado)
            
            for posicion, datos_fila in enumerate(datos_tabla, start=1):
                row = self.tabla_ranking.rowCount()
                self.tabla_ranking.insertRow(row)
                
                # Posición
                item_pos = QTableWidgetItem(str(posicion))
                item_pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Colorear top 3
                if posicion == 1:
                    item_pos.setBackground(Qt.GlobalColor.yellow)
                    item_pos.setText(f"🥇 {posicion}")
                elif posicion == 2:
                    item_pos.setBackground(Qt.GlobalColor.lightGray)
                    item_pos.setText(f"🥈 {posicion}")
                elif posicion == 3:
                    item_pos.setBackground(Qt.GlobalColor.darkYellow)
                    item_pos.setText(f"🥉 {posicion}")
                
                self.tabla_ranking.setItem(row, 0, item_pos)
                
                # Datos del DVD
                self.tabla_ranking.setItem(row, 1, QTableWidgetItem(str(datos_fila[0])))  # Título
                self.tabla_ranking.setItem(row, 2, QTableWidgetItem(str(datos_fila[1])))  # Género
                
                # Total rentas
                item_total = QTableWidgetItem(str(datos_fila[2]))
                item_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_ranking.setItem(row, 3, item_total)
            
            if not resultado:
                QMessageBox.information(self, "Sin Datos", "No hay información de rentas disponible")
    
    def exportar_csv(self):
        """
        Exporta los datos de la tabla a CSV
        """
        if self.tabla_ranking.rowCount() == 0:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para exportar")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            import csv
            
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Ranking",
                "ranking_dvds_mas_rentados.csv",
                "CSV Files (*.csv)"
            )
            
            if archivo:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Escribir encabezados
                    headers = []
                    for col in range(self.tabla_ranking.columnCount()):
                        headers.append(self.tabla_ranking.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for row in range(self.tabla_ranking.rowCount()):
                        row_data = []
                        for col in range(self.tabla_ranking.columnCount()):
                            item = self.tabla_ranking.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Éxito", f"Ranking exportado a:\n{archivo}")
        
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