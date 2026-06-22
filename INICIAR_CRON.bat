@echo off
title Guardia Medica - Envio automatico WhatsApp (9hs)
cd /d "%~dp0"
call venv\Scripts\activate
echo.
echo  Iniciando envio automatico de encuestas...
echo  Este programa envia WhatsApp todos los dias a las 9:00 hs.
echo  NO cierres esta ventana.
echo.
python enviar_encuestas.py
pause
