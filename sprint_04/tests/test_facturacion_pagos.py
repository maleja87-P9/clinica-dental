import pytest
from modelos.factura import Factura
from modelos.pago import Pago
from modelos.paciente import Paciente

def test_generar_factura_y_pago(paciente_controller, factura_controller, pago_controller):
    # Registrar paciente
    paciente = Paciente("9999", "Pedro Test", "555-1234", "pedro@test.com")
    paciente_controller.registrar_paciente(paciente)

    # Generar factura
    factura = Factura("9999", "Consulta", 150000)
    ok, msg = factura_controller.generar_factura(factura)
    assert ok
    facturas = factura_controller.listar_facturas()
    id_factura = facturas[0]["id_factura"]

    # Registrar pago parcial
    pago = Pago(id_factura, 50000, "Efectivo", documento_paciente="9999")
    ok, msg = pago_controller.registrar_pago(pago)
    assert ok
    saldo = pago_controller.calcular_saldo_pendiente(id_factura)
    assert saldo == 100000.0

    # Segundo pago que completa
    pago2 = Pago(id_factura, 100000, "Tarjeta", documento_paciente="9999")
    ok, msg = pago_controller.registrar_pago(pago2)
    assert ok
    factura_actualizada = factura_controller.obtener_factura(id_factura)
    assert factura_actualizada["estado_pago"] == "Pagada"
