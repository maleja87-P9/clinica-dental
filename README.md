# 🦷 Sistema de Gestión Clínica Dental – Sonrisa Perfecta

Sistema integral para la administración de clínicas dentales, desarrollado en Python con interfaz gráfica moderna (PySide6). Permite gestionar pacientes, citas, historial clínico, facturación, pagos, usuarios con roles y permisos, reportes exportables y un sistema de pruebas automatizadas que validan todo el flujo de negocio.

##  Características principales

- **Autenticación segura**: Inicio de sesión con usuarios, contraseñas y opción de MFA simulado.
- **Gestión de pacientes**: Registro, búsqueda, actualización y eliminación (con backups automáticos).
- **Agenda de citas**: Agendamiento, validación de disponibilidad por odontólogo, modificación y cancelación.
- **Historial clínico**: Registro de diagnósticos, tratamientos y observaciones por paciente.
- **Facturación y pagos**: Generación de facturas, registro de pagos parciales, cálculo de saldo pendiente.
- **Reportes**: Exportación a CSV de reportes de pacientes, citas por rango, clínico por paciente y financiero.
- **Seguridad y auditoría**: Control de acceso basado en roles (administrador, recepcionista, odontólogo, gerente) y bitácora de acciones.
- **Respaldo automático**: Backups diarios y manuales de todos los datos JSON.

##  Pruebas automatizadas (QA)

El sistema incluye una **suite completa de pruebas** que garantizan su correcto funcionamiento:

| Tipo de prueba | Archivo | Descripción |
|----------------|---------|-------------|
| Unitarias | `test_pacientes_citas.py`, `test_facturacion_pagos.py` | Validan métodos individuales de controladores. |
| Integración | `test_flujo_clinico_financiero.py` | Verifican la interacción entre múltiples módulos. |
| Interfaz de usuario | `test_pacientes_view.py` | Simulan acciones reales (clics, escritura) en las vistas. |
| **End‑to‑end robot** | `test_e2e_completo_robot.py` | Recorre todo el flujo: login → paciente → cita → historial → factura + pago → reporte, todo automático. |

**Resultado:** todas las pruebas pasan exitosamente, con una ejecución completa en ~32 segundos.

##  Tecnologías utilizadas

- **Lenguaje**: Python 3.13
- **Interfaz gráfica**: PySide6 (Qt para Python)
- **Persistencia**: Archivos JSON con gestión de respaldos
- **Pruebas**: `pytest`, `pytest-qt`, `QTest`
- **Entorno**: Windows / Linux / macOS (probado en Windows 11)

##  Estructura del proyecto
sprint_04/
├── controladores/ # Lógica de negocio (auth, citas, pacientes, facturación, etc.)
├── modelos/ # Clases de datos (Paciente, Cita, Factura, Usuario...)
├── vistas/ # Ventanas PySide6 (login, pacientes, citas, etc.)
├── utils/ # Utilidades (JsonManager, backup, validaciones)
├── data/ # Archivos JSON y respaldos (se crean automáticamente)
├── tests/ # Suite de pruebas automatizadas
│ ├── conftest.py
│ └── test_e2e_completo_robot.py # Prueba robot
├── main.py # Punto de entrada del sistema
├── requirements.txt # Dependencias (opcional)
└── README.md # Este archivo

text

##  Instalación y ejecución

### Requisitos previos
- Python 3.13 o superior
- pip

### Pasos
1. Clona el repositorio:
   ```bash
   git clone https://github.com/maleja87-P9/clinica-dental.git
   cd clinica-dental/sprint_04
Instala las dependencias:

bash
pip install -r requirements.txt
Si no tienes requirements.txt, instala manualmente:

bash
pip install PySide6 pytest pytest-qt
Ejecuta la aplicación:

bash
python main.py
 Ejecutar las pruebas automatizadas
Todas las pruebas
bash
pytest tests/ -v
Prueba robot (end‑to‑end) con salida detallada
bash
pytest tests/test_e2e_completo_robot.py -v -s
Generar reporte de pruebas en HTML
bash
pytest tests/ --html=reporte_pruebas.html --self-contained-html
 Usuarios de prueba predefinidos
Usuario	Contraseña	Rol	MFA
admin	admin123	administrador	No
recepcion	recepcion123	recepcionista	No
doctor	doctor123	odontólogo	Sí
gerencia	gerencia123	gerente	Sí
Para el MFA simulado usar el código 123456.

Contribuciones
Este proyecto fue desarrollado como parte del Sprint 04 del curso de Ingeniería de Software. No se aceptan contribuciones externas, pero puedes usarlo como base para tus propios proyectos educativos.

Licencia
Este proyecto es de uso académico. No se otorgan permisos para uso comercial sin autorización expresa.

 Contacto
Repositorio: https://github.com/maleja87-P9/clinica-dental

Autoras: María Alejandra - Karol Moreno (maleja87-P9)

“Sonrisa Perfecta – Tecnología que cuida tu sonrisa y tu tiempo”

text

---

##  Instrucciones para agregarlo a tu repositorio

1. Ve a la raíz de tu proyecto local `sprint_04` (o a la carpeta `sprint` que contiene todo).
2. Crea (o edita) el archivo `README.md`.
3. Copia todo el contenido de arriba y pégalo.
4. Guarda el archivo.
5. Sube los cambios a GitHub:
   ```bash
   git add README.md
   git commit -m "Agrega README completo con descripción del proyecto y pruebas"
   git push origin main
