from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ReportesView(QWidget):
    def __init__(self, reporte_controller, parent=None):
        super().__init__(parent)
        self.reporte_controller = reporte_controller
        self.ultimo_reporte = None
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        formulario = QFormLayout()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(
            [
                "Pacientes registrados",
                "Citas por rango",
                "Reporte clinico por paciente",
                "Reporte financiero por rango",
            ]
        )
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setDisplayFormat("yyyy-MM-dd")
        self.fecha_fin.setCalendarPopup(True)
        self.input_documento = QLineEdit()

        formulario.addRow("Tipo de reporte:", self.combo_tipo)
        formulario.addRow("Fecha inicio:", self.fecha_inicio)
        formulario.addRow("Fecha fin:", self.fecha_fin)
        formulario.addRow("Documento paciente:", self.input_documento)
        layout.addLayout(formulario)

        botones = QHBoxLayout()
        boton_generar = QPushButton("Generar reporte")
        boton_generar.clicked.connect(self.generar_reporte)
        boton_exportar = QPushButton("Exportar CSV")
        boton_exportar.clicked.connect(self.exportar_csv)
        botones.addWidget(boton_generar)
        botones.addWidget(boton_exportar)
        layout.addLayout(botones)

        self.area_resumen = QTextEdit()
        self.area_resumen.setReadOnly(True)
        layout.addWidget(self.area_resumen)

        self.tabla = QTableWidget(0, 0)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

    def _generar_reporte_actual(self):
        tipo = self.combo_tipo.currentText()
        fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        documento = self.input_documento.text().strip()

        if tipo == "Pacientes registrados":
            return self.reporte_controller.reporte_pacientes()
        if tipo == "Citas por rango":
            return self.reporte_controller.reporte_citas_por_rango(fecha_inicio, fecha_fin)
        if tipo == "Reporte clinico por paciente":
            if not documento:
                QMessageBox.warning(self, "Reportes", "Ingresa el documento del paciente.")
                return None
            return self.reporte_controller.reporte_clinico_por_paciente(documento)
        return self.reporte_controller.reporte_financiero_por_rango(fecha_inicio, fecha_fin)

    def generar_reporte(self):
        reporte = self._generar_reporte_actual()
        if reporte is None:
            return

        self.ultimo_reporte = reporte
        self.area_resumen.setPlainText(f"{reporte['titulo']}\n\n{reporte['resumen']}")
        self.tabla.setColumnCount(len(reporte["columnas"]))
        self.tabla.setHorizontalHeaderLabels(reporte["columnas"])
        self.tabla.setRowCount(len(reporte["filas"]))
        for fila, valores in enumerate(reporte["filas"]):
            for columna, valor in enumerate(valores):
                self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

    def exportar_csv(self):
        if self.ultimo_reporte is None:
            self.generar_reporte()
        if self.ultimo_reporte is None:
            return

        ruta = self.reporte_controller.exportar_reporte_csv(self.ultimo_reporte)
        QMessageBox.information(self, "Reportes", f"Reporte exportado en:\n{ruta}")

    def refrescar_datos(self):
        return
