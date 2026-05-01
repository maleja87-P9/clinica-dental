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
    def cerrar():
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QMessageBox):
                ok_btn = w.button(QMessageBox.Ok)
                if ok_btn:
                    qtbot.mouseClick(ok_btn, Qt.LeftButton)
                else:
                    w.accept()
    QTimer.singleShot(delay, cerrar)


def buscar_boton_por_texto(widget, texto):
    for btn in widget.findChildren(QPushButton):
        if btn.text() == texto:
            return btn
    return None


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
    print("\n[1] Login...")
    login = LoginView(auth_controller)
    qtbot.addWidget(login)
    login.show()
    QTest.qWait(1000)

    login.input_usuario.setText("admin")
    login.input_password.setText("admin123")
    QTest.qWait(500)

    cerrar_msgbox_automatico(qtbot, delay=500)
    qtbot.mouseClick(login.boton_ingresar, Qt.LeftButton)
    QTest.qWait(2000)

    assert login.result() == LoginView.Accepted
    assert login.usuario_autenticado["rol"] == "administrador"
    print("[1] Login OK")
    login.close()
    QTest.qWait(500)

    print("\n[2] Registrar paciente...")
    pacientes = PacientesView(paciente_controller)
    qtbot.addWidget(pacientes)
    pacientes.show()
    QTest.qWait(1000)

    pacientes.input_documento.setText("999888777")
    pacientes.input_nombre.setText("Robot E2E")
    pacientes.input_telefono.setText("555111222")
    pacientes.input_correo.setText("robot@prueba.com")
    pacientes.input_direccion.setText("Calle Automatizada 456")
    QTest.qWait(500)

    cerrar_msgbox_automatico(qtbot, delay=500)
    btn_registrar = buscar_boton_por_texto(pacientes, "Registrar")
    assert btn_registrar is not None
    qtbot.mouseClick(btn_registrar, Qt.LeftButton)
    QTest.qWait(2000)

    paciente_db = paciente_controller.buscar_por_documento("999888777")
    assert paciente_db is not None
    assert paciente_db["nombre"] == "Robot E2E"
    print("[2] Paciente registrado OK")
    pacientes.close()
    QTest.qWait(500)

    print("\n[3] Agendar cita...")
    citas = CitasView(
        cita_controller,
        paciente_controller,
        notificacion_controller,
        usuario_controller
    )
    qtbot.addWidget(citas)
    citas.show()
    QTest.qWait(1000)

    citas.input_documento.setText("999888777")
    QTest.qWait(500)
    citas._obtener_nombre_paciente()
    QTest.qWait(500)
    citas.input_motivo.setText("Revisión robotizada")
    citas.fecha.setDate(citas.fecha.date().addDays(10))
    QTest.qWait(500)

    cerrar_msgbox_automatico(qtbot, delay=500)
    btn_agendar = buscar_boton_por_texto(citas, "Agendar")
    assert btn_agendar is not None
    qtbot.mouseClick(btn_agendar, Qt.LeftButton)
    QTest.qWait(2000)

    todas_citas = cita_controller.listar_todas()
    assert len(todas_citas) >= 1
    cita_paciente = [c for c in todas_citas if c["documento_paciente"] == "999888777"]
    assert len(cita_paciente) == 1
    print("[3] Cita agendada OK")
    citas.close()
    QTest.qWait(500)

    print("\n[4] Historial clínico...")
    historial = HistorialView(
        historial_controller,
        paciente_controller,
        usuario_controller
    )
    qtbot.addWidget(historial)
    historial.show()
    QTest.qWait(1000)

    historial.input_documento.setText("999888777")
    QTest.qWait(500)
    historial.input_diagnostico.setText("Diagnóstico automatizado")
    historial.input_tratamiento.setText("Tratamiento de prueba")
    QTest.qWait(500)

    cerrar_msgbox_automatico(qtbot, delay=500)
    btn_historial = buscar_boton_por_texto(historial, "Registrar entrada")
    if btn_historial is None:
        btn_historial = buscar_boton_por_texto(historial, "Registrar")
    assert btn_historial is not None
    qtbot.mouseClick(btn_historial, Qt.LeftButton)
    QTest.qWait(2000)

    registros = historial_controller.consultar_por_paciente("999888777")
    assert len(registros) == 1
    assert "automatizado" in registros[0]["diagnostico"].lower()
    print("[4] Historial OK")
    historial.close()
    QTest.qWait(500)

    print("\n[5] Facturación y pago...")
    facturacion = FacturacionView(
        factura_controller,
        pago_controller,
        paciente_controller
    )
    qtbot.addWidget(facturacion)
    facturacion.show()
    QTest.qWait(1000)

    facturacion.input_documento.setText("999888777")
    facturacion.input_concepto.setText("Consulta robot")
    facturacion.input_valor_total.setText("85000")
    QTest.qWait(500)

    cerrar_msgbox_automatico(qtbot, delay=500)
    btn_generar = buscar_boton_por_texto(facturacion, "Generar factura")
    assert btn_generar is not None
    qtbot.mouseClick(btn_generar, Qt.LeftButton)
    QTest.qWait(2000)

    facturas = factura_controller.buscar_por_paciente("999888777")
    assert len(facturas) == 1
    id_factura = facturas[0]["id_factura"]
    print(f"   Factura generada: {id_factura}")

    facturacion.tabla_facturas.selectRow(0)
    QTest.qWait(500)
    facturacion.input_valor_pago.setText("30000")
    QTest.qWait(500)

    cerrar_msgbox_automatico(qtbot, delay=500)
    btn_pago = buscar_boton_por_texto(facturacion, "Registrar pago")
    assert btn_pago is not None
    qtbot.mouseClick(btn_pago, Qt.LeftButton)
    QTest.qWait(2000)

    saldo = pago_controller.calcular_saldo_pendiente(id_factura)
    assert saldo == 55000.0
    print("   Pago parcial OK (saldo 55000)")
    facturacion.close()
    QTest.qWait(500)

    print("\n[6] Reporte...")
    reportes = ReportesView(reporte_controller)
    qtbot.addWidget(reportes)
    reportes.show()
    QTest.qWait(1000)

    reportes.combo_tipo.setCurrentText("Pacientes registrados")
    QTest.qWait(500)
    btn_generar_reporte = buscar_boton_por_texto(reportes, "Generar reporte")
    assert btn_generar_reporte is not None
    qtbot.mouseClick(btn_generar_reporte, Qt.LeftButton)
    QTest.qWait(2000)

    # Verificar en la tabla del reporte (columna 1 = nombre)
    tabla = reportes.tabla
    encontrado = False
    for row in range(tabla.rowCount()):
        item = tabla.item(row, 1)  # columna Nombre
        if item and item.text() == "Robot E2E":
            encontrado = True
            break
        # También por documento (columna 0)
        item_doc = tabla.item(row, 0)
        if item_doc and item_doc.text() == "999888777":
            encontrado = True
            break
    assert encontrado, "Paciente no encontrado en la tabla del reporte"
    print("[6] Reporte OK")
    reportes.close()

    print("\n🤖 PRUEBA ROBOT COMPLETA: TODOS LOS PASOS EXITOSOS")