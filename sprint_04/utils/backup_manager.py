from __future__ import annotations

import shutil
from datetime import datetime

from .json_manager import JsonManager


class BackupManager:
    @staticmethod
    def crear_respaldo():
        data_dir = JsonManager.DATA_DIR
        destino = data_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        destino.mkdir(parents=True, exist_ok=True)

        total = 0
        for archivo_json in data_dir.glob("*.json"):
            shutil.copy2(archivo_json, destino / archivo_json.name)
            total += 1

        return {
            "destino": str(destino),
            "archivos": total,
        }

    @staticmethod
    def crear_respaldo_diario_si_no_existe():
        carpeta_respaldos = JsonManager.DATA_DIR / "backups"
        carpeta_respaldos.mkdir(parents=True, exist_ok=True)
        prefijo_hoy = datetime.now().strftime("%Y%m%d")

        existentes = sorted(
            ruta for ruta in carpeta_respaldos.iterdir() if ruta.is_dir() and ruta.name.startswith(prefijo_hoy)
        )
        if existentes:
            ultimo = existentes[-1]
            return {
                "creado": False,
                "destino": str(ultimo),
                "archivos": len(list(ultimo.glob("*.json"))),
            }

        respaldo = BackupManager.crear_respaldo()
        respaldo["creado"] = True
        return respaldo
