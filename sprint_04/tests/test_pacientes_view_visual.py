from pathlib import Path

import pytest
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox
from vistas.pacientes_view import PacientesView

def handle_message_box():
    """Busca un QMessageBox abierto y lo acepta (hace clic en OK)."""
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMessageBox):
            # Hacemos clic en el botón "OK" (por defecto es el primero)
            ok_button = widget.button(QMessageBox.Ok)
            if ok_button:
                QTest.mouseClick(ok_button, Qt.LeftButton)
            else:
                widget.accept()
            return True
    return False

def test_registro_paciente_visual(qapp):
    from controladores.paciente_controller import PacienteController
    from utils.json_manager import JsonManager

    # Usar un directorio temporal para no ensuciar datos reales
    import tempfile, shutil
    temp_dir = tempfile.mkdtemp()
    paciente_controller = PacienteController(Path(temp_dir) / "pacientes.json")

    view = PacientesView(paciente_controller)
    view.show()  # Mostrar la ventana (visible)
    QTest.qWait(500)  # Esperar a que se dibuje

    # Llenar el formulario
    view.input_documento.setText("999999")
    QTest.qWait(300)
    view.input_nombre.setText("Ana Pérez")
    QTest.qWait(300)
    view.input_telefono.setText("3112223333")
    QTest.qWait(300)
    view.input_correo.setText("ana@test.com")
    QTest.qWait(300)
    view.input_direccion.setText("Calle 123")
    QTest.qWait(300)

    # Programar el cierre automático del QMessageBox (si aparece)
    # Usamos un QTimer para que después de 1 segundo busque el diálogo y lo acepte
    QTimer.singleShot(1000, handle_message_box)

    # Hacer clic en "Registrar"
    QTest.mouseClick(view.boton_registrar, Qt.LeftButton)
    QTest.qWait(2000)  # Esperar a que el mensaje aparezca y se cierre solo

    # Verificar que el paciente se haya agregado a la tabla
    view.refrescar_datos()
    tabla = view.tabla
    encontrado = False
    for row in range(tabla.rowCount()):
        if tabla.item(row, 0).text() == "999999":
            encontrado = True
            break
    assert encontrado

    # Limpiar
    view.close()
    shutil.rmtree(temp_dir, ignore_errors=True)
