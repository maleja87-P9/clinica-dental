import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from vistas.pacientes_view import PacientesView


def test_pacientes_view_alta_busqueda_modificacion(qtbot, paciente_controller):
    """
    Prueba el flujo completo de ABM (alta, búsqueda, modificación) en PacientesView.
    """
    view = PacientesView(paciente_controller)
    qtbot.addWidget(view)

    # --- 1. Alta de paciente ---
    # Llenar campos
    qtbot.keyClicks(view.input_documento, "999999")
    qtbot.keyClicks(view.input_nombre, "Lucia Perez")
    qtbot.keyClicks(view.input_telefono, "3001234567")
    qtbot.keyClicks(view.input_correo, "lucia@example.com")
    qtbot.keyClicks(view.input_direccion, "Calle Falsa 123")

    # Hacer clic en botón Registrar (usando objectName)
    boton_registrar = view.findChild(QPushButton, "boton_registrar")
    assert boton_registrar is not None, "No se encontró el botón 'boton_registrar'"
    qtbot.mouseClick(boton_registrar, Qt.LeftButton)

    # Esperar a que se procesen los eventos y se guarde en JSON
    qtbot.wait(500)

    # Verificar que el paciente aparezca en la tabla
    items = view.tabla.findItems("999999", Qt.MatchExactly)
    assert len(items) > 0, "El paciente no apareció en la tabla después del alta"

    # Verificar directamente en el controlador
    paciente_db = paciente_controller.buscar_por_documento("999999")
    assert paciente_db is not None
    assert paciente_db["nombre"] == "Lucia Perez"

    # --- 2. Búsqueda por documento ---
    # Limpiar y escribir el documento
    view.input_documento.clear()
    qtbot.keyClicks(view.input_documento, "999999")
    boton_buscar = view.findChild(QPushButton, "boton_buscar")
    assert boton_buscar is not None
    qtbot.mouseClick(boton_buscar, Qt.LeftButton)
    qtbot.wait(300)

    # Verificar que los campos se llenaron con los datos del paciente
    assert view.input_nombre.text() == "Lucia Perez"
    assert view.input_telefono.text() == "3001234567"
    assert view.input_correo.text() == "lucia@example.com"
    assert view.input_direccion.text() == "Calle Falsa 123"

    # --- 3. Modificación del paciente ---
    # Cambiar nombre y teléfono
    view.input_nombre.clear()
    qtbot.keyClicks(view.input_nombre, "Lucia Perez Modificada")
    view.input_telefono.clear()
    qtbot.keyClicks(view.input_telefono, "3112223344")

    boton_actualizar = view.findChild(QPushButton, "boton_actualizar")
    assert boton_actualizar is not None
    qtbot.mouseClick(boton_actualizar, Qt.LeftButton)
    qtbot.wait(500)

    # Verificar cambio en el controlador
    paciente_actualizado = paciente_controller.buscar_por_documento("999999")
    assert paciente_actualizado["nombre"] == "Lucia Perez Modificada"
    assert paciente_actualizado["telefono"] == "3112223344"

    # Refrescar la tabla (opcional: volver a buscar)
    qtbot.mouseClick(boton_buscar, Qt.LeftButton)
    qtbot.wait(300)
    assert view.input_nombre.text() == "Lucia Perez Modificada"
