@echo off
title Guardia Medica - Prueba de envio
cd /d "%~dp0"
call venv\Scripts\activate
echo.
echo  MODO PRUEBA: enviando mensajes ahora mismo...
echo.
python enviar_encuestas.py --ahora
pause
