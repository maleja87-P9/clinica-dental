from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

from modelos.paciente import Paciente


class PacientesView(QWidget):
    def __init__(self, paciente_controller, on_change=None, parent=None):
        super().__init__(parent)
        self.paciente_controller = paciente_controller
        self.on_change = on_change
        self.documento_original = None  # Guarda el documento original al cargar un paciente
        self._construir_ui()
        self.refrescar_datos()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        grupo_formulario = QGroupBox("Gestión de pacientes")
        form_layout = QFormLayout(grupo_formulario)

        self.input_documento = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_correo = QLineEdit()
        self.input_direccion = QLineEdit()

        form_layout.addRow("Documento:", self.input_documento)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Teléfono:", self.input_telefono)
        form_layout.addRow("Correo:", self.input_correo)
        form_layout.addRow("Dirección:", self.input_direccion)

        # Botones principales
        botones = QHBoxLayout()
        boton_registrar = QPushButton("Registrar")
        boton_buscar = QPushButton("Buscar por documento")
        boton_actualizar = QPushButton("Actualizar")
        boton_limpiar = QPushButton("Limpiar")

        boton_registrar.clicked.connect(self.registrar_paciente)
        boton_buscar.clicked.connect(self.buscar_paciente)
        boton_actualizar.clicked.connect(self.actualizar_paciente)
        boton_limpiar.clicked.connect(self.limpiar_campos)

        botones.addWidget(boton_registrar)
        botones.addWidget(boton_buscar)
        botones.addWidget(boton_actualizar)
        botones.addWidget(boton_limpiar)

        # Botones de eliminación
        botones_eliminar = QHBoxLayout()
        self.boton_eliminar = QPushButton("🗑️ Eliminar paciente seleccionado")
        self.boton_eliminar.setStyleSheet("background-color: #dc3545; color: white;")
        self.boton_eliminar.clicked.connect(self.eliminar_paciente_seleccionado)

        self.boton_eliminar_todos = QPushButton("⚠️ Eliminar TODOS los pacientes")
        self.boton_eliminar_todos.setStyleSheet("background-color: #c82333; color: white; font-weight: bold;")
        self.boton_eliminar_todos.clicked.connect(self.eliminar_todos_los_pacientes)

        botones_eliminar.addWidget(self.boton_eliminar)
        botones_eliminar.addWidget(self.boton_eliminar_todos)

        layout.addWidget(grupo_formulario)
        layout.addLayout(botones)
        layout.addLayout(botones_eliminar)

        self.etiqueta_resultado = QLabel("")
        layout.addWidget(self.etiqueta_resultado)

        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels(
            ["Documento", "Nombre", "Teléfono", "Correo", "Dirección", "Historiales"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.itemSelectionChanged.connect(self.cargar_desde_tabla)
        layout.addWidget(self.tabla)

    def _paciente_desde_formulario(self):
        return Paciente(
            documento=self.input_documento.text(),
            nombre=self.input_nombre.text(),
            telefono=self.input_telefono.text(),
            correo=self.input_correo.text(),
            direccion=self.input_direccion.text(),
        )

    def registrar_paciente(self):
        # Validar que el documento no esté vacío
        if not self.input_documento.text().strip():
            QMessageBox.warning(self, "Registrar", "El documento es obligatorio.")
            return
        exito, mensaje = self.paciente_controller.registrar_paciente(self._paciente_desde_formulario())
        if exito:
            QMessageBox.information(self, "Paciente", mensaje)
            self.limpiar_campos()
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Paciente", mensaje)

    def buscar_paciente(self):
        documento = self.input_documento.text().strip()
        if not documento:
            QMessageBox.warning(self, "Búsqueda", "Ingrese un documento para buscar.")
            return
        paciente = self.paciente_controller.buscar_por_documento(documento)
        if not paciente:
            QMessageBox.warning(self, "Búsqueda", "No se encontró un paciente con ese documento.")
            return
        self._cargar_paciente_en_formulario(paciente)
        self.documento_original = paciente.get("documento")  # Guardar documento original
        self.etiqueta_resultado.setText(f"Paciente encontrado: {paciente.get('nombre')}")

    def actualizar_paciente(self):
        if not self.documento_original:
            QMessageBox.warning(self, "Actualizar", "Primero busque o seleccione un paciente de la tabla.")
            return

        # Obtener los datos actuales del formulario
        datos_actualizados = {
            "documento": self.input_documento.text().strip(),
            "nombre": self.input_nombre.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "correo": self.input_correo.text().strip(),
            "direccion": self.input_direccion.text().strip(),
        }

        # Validar campos obligatorios
        if not datos_actualizados["documento"] or not datos_actualizados["nombre"] or not datos_actualizados["telefono"]:
            QMessageBox.warning(self, "Actualizar", "Documento, nombre y teléfono son obligatorios.")
            return

        exito, mensaje = self.paciente_controller.actualizar_paciente(
            self.documento_original,  # pasamos el documento original (el que tenía antes)
            datos_actualizados
        )
        if exito:
            QMessageBox.information(self, "Paciente", mensaje)
            self.limpiar_campos()
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def _cargar_paciente_en_formulario(self, paciente):
        self.input_documento.setText(paciente.get("documento", ""))
        self.input_nombre.setText(paciente.get("nombre", ""))
        self.input_telefono.setText(paciente.get("telefono", ""))
        self.input_correo.setText(paciente.get("correo", ""))
        self.input_direccion.setText(paciente.get("direccion", ""))
        # Guardar el documento original para la actualización
        self.documento_original = paciente.get("documento")

    def cargar_desde_tabla(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return
        paciente = {
            "documento": self.tabla.item(fila, 0).text(),
            "nombre": self.tabla.item(fila, 1).text(),
            "telefono": self.tabla.item(fila, 2).text(),
            "correo": self.tabla.item(fila, 3).text(),
            "direccion": self.tabla.item(fila, 4).text(),
        }
        self._cargar_paciente_en_formulario(paciente)
        self.etiqueta_resultado.setText(f"Paciente cargado: {paciente.get('nombre')}")

    def limpiar_campos(self):
        self.input_documento.clear()
        self.input_nombre.clear()
        self.input_telefono.clear()
        self.input_correo.clear()
        self.input_direccion.clear()
        self.etiqueta_resultado.clear()
        self.documento_original = None

    def refrescar_datos(self):
        pacientes = self.paciente_controller.listar_pacientes()
        self.tabla.setRowCount(len(pacientes))
        for fila, paciente in enumerate(pacientes):
            self.tabla.setItem(fila, 0, QTableWidgetItem(paciente.get("documento", "")))
            self.tabla.setItem(fila, 1, QTableWidgetItem(paciente.get("nombre", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem(paciente.get("telefono", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(paciente.get("correo", "")))
            self.tabla.setItem(fila, 4, QTableWidgetItem(paciente.get("direccion", "")))
            self.tabla.setItem(
                fila,
                5,
                QTableWidgetItem(str(len(paciente.get("historial", [])))),
            )

    # ================== ELIMINACIÓN ==================
    def eliminar_paciente_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Eliminar paciente", "❌ Selecciona un paciente de la tabla.")
            return

        documento = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar permanentemente a:\n\n📄 Documento: {documento}\n👤 Nombre: {nombre}\n\n⚠️ Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        exito, mensaje = self.paciente_controller.eliminar_paciente_por_documento(documento)
        if exito:
            QMessageBox.information(self, "Paciente eliminado", f"✅ {mensaje}")
            self.refrescar_datos()
            self.limpiar_campos()
            if self.on_change:
                self.on_change()
        else:
            QMessageBox.warning(self, "Error", f"❌ {mensaje}")

    def eliminar_todos_los_pacientes(self):
        pacientes = self.paciente_controller.listar_pacientes()
        if not pacientes:
            QMessageBox.warning(self, "Eliminar todos", "❌ No hay pacientes para eliminar.")
            return

        resp = QMessageBox.question(
            self,
            "⚠️ ADVERTENCIA EXTREMA ⚠️",
            f"Estás a punto de eliminar TODOS los {len(pacientes)} pacientes.\n\nSe creará un backup automático.\n¿Estás ABSOLUTAMENTE seguro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        codigo, ok = QInputDialog.getText(self, "Confirmación final", "Escribe 'ELIMINAR' para confirmar:")
        if not ok or codigo != "ELIMINAR":
            QMessageBox.warning(self, "Cancelado", "Operación cancelada.")
            return

        exito, mensaje = self.paciente_controller.eliminar_todos_los_pacientes()
        if exito:
            QMessageBox.information(self, "Pacientes eliminados", f"✅ {mensaje}")
            self.refrescar_datos()
            self.limpiar_campos()
            if self.on_change:
                self.on_change()
        else:
            QMessageBox.warning(self, "Error", f"❌ {mensaje}")
