import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMessageBox, QApplication, QPushButton
from PySide6.QtTest import QTest

from vistas.login_view import LoginView
from vistas.pacientes_view import PacientesView
from vistas.citas_view import CitasView
from vistas.historial_view import HistorialView
from vistas.facturacion_view import FacturacionView
from vistas.reportes_view import ReportesView


def cerrar_msgbox_automatico(qtbot, delay=800):
    """Cierra automáticamente cualquier QMessageBox que aparezca."""
    def cerrar():
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QMessageBox):
                ok_btn = w.button(QMessageBox.Ok)
                if ok_btn:
                    qtbot.mouseClick(ok_btn, Qt.LeftButton)
                else:
                    w.accept()
    QTimer.singleShot(delay, cerrar)


def test_flujo_completo_robot(
    qtbot,
    auth_controller,
    paciente_controller,
    cita_controller,
    usuario_controller,
    historial_controller,
    factura_controller,
    pago_controller,
    notificacion_controller,
    reporte_controller
):
    """
    Prueba end‑to‑end (robot) que verifica el flujo completo del sistema:
    Login → Registrar paciente → Agendar cita → Historial → Factura + Pago → Reporte
    """

    # ------------------------------------------------------------
    # 1. LOGIN (usuario admin sin MFA)
    # ------------------------------------------------------------
    login = LoginView(auth_controller)
    qtbot.addWidget(login)
    login.show()
    QTest.qWait(500)

    qtbot.keyClicks(login.input_usuario, "admin")
    qtbot.keyClicks(login.input_password, "admin123")
    cerrar_msgbox_automatico(qtbot)
    qtbot.mouseClick(login.boton_ingresar, Qt.LeftButton)
    QTest.qWait(1500)

    assert login.result() == LoginView.Accepted
    usuario_actual = login.usuario_autenticado
    assert usuario_actual["rol"] == "administrador"
    login.close()

    # ------------------------------------------------------------
    # 2. REGISTRAR PACIENTE
    # ------------------------------------------------------------
    pacientes = PacientesView(paciente_controller)
    qtbot.addWidget(pacientes)
    pacientes.show()
    QTest.qWait(500)

    qtbot.keyClicks(pacientes.input_documento, "999888777")
    qtbot.keyClicks(pacientes.input_nombre, "Robot E2E")
    qtbot.keyClicks(pacientes.input_telefono, "555111222")
    qtbot.keyClicks(pacientes.input_correo, "robot@prueba.com")
    qtbot.keyClicks(pacientes.input_direccion, "Calle Automatizada 456")

    cerrar_msgbox_automatico(qtbot)
    # El botón "Registrar" no tiene objectName, lo buscamos por texto
    btn_registrar = pacientes.findChild(QPushButton, "Registrar")
    assert btn_registrar is not None
    qtbot.mouseClick(btn_registrar, Qt.LeftButton)
    QTest.qWait(1500)

    paciente_db = paciente_controller.buscar_por_documento("999888777")
    assert paciente_db is not None
    assert paciente_db["nombre"] == "Robot E2E"
    pacientes.close()

    # ------------------------------------------------------------
    # 3. AGENDAR CITA
    # ------------------------------------------------------------
    citas = CitasView(
        cita_controller,
        paciente_controller,
        notificacion_controller,
        usuario_controller
    )
    qtbot.addWidget(citas)
    citas.show()
    QTest.qWait(500)

    qtbot.keyClicks(citas.input_documento, "999888777")
    citas._obtener_nombre_paciente()   # carga el nombre
    qtbot.keyClicks(citas.input_motivo, "Revisión robotizada")
    # Fecha: dentro de 10 días (evita conflictos con fechas pasadas)
    citas.fecha.setDate(citas.fecha.date().addDays(10))

    cerrar_msgbox_automatico(qtbot)
    qtbot.mouseClick(citas.boton_agendar, Qt.LeftButton)
    QTest.qWait(1500)

    todas_citas = cita_controller.listar_todas()
    assert len(todas_citas) >= 1
    cita_paciente = [c for c in todas_citas if c["documento_paciente"] == "999888777"]
    assert len(cita_paciente) == 1
    citas.close()

    # ------------------------------------------------------------
    # 4. REGISTRAR HISTORIAL CLÍNICO
    # ------------------------------------------------------------
    historial = HistorialView(
        historial_controller,
        paciente_controller,
        usuario_controller
    )
    qtbot.addWidget(historial)
    historial.show()
    QTest.qWait(500)

    qtbot.keyClicks(historial.input_documento, "999888777")
    qtbot.keyClicks(historial.input_diagnostico, "Diagnóstico automatizado")
    qtbot.keyClicks(historial.input_tratamiento, "Tratamiento de prueba")

    cerrar_msgbox_automatico(qtbot)
    qtbot.mouseClick(historial.boton_registrar, Qt.LeftButton)
    QTest.qWait(1500)

    registros = historial_controller.consultar_por_paciente("999888777")
    assert len(registros) == 1
    assert "automatizado" in registros[0]["diagnostico"].lower()
    historial.close()

    # ------------------------------------------------------------
    # 5. FACTURACIÓN Y PAGO
    # ------------------------------------------------------------
    facturacion = FacturacionView(
        factura_controller,
        pago_controller,
        paciente_controller
    )
    qtbot.addWidget(facturacion)
    facturacion.show()
    QTest.qWait(500)

    qtbot.keyClicks(facturacion.input_documento, "999888777")
    qtbot.keyClicks(facturacion.input_concepto, "Consulta robot")
    qtbot.keyClicks(facturacion.input_valor_total, "85000")

    cerrar_msgbox_automatico(qtbot)
    qtbot.mouseClick(facturacion.boton_generar, Qt.LeftButton)
    QTest.qWait(1500)

    facturas = factura_controller.buscar_por_paciente("999888777")
    assert len(facturas) == 1
    id_factura = facturas[0]["id_factura"]

    # Seleccionar la factura en la tabla
    facturacion.tabla_facturas.selectRow(0)
    QTest.qWait(300)

    qtbot.keyClicks(facturacion.input_valor_pago, "30000")
    cerrar_msgbox_automatico(qtbot)
    qtbot.mouseClick(facturacion.boton_pago, Qt.LeftButton)
    QTest.qWait(1500)

    saldo = pago_controller.calcular_saldo_pendiente(id_factura)
    assert saldo == 55000.0
    facturacion.close()

    # ------------------------------------------------------------
    # 6. GENERAR REPORTE (solo verificar que funciona)
    # ------------------------------------------------------------
    reportes = ReportesView(reporte_controller)
    qtbot.addWidget(reportes)
    reportes.show()
    QTest.qWait(500)

    reportes.combo_tipo.setCurrentText("Pacientes registrados")
    qtbot.mouseClick(reportes.boton_generar, Qt.LeftButton)
    QTest.qWait(1000)

    assert "Robot E2E" in reportes.area_resumen.toPlainText()
    reportes.close()

    # Si llegamos hasta aquí, todo funciona correctamente
    print("\n🤖 PRUEBA ROBOT COMPLETA: TODOS LOS PASOS EXITOSOS")
