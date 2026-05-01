from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from modelos.factura import Factura
from modelos.pago import Pago


class FacturacionView(QWidget):
    def __init__(
        self,
        factura_controller,
        pago_controller,
        paciente_controller,
        on_change=None,
        parent=None,
    ):
        super().__init__(parent)
        self.factura_controller = factura_controller
        self.pago_controller = pago_controller
        self.paciente_controller = paciente_controller
        self.on_change = on_change
        self._construir_ui()
        self.refrescar_datos()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        grupo_factura = QGroupBox("📄 Facturación")
        grupo_factura.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #a9cce3;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        factura_layout = QFormLayout(grupo_factura)

        self.input_documento = QLineEdit()
        self.input_concepto = QLineEdit()
        self.input_valor_total = QLineEdit()

        factura_layout.addRow("📋 Documento paciente:", self.input_documento)
        factura_layout.addRow("📝 Concepto:", self.input_concepto)
        factura_layout.addRow("💰 Valor total:", self.input_valor_total)
        layout.addWidget(grupo_factura)

        botones_factura = QHBoxLayout()
        boton_generar = QPushButton("Generar factura")
        boton_generar.setStyleSheet("background-color: #27ae60;")
        boton_buscar = QPushButton("Buscar historial financiero")
        boton_limpiar = QPushButton("Limpiar")

        boton_generar.clicked.connect(self.generar_factura)
        boton_buscar.clicked.connect(self.buscar_historial)
        boton_limpiar.clicked.connect(self.limpiar_factura)

        botones_factura.addWidget(boton_generar)
        botones_factura.addWidget(boton_buscar)
        botones_factura.addWidget(boton_limpiar)
        layout.addLayout(botones_factura)

        self.tabla_facturas = QTableWidget(0, 8)
        self.tabla_facturas.setHorizontalHeaderLabels(
            ["Factura", "Documento", "Paciente", "Fecha", "Concepto", "Total", "Saldo", "Estado"]
        )
        self.tabla_facturas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_facturas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_facturas.itemSelectionChanged.connect(self.cargar_factura_seleccionada)
        self.tabla_facturas.setStyleSheet("alternate-background-color: #f0f8ff;")
        layout.addWidget(self.tabla_facturas)

        grupo_pago = QGroupBox("💰 Registro de pagos")
        grupo_pago.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #a9cce3;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
            }
        """)
        pago_layout = QFormLayout(grupo_pago)

        self.input_id_factura = QLineEdit()
        self.input_id_factura.setReadOnly(True)
        self.input_valor_pago = QLineEdit()
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Efectivo", "Tarjeta", "Transferencia"])

        pago_layout.addRow("🏷️ Factura seleccionada:", self.input_id_factura)
        pago_layout.addRow("💵 Valor pagado:", self.input_valor_pago)
        pago_layout.addRow("💳 Método:", self.combo_metodo)
        layout.addWidget(grupo_pago)

        boton_pago = QPushButton("Registrar pago")
        boton_pago.setStyleSheet("background-color: #2980b9;")
        boton_pago.clicked.connect(self.registrar_pago)
        layout.addWidget(boton_pago)

        self.tabla_pagos = QTableWidget(0, 6)
        self.tabla_pagos.setHorizontalHeaderLabels(
            ["Pago", "Factura", "Documento", "Fecha", "Valor", "Método"]
        )
        self.tabla_pagos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_pagos)

    def _validar_campos_obligatorios(self, campos):
        for nombre, valor in campos.items():
            if not valor or not str(valor).strip():
                QMessageBox.warning(self, "Campos incompletos", f"❌ El campo '{nombre}' es obligatorio.")
                return False
        return True

    def generar_factura(self):
        documento = self.input_documento.text().strip()
        concepto = self.input_concepto.text().strip()
        valor_total = self.input_valor_total.text().strip()

        if not self._validar_campos_obligatorios({
            "documento del paciente": documento,
            "concepto": concepto,
            "valor total": valor_total
        }):
            return

        paciente = self.paciente_controller.buscar_por_documento(documento)
        if not paciente:
            QMessageBox.warning(self, "Facturación", "❌ El paciente no existe.")
            return

        try:
            valor_float = float(valor_total)
            if valor_float <= 0:
                QMessageBox.warning(self, "Facturación", "❌ El valor total debe ser mayor a cero.")
                return
        except ValueError:
            QMessageBox.warning(self, "Facturación", "❌ El valor total debe ser un número válido.")
            return

        factura = Factura(
            documento_paciente=documento,
            nombre_paciente=paciente.get("nombre", ""),
            concepto=concepto,
            valor_total=valor_total,
        )
        exito, mensaje = self.factura_controller.generar_factura(factura)
        if exito:
            QMessageBox.information(self, "Facturación", f"✅ {mensaje}")
            self.limpiar_factura()
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Facturación", f"❌ {mensaje}")

    def registrar_pago(self):
        id_factura = self.input_id_factura.text().strip()
        valor_pago = self.input_valor_pago.text().strip()

        if not id_factura:
            QMessageBox.warning(self, "Pagos", "❌ Selecciona una factura de la tabla.")
            return

        if not self._validar_campos_obligatorios({"valor pagado": valor_pago}):
            return

        try:
            valor_float = float(valor_pago)
            if valor_float <= 0:
                QMessageBox.warning(self, "Pagos", "❌ El valor pagado debe ser mayor a cero.")
                return
        except ValueError:
            QMessageBox.warning(self, "Pagos", "❌ El valor pagado debe ser un número válido.")
            return

        factura = self.factura_controller.obtener_factura(id_factura)
        pago = Pago(
            id_factura=id_factura,
            documento_paciente=factura.get("documento_paciente", "") if factura else "",
            valor_pagado=valor_pago,
            metodo_pago=self.combo_metodo.currentText(),
        )
        exito, mensaje = self.pago_controller.registrar_pago(pago)
        if exito:
            QMessageBox.information(self, "Pagos", f"✅ {mensaje}")
            self.input_valor_pago.clear()
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Pagos", f"❌ {mensaje}")

    def cargar_factura_seleccionada(self):
        fila = self.tabla_facturas.currentRow()
        if fila < 0:
            return
        self.input_id_factura.setText(self.tabla_facturas.item(fila, 0).text())

    def buscar_historial(self):
        documento = self.input_documento.text().strip()
        if not documento:
            QMessageBox.warning(self, "Facturación", "❌ Ingresa el documento del paciente.")
            return
        self.refrescar_datos(documento)

    def limpiar_factura(self):
        self.input_documento.clear()
        self.input_concepto.clear()
        self.input_valor_total.clear()
        self.input_id_factura.clear()
        self.input_valor_pago.clear()

    def refrescar_datos(self, documento=None):
        if documento:
            facturas = self.factura_controller.buscar_por_paciente(documento)
            pagos = self.pago_controller.historial_financiero_por_paciente(documento).get("pagos", [])
        else:
            facturas = self.factura_controller.listar_facturas()
            pagos = self.pago_controller.listar_pagos()

        self.tabla_facturas.setRowCount(len(facturas))
        for fila, factura in enumerate(facturas):
            saldo = self.pago_controller.calcular_saldo_pendiente(factura.get("id_factura")) or 0
            self.tabla_facturas.setItem(fila, 0, QTableWidgetItem(factura.get("id_factura", "")))
            self.tabla_facturas.setItem(fila, 1, QTableWidgetItem(factura.get("documento_paciente", "")))
            self.tabla_facturas.setItem(fila, 2, QTableWidgetItem(factura.get("nombre_paciente", "")))
            self.tabla_facturas.setItem(fila, 3, QTableWidgetItem(factura.get("fecha", "")))
            self.tabla_facturas.setItem(fila, 4, QTableWidgetItem(factura.get("concepto", "")))
            self.tabla_facturas.setItem(fila, 5, QTableWidgetItem(str(factura.get("valor_total", 0))))
            self.tabla_facturas.setItem(fila, 6, QTableWidgetItem(f"{saldo:.2f}"))
            self.tabla_facturas.setItem(fila, 7, QTableWidgetItem(factura.get("estado_pago", "")))

        self.tabla_pagos.setRowCount(len(pagos))
        for fila, pago in enumerate(pagos):
            self.tabla_pagos.setItem(fila, 0, QTableWidgetItem(pago.get("id_pago", "")))
            self.tabla_pagos.setItem(fila, 1, QTableWidgetItem(pago.get("id_factura", "")))
            self.tabla_pagos.setItem(fila, 2, QTableWidgetItem(pago.get("documento_paciente", "")))
            self.tabla_pagos.setItem(fila, 3, QTableWidgetItem(pago.get("fecha", "")))
            self.tabla_pagos.setItem(fila, 4, QTableWidgetItem(str(pago.get("valor_pagado", 0))))
            self.tabla_pagos.setItem(fila, 5, QTableWidgetItem(pago.get("metodo_pago", "")))
