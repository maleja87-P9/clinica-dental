import shutil
import tempfile
import pytest
from pathlib import Path

from controladores.auth_controller import AuthController
from controladores.cita_controller import CitaController
from controladores.paciente_controller import PacienteController
from controladores.usuario_controller import UsuarioController
from controladores.factura_controller import FacturaController
from controladores.pago_controller import PagoController
from controladores.historial_controller import HistorialController
from controladores.notificacion_controller import NotificacionController
from controladores.reporte_controller import ReporteController

@pytest.fixture
def temp_data_dir():
    """Crea un directorio temporal para los archivos JSON de cada prueba."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def paciente_controller(temp_data_dir):
    return PacienteController(temp_data_dir / "pacientes.json")

@pytest.fixture
def usuario_controller(temp_data_dir):
    return UsuarioController(
        temp_data_dir / "usuarios.json",
        temp_data_dir / "roles.json",
        temp_data_dir / "bitacora.json"
    )

@pytest.fixture
def auth_controller(usuario_controller):
    return AuthController(usuario_controller)

@pytest.fixture
def cita_controller(temp_data_dir, paciente_controller):
    return CitaController(temp_data_dir / "citas.json", paciente_controller=paciente_controller)

@pytest.fixture
def factura_controller(temp_data_dir, paciente_controller):
    return FacturaController(temp_data_dir / "facturas.json", paciente_controller=paciente_controller)

@pytest.fixture
def pago_controller(temp_data_dir, factura_controller):
    return PagoController(temp_data_dir / "pagos.json", factura_controller=factura_controller)

@pytest.fixture
def historial_controller(temp_data_dir, paciente_controller):
    return HistorialController(temp_data_dir / "historiales.json", paciente_controller=paciente_controller)

@pytest.fixture
def notificacion_controller(temp_data_dir, paciente_controller):
    return NotificacionController(temp_data_dir / "notificaciones.json", paciente_controller=paciente_controller)

@pytest.fixture
def reporte_controller(paciente_controller, cita_controller, historial_controller,
                       factura_controller, pago_controller):
    return ReporteController(
        paciente_controller=paciente_controller,
        cita_controller=cita_controller,
        historial_controller=historial_controller,
        factura_controller=factura_controller,
        pago_controller=pago_controller
    )
