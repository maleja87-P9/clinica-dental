from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from controladores.auth_controller import AuthController
from controladores.cita_controller import CitaController
from controladores.factura_controller import FacturaController
from controladores.historial_controller import HistorialController
from controladores.notificacion_controller import NotificacionController
from controladores.paciente_controller import PacienteController
from controladores.pago_controller import PagoController
from controladores.reporte_controller import ReporteController
from controladores.usuario_controller import UsuarioController
from utils.backup_manager import BackupManager
from vistas.citas_view import CitasView
from vistas.facturacion_view import FacturacionView
from vistas.historial_view import HistorialView
from vistas.notificaciones_view import NotificacionesView
from vistas.pacientes_view import PacientesView
from vistas.reportes_view import ReportesView
from vistas.seguridad_view import SeguridadView


class VentanaPrincipalClinica(QMainWindow):
    cerrar_sesion_solicitada = Signal()

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self._sesion_cerrada = False
        self.setWindowTitle("🦷 Sistema de Gestión Clínica Dental Sonrisa Perfecta")
        self.resize(1300, 800)
        self.setup_estilo()

        self.usuario_controller = UsuarioController()
        self.auth_controller = AuthController(self.usuario_controller)
        self.paciente_controller = PacienteController()
        self.cita_controller = CitaController(paciente_controller=self.paciente_controller)
        self.historial_controller = HistorialController(paciente_controller=self.paciente_controller)
        self.factura_controller = FacturaController(paciente_controller=self.paciente_controller)
        self.pago_controller = PagoController(factura_controller=self.factura_controller)
        self.notificacion_controller = NotificacionController(
            paciente_controller=self.paciente_controller
        )
        self.reporte_controller = ReporteController(
            paciente_controller=self.paciente_controller,
            cita_controller=self.cita_controller,
            historial_controller=self.historial_controller,
            factura_controller=self.factura_controller,
            pago_controller=self.pago_controller,
        )
        self._ejecutar_backup_diario()
        self._construir_ui()

    def setup_estilo(self):
        self.setStyleSheet("""
            /* Fondo general */
            QMainWindow, QWidget {
                background-color: #f0f7fc;
            }

            /* Estilo de las pestañas */
            QTabWidget::pane {
                border: 2px solid #b8d4e8;
                border-radius: 10px;
                background-color: #ffffff;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #d9eaf5;
                color: #0a3b5c;
                padding: 10px 20px;
                margin: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #2c7da0;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #b8d4e8;
                color: #0a3b5c;
            }

            /* Botones */
            QPushButton {
                background-color: #2c7da0;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1f5e7a;
            }
            QPushButton:pressed {
                background-color: #154c63;
            }

            /* Etiquetas */
            QLabel {
                color: #0a3b5c;
                background-color: transparent;
                font-size: 12px;
            }

            /* Campos de entrada */
            QLineEdit {
                border: 2px solid #cde1ef;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #ffffff;
                color: #000000;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2c7da0;
            }
            QLineEdit:disabled {
                background-color: #eef2f5;
                color: #555555;
            }

            /* Tablas */
            QTableWidget {
                alternate-background-color: #f8fbfd;
                selection-background-color: #cde1ef;
                selection-color: #0a3b5c;
                gridline-color: #d4e4f0;
                background-color: #ffffff;
                color: #000000;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #2c7da0;
                color: #ffffff;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }

            /* ComboBox */
            QComboBox {
                border: 2px solid #cde1ef;
                border-radius: 6px;
                padding: 5px 8px;
                background-color: #ffffff;
                color: #000000;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #cde1ef;
                selection-color: #0a3b5c;
            }

            /* DateEdit y TimeEdit */
            QDateEdit, QTimeEdit {
                border: 2px solid #cde1ef;
                border-radius: 6px;
                padding: 5px 8px;
                background-color: #ffffff;
                color: #000000;
                font-size: 12px;
            }
            QDateEdit:focus, QTimeEdit:focus {
                border-color: #2c7da0;
            }

            /* TextEdit */
            QTextEdit {
                border: 2px solid #cde1ef;
                border-radius: 6px;
                background-color: #ffffff;
                color: #000000;
                font-size: 12px;
            }
            QTextEdit:focus {
                border-color: #2c7da0;
            }

            /* GroupBox */
            QGroupBox {
                font-weight: bold;
                border: 2px solid #b8d4e8;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 10px;
                color: #0a3b5c;
                background-color: #ffffff;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
            }

            /* Message Box */
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #000000;
            }

            /* Scrollbars */
            QScrollBar:vertical {
                background-color: #eef2f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2c7da0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #1f5e7a;
            }
        """)

    def _ejecutar_backup_diario(self):
        respaldo = BackupManager.crear_respaldo_diario_si_no_existe()
        if respaldo.get("creado"):
            self.usuario_controller.registrar_bitacora(
                self.usuario_actual,
                "backup_diario",
                f"Backup diario creado en {respaldo['destino']}.",
                "OK",
            )

    def _construir_ui(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setSpacing(10)

        encabezado = QHBoxLayout()
        permisos = ", ".join(self.auth_controller.obtener_permisos(self.usuario_actual))

        etiqueta = QLabel(
            f"👤 Usuario: {self.usuario_actual.get('nombre')} | "
            f"⭐ Rol: {self.usuario_actual.get('rol')} | "
            f"🔑 Permisos: {permisos}"
        )
        etiqueta.setStyleSheet("background-color: #d9eaf5; padding: 8px 12px; border-radius: 8px; font-weight: bold; color: #0a3b5c; font-size: 12px;")

        encabezado.addWidget(etiqueta)
        encabezado.addStretch()

        self.boton_backup = QPushButton("💾 Backup rápido")
        self.boton_backup.clicked.connect(self.crear_backup_rapido)
        self.boton_backup.setVisible(
            self.auth_controller.tiene_permiso(self.usuario_actual, "seguridad")
        )
        encabezado.addWidget(self.boton_backup)

        boton_logout = QPushButton("🚪 Cerrar sesión")
        boton_logout.clicked.connect(self.cerrar_sesion)
        encabezado.addWidget(boton_logout)

        layout.addLayout(encabezado)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.setCentralWidget(contenedor)
        self._construir_tabs()
        self.tabs.currentChanged.connect(lambda _: self.refrescar_vistas())

    def _construir_tabs(self):
        permisos = set(self.auth_controller.obtener_permisos(self.usuario_actual))
        self.vistas = []

        if "pacientes" in permisos:
            vista = PacientesView(self.paciente_controller, on_change=self.refrescar_vistas)
            self.tabs.addTab(vista, "👥 Pacientes")
            self.vistas.append(vista)

        if "citas" in permisos:
            vista = CitasView(
                self.cita_controller,
                self.paciente_controller,
                self.notificacion_controller,
                self.usuario_controller,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "📅 Citas")
            self.vistas.append(vista)

        if "historial" in permisos:
            vista = HistorialView(
                self.historial_controller,
                self.paciente_controller,
                self.usuario_controller,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "📋 Historial médico")
            self.vistas.append(vista)

        if "facturacion" in permisos:
            vista = FacturacionView(
                self.factura_controller,
                self.pago_controller,
                self.paciente_controller,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "💰 Facturación y pagos")
            self.vistas.append(vista)


        if "reportes" in permisos:
            vista = ReportesView(self.reporte_controller)
            self.tabs.addTab(vista, "📊 Reportes")
            self.vistas.append(vista)

        if "notificaciones" in permisos:
            # AHORA SÍ: pasamos primero notificacion_controller y luego paciente_controller
            vista = NotificacionesView(self.notificacion_controller, self.paciente_controller)
            self.tabs.addTab(vista, "🔔 Notificaciones")
            self.vistas.append(vista)

        if "seguridad" in permisos:
            vista = SeguridadView(
                self.usuario_controller,
                self.usuario_actual,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "🔒 Seguridad")
            self.vistas.append(vista)

    def refrescar_vistas(self):
        for vista in self.vistas:
            refrescar = getattr(vista, "refrescar_datos", None)
            if callable(refrescar):
                refrescar()

    def crear_backup_rapido(self):
        respaldo = BackupManager.crear_respaldo()
        self.usuario_controller.registrar_bitacora(
            self.usuario_actual,
            "backup_rapido",
            f"Backup rapido en {respaldo['destino']}.",
            "OK",
        )
        QMessageBox.information(
            self,
            "Backup",
            f"✅ Se copiaron {respaldo['archivos']} archivos en:\n{respaldo['destino']}",
        )
        self.refrescar_vistas()

    def cerrar_sesion(self):
        self._sesion_cerrada = True
        self.auth_controller.cerrar_sesion(self.usuario_actual)
        self.close()
        self.cerrar_sesion_solicitada.emit()

    def closeEvent(self, event):
        if not self._sesion_cerrada:
            self.auth_controller.cerrar_sesion(self.usuario_actual)
        super().closeEvent(event)
