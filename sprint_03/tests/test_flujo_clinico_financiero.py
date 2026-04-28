import shutil
import unittest
import uuid
from pathlib import Path

from controladores.cita_controller import CitaController
from controladores.notificacion_controller import NotificacionController
from controladores.paciente_controller import PacienteController
from controladores.reporte_controller import ReporteController
from modelos.cita import Cita
from modelos.paciente import Paciente


class ReportesYNotificacionesTestCase(unittest.TestCase):
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
        self.notificacion_controller = NotificacionController(
            self.temp_dir / "notificaciones.json",
            paciente_controller=self.paciente_controller,
        )
        self.reporte_controller = ReporteController(
            paciente_controller=self.paciente_controller,
            cita_controller=self.cita_controller,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_crea_recordatorios_y_exporta_csv(self):
        exito, _ = self.paciente_controller.registrar_paciente(
            Paciente("5005", "Mariana Perez", "3011110000", "mariana@example.com", "Calle 10")
        )
        self.assertTrue(exito)

        exito, _ = self.cita_controller.agendar_cita(
            Cita(
                "5005",
                "2026-10-01",
                motivo="Control",
                odontologo="Dr. Sofia Herrera",
                hora="09:30",
                nombre_paciente="Mariana Perez",
            )
        )
        self.assertTrue(exito)

        cita = self.cita_controller.listar_todas()[0]
        self.notificacion_controller.crear_confirmacion_cita(cita)
        self.notificacion_controller.crear_recordatorio_cita(cita)
        self.assertEqual(len(self.notificacion_controller.listar_notificaciones()), 2)

        reporte = self.reporte_controller.reporte_citas_por_rango("2026-10-01", "2026-10-31")
        self.assertEqual(reporte["titulo"], "Citas por rango de fechas")
        ruta_csv = self.reporte_controller.exportar_reporte_csv(reporte, "citas_octubre")
        self.assertTrue(Path(ruta_csv).exists())
        self.assertIn("citas_octubre", Path(ruta_csv).name)
