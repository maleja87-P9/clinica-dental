import shutil
import unittest
import uuid
from pathlib import Path

from controladores.auth_controller import AuthController
from controladores.cita_controller import CitaController
from controladores.factura_controller import FacturaController
from controladores.historial_controller import HistorialController
from controladores.notificacion_controller import NotificacionController
from controladores.paciente_controller import PacienteController
from controladores.pago_controller import PagoController
from controladores.reporte_controller import ReporteController
from controladores.usuario_controller import UsuarioController
from modelos.cita import Cita
from modelos.factura import Factura
from modelos.historial_medico import HistorialMedico
from modelos.paciente import Paciente
from modelos.pago import Pago
from utils.backup_manager import BackupManager
from utils.json_manager import JsonManager


class FlujoClinicoFinancieroTestCase(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[1] / ".tmp_test_runs"
        base.mkdir(exist_ok=True)
        self.temp_dir = base / f"run_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir()
        self.paciente_controller = PacienteController(self.temp_dir / "pacientes.json")
        self.cita_controller = CitaController(
            self.temp_dir / "citas.json",
            paciente_controller=self.paciente_controller,
        )
        self.historial_controller = HistorialController(
            self.temp_dir / "historiales.json",
            paciente_controller=self.paciente_controller,
        )
        self.factura_controller = FacturaController(
            self.temp_dir / "facturas.json",
            paciente_controller=self.paciente_controller,
        )
        self.pago_controller = PagoController(
            self.temp_dir / "pagos.json",
            factura_controller=self.factura_controller,
        )
        self.usuario_controller = UsuarioController(
            self.temp_dir / "usuarios.json",
            self.temp_dir / "roles.json",
            self.temp_dir / "bitacora.json",
        )
        self.auth_controller = AuthController(self.usuario_controller)
        self.notificacion_controller = NotificacionController(
            self.temp_dir / "notificaciones.json",
            paciente_controller=self.paciente_controller,
        )
        self.reporte_controller = ReporteController(
            paciente_controller=self.paciente_controller,
            cita_controller=self.cita_controller,
            historial_controller=self.historial_controller,
            factura_controller=self.factura_controller,
            pago_controller=self.pago_controller,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_flujo_integrado_con_exportacion(self):
        exito, _ = self.paciente_controller.registrar_paciente(
            Paciente("3003", "Andrea Molina", "3101112233", "andrea@example.com", "Avenida 1")
        )
        self.assertTrue(exito)

        exito, _ = self.cita_controller.agendar_cita(
            Cita(
                "3003",
                "2026-08-15",
                motivo="Ortodoncia",
                odontologo="Dr. Sofia Herrera",
                hora="11:30",
                nombre_paciente="Andrea Molina",
            )
        )
        self.assertTrue(exito)

        cita = self.cita_controller.listar_todas()[0]
        self.notificacion_controller.crear_confirmacion_cita(cita)
        self.notificacion_controller.crear_recordatorio_cita(cita)
        self.assertEqual(len(self.notificacion_controller.listar_notificaciones()), 2)

        exito, _ = self.historial_controller.registrar_entrada(
            HistorialMedico(
                "3003",
                "Dr. Sofia Herrera",
                "Apinamiento dental",
                "Ajuste de brackets",
                "Continuar control mensual",
            )
        )
        self.assertTrue(exito)

        exito, _ = self.factura_controller.generar_factura(
            Factura("3003", "Ajuste de ortodoncia", 250000, nombre_paciente="Andrea Molina")
        )
        self.assertTrue(exito)
        factura = self.factura_controller.listar_facturas()[0]

        exito, _ = self.pago_controller.registrar_pago(
            Pago(
                factura["id_factura"],
                100000,
                "Tarjeta",
                documento_paciente="3003",
            )
        )
        self.assertTrue(exito)

        saldo = self.pago_controller.calcular_saldo_pendiente(factura["id_factura"])
        self.assertEqual(saldo, 150000.0)

        reporte = self.reporte_controller.reporte_financiero_por_rango("2026-08-01", "2026-08-31")
        ruta_csv = self.reporte_controller.exportar_reporte_csv(reporte, "reporte_financiero")
        self.assertTrue(Path(ruta_csv).exists())

    def test_login_mfa_y_bitacora(self):
        exito, mensaje, _ = self.auth_controller.iniciar_sesion("doctor", "doctor123", "")
        self.assertFalse(exito)
        self.assertIn("mfa", mensaje.lower())

        exito, mensaje, usuario = self.auth_controller.iniciar_sesion("doctor", "doctor123", "123456")
        self.assertTrue(exito)
        self.assertEqual(usuario["rol"], "odontologo")

        bitacora = self.usuario_controller.listar_bitacora()
        self.assertGreaterEqual(len(bitacora), 2)
        self.assertEqual(bitacora[-1]["resultado"], "OK")

    def test_backup_diario_se_ejecuta_solo_una_vez(self):
        original_base_dir = JsonManager.BASE_DIR
        original_data_dir = JsonManager.DATA_DIR
        try:
            JsonManager.BASE_DIR = self.temp_dir
            JsonManager.DATA_DIR = self.temp_dir / "data"
            JsonManager.DATA_DIR.mkdir(parents=True, exist_ok=True)
            (JsonManager.DATA_DIR / "pacientes.json").write_text("[]", encoding="utf-8")
            (JsonManager.DATA_DIR / "usuarios.json").write_text("[]", encoding="utf-8")

            primero = BackupManager.crear_respaldo_diario_si_no_existe()
            segundo = BackupManager.crear_respaldo_diario_si_no_existe()

            self.assertTrue(primero["creado"])
            self.assertFalse(segundo["creado"])
            self.assertTrue(Path(primero["destino"]).exists())
        finally:
            JsonManager.BASE_DIR = original_base_dir
            JsonManager.DATA_DIR = original_data_dir
