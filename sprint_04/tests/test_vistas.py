import pytest
from PySide6.QtWidgets import QApplication
from vistas.login_view import LoginView
from controladores.auth_controller import AuthController

@pytest.fixture
def app(qtbot):
    """Fixture que ya proporciona QApplication automáticamente con pytest-qt."""
    pass  # qtbot ya maneja la aplicación

def test_login_exitoso_sin_mfa(qtbot, usuario_controller):
    # Preparamos un usuario sin MFA en la base de datos temporal
    from modelos.usuario import Usuario
    usuario = Usuario("testuser", "1234", "Test", "recepcionista", mfa_habilitado=False)
    usuario_controller.registrar_usuario(usuario)

    auth = AuthController(usuario_controller)
    view = LoginView(auth)
    qtbot.addWidget(view)

    # Simular escritura en los campos
    qtbot.keyClicks(view.input_usuario, "testuser")
    qtbot.keyClicks(view.input_password, "1234")
    # No ingresamos MFA
    qtbot.mouseClick(view.boton_ingresar, QtCore.Qt.LeftButton)

    # Verificar que el diálogo se aceptó (login exitoso)
    assert view.result() == LoginView.Accepted
    assert view.usuario_autenticado is not None
    assert view.usuario_autenticado["username"] == "testuser"

def test_login_con_mfa_incorrecto(qtbot, usuario_controller):
    from modelos.usuario import Usuario
    usuario = Usuario("docmfa", "pass", "Doctor MFA", "odontologo", mfa_habilitado=True)
    usuario_controller.registrar_usuario(usuario)

    auth = AuthController(usuario_controller)
    view = LoginView(auth)
    qtbot.addWidget(view)

    qtbot.keyClicks(view.input_usuario, "docmfa")
    qtbot.keyClicks(view.input_password, "pass")
    qtbot.keyClicks(view.input_mfa, "000000")  # código incorrecto
    qtbot.mouseClick(view.boton_ingresar, QtCore.Qt.LeftButton)

    # El diálogo no debe aceptarse y debe mostrar advertencia
    assert view.result() != LoginView.Accepted
    # Opcional: verificar que el QMessageBox se mostró (más avanzado)
