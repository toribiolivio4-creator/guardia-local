@echo off
title Guardia Medica - Cargar Paciente
cd /d "%~dp0"
call venv\Scripts\activate
python cargar_paciente.py
pause
