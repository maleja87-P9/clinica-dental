from __future__ import annotations

from modelos.paciente import Paciente
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


class PacienteController:
    def __init__(self, ruta_db="pacientes.json"):
        self.ruta_db = ruta_db

    def _normalizar_registros(self):
        registros = JsonManager.leer(self.ruta_db, [])
        normalizados = [Paciente.from_dict(item).to_dict() for item in registros]
        if registros != normalizados:
            JsonManager.guardar(self.ruta_db, normalizados)
        return normalizados

    def listar_pacientes(self):
        return self._normalizar_registros()

    def obtener_todos(self):
        return self.listar_pacientes()

    def buscar_por_documento(self, documento):
        for paciente in self.listar_pacientes():
            if paciente.get("documento") == str(documento).strip():
                return paciente
        return None

    def registrar_paciente(self, paciente_obj):
        paciente = paciente_obj if isinstance(paciente_obj, Paciente) else Paciente.from_dict(paciente_obj)
        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "documento": paciente.documento,
                "nombre": paciente.nombre,
                "teléfono": paciente.telefono,
            }
        )
        if not valido:
            return False, mensaje

        valido, mensaje = Validaciones.validar_email(paciente.correo)
        if not valido:
            return False, mensaje

        pacientes = self.listar_pacientes()
        valido, mensaje = Validaciones.validar_documento_unico(paciente.documento, pacientes)
        if not valido:
            return False, mensaje

        pacientes.append(paciente.to_dict())
        JsonManager.guardar(self.ruta_db, pacientes)
        return True, "Paciente registrado correctamente."

    def actualizar_paciente(self, documento, datos_actualizados):
        pacientes = self.listar_pacientes()
        documento = str(documento).strip()

        for indice, registro in enumerate(pacientes):
            if registro.get("documento") != documento:
                continue

            registro_actualizado = dict(registro)
            registro_actualizado.update(datos_actualizados)
            paciente = Paciente.from_dict(registro_actualizado)

            valido, mensaje = Validaciones.validar_campos_obligatorios(
                {
                    "documento": paciente.documento,
                    "nombre": paciente.nombre,
                    "teléfono": paciente.telefono,
                }
            )
            if not valido:
                return False, mensaje

            valido, mensaje = Validaciones.validar_email(paciente.correo)
            if not valido:
                return False, mensaje

            pacientes[indice] = paciente.to_dict()
            JsonManager.guardar(self.ruta_db, pacientes)
            return True, "Paciente actualizado correctamente."

        return False, "No se encontró el paciente solicitado."

    # ================== NUEVOS MÉTODOS ELIMINACIÓN ==================
    def eliminar_paciente_por_documento(self, documento):
        """Elimina un paciente específico por su documento."""
        documento = str(documento).strip()
        pacientes = self.listar_pacientes()

        for i, paciente in enumerate(pacientes):
            if paciente.get("documento") == documento:
                nombre = paciente.get("nombre", "Sin nombre")
                pacientes.pop(i)
                JsonManager.guardar(self.ruta_db, pacientes)
                return True, f"Paciente '{nombre}' (Doc: {documento}) eliminado correctamente."

        return False, f"No se encontró un paciente con documento {documento}."

    def eliminar_todos_los_pacientes(self):
        """Elimina TODOS los pacientes del sistema (con backup automático)."""
        pacientes = self.listar_pacientes()
        if not pacientes:
            return False, "No hay pacientes registrados para eliminar."

        from utils.backup_manager import BackupManager
        backup = BackupManager.crear_respaldo()
        cantidad = len(pacientes)

        JsonManager.guardar(self.ruta_db, [])

        return True, f"Se eliminaron {cantidad} pacientes. Backup guardado en: {backup['destino']}"
