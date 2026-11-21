@echo off
REM Inicio para desarrollo: instala dependencias y abre la interfaz Python.
REM Utiliza la carpeta base del codigo, independientemente del directorio actual.
cd /d "%~dp0.."
REM Asegura los paquetes indicados por requirements.txt.
REM Este archivo instala paquetes para iniciar el código fuente; no compila ni instala PostgreSQL.
py -m pip install -r requirements.txt
if errorlevel 1 (pause & exit /b 1)
REM Ejecuta el punto de entrada principal de la interfaz.
REM Ejecuta el punto de entrada de Tkinter. La aplicación leerá su configuración por usuario.
py main.py
