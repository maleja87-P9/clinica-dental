import pytest
from pathlib import Path
import shutil
import tempfile
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from controladores.paciente_controller import PacienteController
from vistas.pacientes_view import PacientesView

@pytest.fixture
def temp_paciente_controller():
    """Fixture que crea un controlador aislado en directorio temporal."""
    temp_dir = tempfile.mkdtemp()
    controller = PacienteController(Path(temp_dir) / "pacientes.json")
    yield controller
    # Limpieza después de la prueba
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_registrar_paciente_visual(qtbot, temp_paciente_controller):
    # 1. Crear la vista
    view = PacientesView(temp_paciente_controller)
    # 2. Agregar la vista a qtbot para que la cierre automáticamente al final
    qtbot.addWidget(view)
    # 3. Mostrar la ventana (visible)
    view.show()
    # 4. Esperar un poco para que se renderice
    qtbot.wait(500)  # milisegundos

    # 5. Simular escritura en campos (keyClicks escribe texto completo)
    qtbot.keyClicks(view.input_documento, "12345678")
    qtbot.wait(300)
    qtbot.keyClicks(view.input_nombre, "María López")
    qtbot.wait(300)
    qtbot.keyClicks(view.input_telefono, "3105556666")
    qtbot.wait(300)
    qtbot.keyClicks(view.input_correo, "maria@test.com")
    qtbot.wait(300)
    qtbot.keyClicks(view.input_direccion, "Carrera 99 #12-34")
    qtbot.wait(300)

    # 6. Manejar el QMessageBox que aparecerá tras el registro
    #    Usamos with qtbot.waitSignal para esperar la señal clicked del botón,
    #    y además capturamos el diálogo automáticamente.
    with qtbot.waitSignal(view.boton_registrar.clicked, timeout=3000):
        qtbot.mouseClick(view.boton_registrar, Qt.LeftButton)

    # 7. Esperar un poco para que el mensaje se muestre y luego se cierre
    #    (qtbot no cierra automáticamente los QMessageBox, pero podemos usar
    #     un QTimer o simplemente esperar y luego aceptar manualmente)
    #    Opción sencilla: esperar un poco y luego buscar el QMessageBox para cerrarlo
    qtbot.wait(1500)  # dejar visible el mensaje por 1.5 segundos
    # Buscar QMessageBox y hacer clic en OK
    for widget in qtbot.qapp.topLevelWidgets():
        if isinstance(widget, QMessageBox):
            ok_button = widget.button(QMessageBox.Ok)
            if ok_button:
                qtbot.mouseClick(ok_button, Qt.LeftButton)
            else:
                widget.accept()
            break

    # 8. Verificar que el paciente se registró realmente
    view.refrescar_datos()
    tabla = view.tabla
    encontrado = False
    for row in range(tabla.rowCount()):
        if tabla.item(row, 0).text() == "12345678":
            assert tabla.item(row, 1).text() == "María López"
            encontrado = True
            break
    assert encontrado

    # 9. Al final, qtbot cerrará la ventana automáticamente porque usamos addWidget
    #    La limpieza del temp_dir la hace el fixture.
