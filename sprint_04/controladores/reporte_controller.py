from __future__ import annotations

import csv
from datetime import datetime

from controladores.cita_controller import CitaController
from controladores.factura_controller import FacturaController
from controladores.historial_controller import HistorialController
from controladores.paciente_controller import PacienteController
from controladores.pago_controller import PagoController
from utils.json_manager import JsonManager


class ReporteController:
    def __init__(
        self,
        paciente_controller=None,
        cita_controller=None,
        historial_controller=None,
        factura_controller=None,
        pago_controller=None,
    ):
        self.paciente_controller = paciente_controller or PacienteController()
        self.cita_controller = cita_controller or CitaController(
            paciente_controller=self.paciente_controller
        )
        self.historial_controller = historial_controller or HistorialController(
            paciente_controller=self.paciente_controller
        )
        self.factura_controller = factura_controller or FacturaController(
            paciente_controller=self.paciente_controller
        )
        self.pago_controller = pago_controller or PagoController(
            factura_controller=self.factura_controller
        )

    def reporte_pacientes(self):
        pacientes = self.paciente_controller.listar_pacientes()
        return {
            "titulo": "Pacientes registrados",
            "columnas": ["Documento", "Nombre", "Telefono", "Correo", "Direccion"],
            "filas": [
                [
                    paciente.get("documento"),
                    paciente.get("nombre"),
                    paciente.get("telefono"),
                    paciente.get("correo"),
                    paciente.get("direccion"),
                ]
                for paciente in pacientes
            ],
            "resumen": f"Total de pacientes registrados: {len(pacientes)}",
        }

    def reporte_citas_por_rango(self, fecha_inicio, fecha_fin):
        citas = self.cita_controller.citas_por_rango(fecha_inicio, fecha_fin)
        return {
            "titulo": "Citas por rango de fechas",
            "columnas": ["ID", "Paciente", "Fecha", "Hora", "Motivo", "Odontologo", "Estado"],
            "filas": [
                [
                    cita.get("id_cita"),
                    cita.get("nombre_paciente") or cita.get("documento_paciente"),
                    cita.get("fecha"),
                    cita.get("hora"),
                    cita.get("motivo"),
                    cita.get("odontologo"),
                    cita.get("estado"),
                ]
                for cita in citas
            ],
            "resumen": f"Citas encontradas entre {fecha_inicio} y {fecha_fin}: {len(citas)}",
        }

    def reporte_clinico_por_paciente(self, documento):
        paciente = self.paciente_controller.buscar_por_documento(documento)
        historiales = self.historial_controller.consultar_por_paciente(documento)
        nombre = paciente.get("nombre") if paciente else documento
        return {
            "titulo": "Reporte clinico por paciente",
            "columnas": ["Fecha", "Odontologo", "Diagnostico", "Tratamiento", "Observaciones"],
            "filas": [
                [
                    registro.get("fecha"),
                    registro.get("odontologo"),
                    registro.get("diagnostico"),
                    registro.get("tratamiento"),
                    registro.get("observaciones"),
                ]
                for registro in historiales
            ],
            "resumen": f"Paciente: {nombre}. Registros clinicos encontrados: {len(historiales)}",
        }

    def reporte_financiero_por_rango(self, fecha_inicio, fecha_fin):
        facturas = [
            factura
            for factura in self.factura_controller.listar_facturas()
            if fecha_inicio <= factura.get("fecha", "") <= fecha_fin
        ]
        ingresos = 0.0
        filas = []
        for factura in facturas:
            pagado = self.pago_controller.calcular_total_pagado(factura.get("id_factura"))
            saldo = self.pago_controller.calcular_saldo_pendiente(factura.get("id_factura")) or 0.0
            ingresos += pagado
            filas.append(
                [
                    factura.get("id_factura"),
                    factura.get("documento_paciente"),
                    factura.get("fecha"),
                    factura.get("concepto"),
                    factura.get("valor_total"),
                    pagado,
                    saldo,
                    factura.get("estado_pago"),
                ]
            )

        return {
            "titulo": "Reporte financiero por rango de fechas",
            "columnas": [
                "Factura",
                "Documento",
                "Fecha",
                "Concepto",
                "Valor total",
                "Pagado",
                "Saldo",
                "Estado",
            ],
            "filas": filas,
            "resumen": (
                f"Facturas en rango: {len(facturas)} | Ingresos registrados: {ingresos:.2f}"
            ),
        }

    def exportar_reporte_csv(self, reporte, nombre_archivo=None):
        titulo_base = nombre_archivo or reporte.get("titulo", "reporte")
        slug = "".join(caracter.lower() if caracter.isalnum() else "_" for caracter in titulo_base)
        slug = "_".join(fragmento for fragmento in slug.split("_") if fragmento) or "reporte"
        carpeta = JsonManager.BASE_DIR / "data" / "exportes"
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta / f"{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([reporte.get("titulo", "Reporte")])
            writer.writerow([reporte.get("resumen", "")])
            writer.writerow([])
            writer.writerow(reporte.get("columnas", []))
            writer.writerows(reporte.get("filas", []))

        return str(ruta)
