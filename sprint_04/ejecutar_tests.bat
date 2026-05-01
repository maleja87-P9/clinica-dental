@echo off
echo ======================================
echo  Ejecutando pruebas automatizadas...
echo ======================================
cd /d "%~dp0"
pytest tests/ -v --html=reporte_pruebas.html --self-contained-html
echo.
echo ======================================
echo  Pruebas finalizadas.
echo  Reporte generado: reporte_pruebas.html
echo ======================================
pause
