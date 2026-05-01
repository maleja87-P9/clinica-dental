from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QFrame,
)

from controladores.auth_controller import AuthController


class LoginView(QDialog):
    def __init__(self, auth_controller=None, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller or AuthController()
        self.usuario_autenticado = None
        self.setWindowTitle("Inicio de sesión - Sonrisa Perfecta")
        self.resize(450, 400)
        self.setup_estilo()
        self._construir_ui()

    def setup_estilo(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f4f8;
            }
            QLabel {
                color: #0d3b66;
                font-size: 12px;
                background-color: transparent;
            }
            QLineEdit {
                border: 2px solid #b0c4de;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #0d6efd;
                background-color: #ffffff;
            }
            QLineEdit[placeholderText=""] {
                color: #000000;
            }
            QPushButton {
                background-color: #0d6efd;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QFrame[frameShape="4"] {
                background-color: #b0c4de;
                max-height: 2px;
            }
        """)

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("🦷 Sonrisa Perfecta")
        titulo.setAlignment(Qt.AlignCenter)
        titulo_font = QFont()
        titulo_font.setPointSize(20)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet("color: #0d3b66; margin-bottom: 5px; background-color: transparent;")
        layout.addWidget(titulo)

        subtitulo = QLabel("Sistema de Gestión Clínica Dental")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #2c7da0; margin-bottom: 20px; font-size: 13px; background-color: transparent;")
        layout.addWidget(subtitulo)

        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: #b0c4de; max-height: 2px;")
        layout.addWidget(separador)

        # Ayuda
        ayuda = QLabel(
            "📋 USUARIOS DE PRUEBA:\n"
            "┌─────────────────┬─────────────────┬──────────────┐\n"
            "│ Usuario         │ Contraseña      │ Rol          │\n"
            "├─────────────────┼─────────────────┼──────────────┤\n"
            "│ admin           │ admin123        │ Administrador│\n"
            "│ recepcion       │ recepcion123    │ Recepcionista│\n"
            "│ doctor          │ doctor123       │ Odontólogo   │\n"
            "│ gerencia        │ gerencia123     │ Gerente      │\n"
            "└─────────────────┴─────────────────┴──────────────┘"
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("background-color: #ffffff; padding: 12px; border-radius: 8px; color: #0d3b66; font-family: monospace; font-size: 11px; border: 1px solid #b0c4de;")
        layout.addWidget(ayuda)

        # Formulario
        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Ej: admin, recepcion, doctor, gerencia")
        self.input_usuario.setStyleSheet("color: #000000; background-color: #ffffff;")

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Ingrese su contraseña")
        self.input_password.setStyleSheet("color: #000000; background-color: #ffffff;")

        label_usuario = QLabel("👤 USUARIO:")
        label_usuario.setStyleSheet("color: #0d3b66; font-weight: bold; font-size: 12px;")
        label_password = QLabel("🔒 CONTRASEÑA:")
        label_password.setStyleSheet("color: #0d3b66; font-weight: bold; font-size: 12px;")

        formulario.addRow(label_usuario, self.input_usuario)
        formulario.addRow(label_password, self.input_password)

        layout.addLayout(formulario)

        self.boton_ingresar = QPushButton(" INGRESAR ")
        self.boton_ingresar.clicked.connect(self.procesar_login)
        self.boton_ingresar.setMinimumHeight(42)
        self.boton_ingresar.setCursor(Qt.PointingHandCursor)
        self.boton_ingresar.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.boton_ingresar)

        # Tecla Enter para ingresar
        self.input_password.returnPressed.connect(self.procesar_login)
        self.input_usuario.returnPressed.connect(self.procesar_login)

    def procesar_login(self):
        username = self.input_usuario.text().strip()
        password = self.input_password.text().strip()

        # Validación de campos vacíos
        if not username:
            QMessageBox.warning(self, "Campos incompletos", "❌ El campo 'Usuario' es obligatorio.")
            self.input_usuario.setFocus()
            return
        if not password:
            QMessageBox.warning(self, "Campos incompletos", "❌ El campo 'Contraseña' es obligatorio.")
            self.input_password.setFocus()
            return

        exito, mensaje, usuario = self.auth_controller.iniciar_sesion(username, password, "")

        if not exito:
            QMessageBox.warning(self, "Acceso denegado", f"❌ {mensaje}")
            self.input_password.clear()
            self.input_password.setFocus()
            return

        self.usuario_autenticado = usuario
        QMessageBox.information(self, "Acceso concedido", f"✅ {mensaje}\n\nBienvenido/a {usuario.get('nombre')}!")
        self.accept()
