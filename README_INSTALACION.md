# APLICATIVO PARA GESTIÓN DE REQUERIMIENTOS Y ADQUISICIONES — CÓDIGO FUENTE COMPLETO

Software académico de Gestión de Requerimientos y Adquisiciones para el caso la organización.

## Organización del código

```text
03_Codigo_Fuente/
├── main.py                         # Punto de entrada
├── requirements.txt                # Dependencias de ejecución
├── requirements_build.txt          # Dependencias de compilación
├── gestion_app/
│   ├── __init__.py
│   ├── frontend/
│   │   ├── __init__.py
│   │   └── ui.py                   # Pantallas, formularios, Tkinter
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── service.py              # Validaciones, reglas y controladores
│   │   ├── database.py             # Transacciones y conexión a PostgreSQL
│   │   └── reports.py              # Consultas para reportes
│   └── config/
│       ├── __init__.py
│       └── settings.py             # Lectura y guardado de configuración
├── configuracion/
│   ├── conexion.ejemplo.json       # Parámetros de ejemplo sin contraseña real
│   └── CREDENCIALES_PRUEBA.md      # Instrucciones para pruebas
├── base_de_datos/
│   ├── 01_creacion_base_datos.sql        # Creación de 12 tablas, restricciones, índices
│   ├── 02_insercion_datos_prueba.sql# Carga de prueba (solo BD nueva)
│   ├── 03_procedimientos_funciones_triggers.sql # 17 procedimientos, 3 funciones y 5 triggers
├── scripts/
│   ├── iniciar_desarrollo_windows.bat
│   └── compilar_windows_un_archivo.bat
└── tests/
    └── test_service.py            # Pruebas unitarias sin servidor PostgreSQL
```

**Equivalencia a la consigna:** al ser una aplicación de escritorio, el *frontend* es Tkinter; el *backend* incluye reglas de negocio y acceso a PostgreSQL. No necesita React, Express ni servidor HTTP. No se implementaron vistas SQL; sí los procedimientos, funciones y triggers usados por el proyecto.

## Requisitos

- Para desarrollo: Windows 10/11, Python 3.11 o 3.12, biblioteca `psycopg2-binary`.
- Para ejecución: PostgreSQL 14+ (local o remoto), esquema SQL cargado y credenciales válidas.
- Para reconstruir el `.exe` (opcional): Windows, Python y PyInstaller (instalado por el BAT con `requirements_build.txt`).
- pgAdmin 4 es opcional: sirve para gestionar PostgreSQL, no es el motor de base de datos.

## Base de datos: instalación en una BD VACÍA

1. En PostgreSQL crea la base de datos `gestion_adquisiciones`.
2. Abre una sesión SQL conectada **a esa base** (por ejemplo, Query Tool en pgAdmin 4).
3. Ejecuta `base_de_datos/01_creacion_base_datos.sql`.
4. Si quieres datos de ejemplo, **solo en una base de pruebas vacía**, ejecuta `base_de_datos/02_insercion_datos_prueba.sql` (no repetir).
5. Ejecuta `base_de_datos/03_procedimientos_funciones_triggers.sql`.
6. Utiliza únicamente `03_procedimientos_funciones_triggers.sql`: contiene juntos los procedimientos, funciones y triggers sin archivos duplicados.

El orden es importante por las claves foráneas y los triggers. En una base ya existente, realiza un respaldo antes de instalar o modificar SQL. Si el programa informa “BD incompleta”, confirma que existen las 12 tablas, los 12 procedimientos requeridos para la verificación y los 5 triggers en el esquema `public`. El script declara 17 procedimientos en total.

## Ejecutar desde código fuente

Abre PowerShell o CMD en la carpeta **03_Codigo_Fuente**:

```powershell
py -m pip install -r requirements.txt
py main.py
```

O haz doble clic en `scripts/iniciar_desarrollo_windows.bat`.

## Crear el EXE de un único archivo

En Windows haz doble clic en `scripts/compilar_windows_un_archivo.bat`. Este script ejecuta PyInstaller `--onefile --windowed` y copia el resultado a `../04_Ejecutable/GestionRequerimientosAdquisiciones.exe`. La carpeta 04 incluye el ejecutable `GestionRequerimientosAdquisiciones.exe` listo para abrirlo directamente. No es necesario volver a compilar para ejecutar la versión entregada. Si recompilas, comprueba que el nuevo EXE abra correctamente en Windows. El usuario final no necesita instalar Python, pero sí requiere PostgreSQL operativo y la BD configurada.

## Configurar la conexión

Al iniciar selecciona **Configurar PostgreSQL** e introduce host, puerto, base de datos, usuario y contraseña. Comprueba la conexión desde la misma pantalla. El sistema guarda localmente esos datos en `%APPDATA%\GestionRequerimientosAdquisiciones\conexion.json` en Windows, sin incorporarlos al código fuente ni al EXE. Es una configuración local; la contraseña no se cifra. Protege el perfil de Windows y utiliza un rol de BD de privilegios limitados.

El archivo `configuracion/conexion.ejemplo.json` muestra la estructura de configuración, **pero no contiene credenciales reales**. Consulta `configuracion/CREDENCIALES_PRUEBA.md`.

## Pruebas unitarias

Ejecuta en **03_Codigo_Fuente**:

```powershell
py -m unittest discover -s tests -v
```

Estas pruebas validan estructuras, datos de entrada y llamadas a servicios con una BD simulada; **no sustituyen** las pruebas de conexión real a PostgreSQL ni la comprobación del EXE en Windows.

## Alcance y precauciones

- No existe un módulo de login de usuarios del aplicativo: los datos de acceso son los del servidor PostgreSQL.
- Los datos SQL de prueba son ficticios; no incluyas usuarios/contraseñas reales en el ZIP.
- Los importes de los reportes siguen el criterio de IGV 18 % definido en el caso académico.
- No se han desarrollado vistas SQL: no es necesario inventarlas para la entrega.
- El código reorganizado mantiene la lógica y las consultas originales; las importaciones Python y rutas BAT se ajustaron a esta estructura.

## Abrir el ejecutable entregado (sin compilar)

En Windows abre `../04_Ejecutable/GestionRequerimientosAdquisiciones.exe`. No hay que usar un iniciador `.cmd` para abrirlo; basta el archivo `.exe`. El programa no instala PostgreSQL automáticamente; configura el servidor y carga los scripts siguiendo las instrucciones anteriores. No requiere internet si PostgreSQL está instalado localmente.

**Validación externa pendiente:** verificar el inicio del `.exe`, conexión real y operaciones CRUD en otra computadora Windows.


## Comentarios y documentacion tecnica del codigo

- Cada modulo Python indica su responsabilidad; cada clase, funcion y metodo cuenta con una cadena de documentacion (`docstring`).
- `backend/service.py` documenta validaciones y transacciones; `backend/database.py` explica conexion, rollback y verificacion del esquema.
- `frontend/ui.py` explica los controles, las pantallas y los procesos de formularios.
- Los SQL tienen comentarios antes de cada tabla, indice, procedimiento, funcion, trigger, conjunto de datos y consulta.
- `GUIA_CODIGO.md` muestra la arquitectura, el flujo de ejecucion y el orden de scripts.
- `conexion.ejemplo.json` se mantiene como **JSON valido sin comentarios internos**; los parametros se explican en la guia.

**Nota sobre el EXE incluido:** el ejecutable original se conserva sin modificaciones. Como fue compilado antes de renombrar los SQL, sus avisos internos pueden citar los nombres antiguos; usa los nombres de archivos nuevos que aparecen en esta guia. Para incorporar los textos nuevos al propio EXE, recompila en Windows mediante `scripts/compilar_windows_un_archivo.bat` y vuelve a probarlo.


Para entender cada campo de `conexion.ejemplo.json`, lee `configuracion/GUIA_CONEXION.md`. Las consultas SQL de informes están integradas en `gestion_app/backend/reports.py`.
