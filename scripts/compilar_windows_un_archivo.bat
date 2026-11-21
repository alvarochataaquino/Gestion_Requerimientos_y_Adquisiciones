@echo off
REM Compila Supermix GDI para Windows en un solo ejecutable con PyInstaller.
REM Activa UTF-8 en la consola para mostrar mensajes correctamente.
chcp 65001 >nul
setlocal
REM Trabajar desde la raiz de 03_Codigo_Fuente sin depender de la ruta absoluta.
cd /d "%~dp0.."
echo ==========================================================
echo  SUPERMIX GDI - Compilacion de un solo ejecutable Windows
echo ==========================================================
REM Validar que el lanzador de Python de Windows este disponible.
REM La compilación necesita el lanzador py; no es requisito para abrir el EXE final.
where py >nul 2>nul
if errorlevel 1 (
  echo Instala Python 3.11 o 3.12 para Windows y agrega py al PATH.
  pause
  exit /b 1
)
REM Instalar el compilador y las dependencias declaradas en el proyecto.
py -m pip install --upgrade pip
if errorlevel 1 goto error
py -m pip install -r requirements_build.txt
if errorlevel 1 goto error
REM Construir el unico archivo EXE y agregar psycopg2 como dependencia.
REM onefile integra dependencias en un único EXE; windowed oculta la consola.
py -m PyInstaller --noconfirm --clean --onefile --windowed --name SupermixGDI --collect-all psycopg2 main.py
if errorlevel 1 goto error
if not exist "dist\SupermixGDI.exe" goto error
REM Copiar el producto compilado a la carpeta final de entrega.
if not exist "..\04_Ejecutable" mkdir "..\04_Ejecutable"
REM Sobrescribe únicamente la copia de 04_Ejecutable con el compilado nuevo.
copy /Y "dist\SupermixGDI.exe" "..\04_Ejecutable\SupermixGDI.exe" >nul
if errorlevel 1 goto error
echo.
echo EXITO: ..\04_Ejecutable\SupermixGDI.exe
echo El usuario final solo abre ese archivo. PostgreSQL es externo.
echo.
pause
exit /b 0
REM Control centralizado de fallos de instalacion o compilacion.
:error
echo Error de compilacion. Revisa los mensajes anteriores.
pause
exit /b 1
