# Guía técnica del código fuente — Gestión de Requerimientos y Adquisiciones

## 1. Arquitectura del programa

Aplicación de escritorio desarrollada en Python con Tkinter y PostgreSQL. Tiene separación lógica entre presentación, servicio, persistencia y configuración. La interfaz no utiliza un servidor HTTP ni requiere conexión a internet cuando PostgreSQL funciona localmente.

```text
main.py → SupermixApp (frontend/ui.py)
             ↓ llamadas a métodos del servicio
          Service (backend/service.py)
             ↓ SQL parametrizado
          Database (backend/database.py) ← load_config (config/settings.py)
             ↓ psycopg2 / transacciones
          PostgreSQL (12 tablas + procedimientos + triggers)
```

### Guía de lectura, archivo por archivo

| Archivo | ¿Qué contiene? | ¿Dónde revisar los comentarios? |
| --- | --- | --- |
| `main.py` | Instancia Tk, configura tamaño mínimo, crea `SupermixApp` e inicia el bucle de eventos. | Inicio del archivo y bloque `if __name__ == '__main__'`. |
| `supermix_app/frontend/ui.py` | Ventana, barra lateral, indicadores, catálogos, formularios, solicitudes, evaluaciones, órdenes y exportación. | Comentarios que preceden **cada método y callback**, más notas sobre selección, botones, borradores y consultas. |
| `supermix_app/backend/service.py` | Validadores `validate_code`, `valid_date`, `positive_integer`, `money`; operaciones de catálogos, requerimientos, evaluaciones y órdenes. | Comentarios sobre cada función, reglas de negocio, parámetros y transacciones. |
| `supermix_app/backend/database.py` | Conexiones a PostgreSQL con `psycopg2`, `commit`, `rollback`, cursores y verificación de esquema. | `transaction`, `query`, `execute`, `verify` y listas de objetos mínimos. |
| `supermix_app/backend/reports.py` | Diccionario de los **10 SELECT** para el módulo Reportes. | Cabecera y encabezados `Informe 01` a `Informe 10`. |
| `supermix_app/config/settings.py` | Determina la ruta por usuario y lee/guarda parámetros de conexión. | `config_path`, `default_config`, `load_config`, `save_config`. |
| `tests/test_service.py` | Pruebas con objetos ficticios (`FakeDB`, `FakeCursor`) que no usan un servidor real. | Comentarios de cada caso de prueba. |
| `supermix_app/**/__init__.py` | Declaran paquetes y sus responsabilidades. | Cabecera de cada paquete. |
| `configuracion/conexion.ejemplo.json` | Ejemplo **válido** de los cinco parámetros, sin secretos reales. | Leer `configuracion/GUIA_CONEXION.md`, porque JSON no admite comentarios. |
| `SupermixGDI.spec` | Configuración de empaquetado PyInstaller. | Comentarios de las secciones `Analysis`, `PYZ` y `EXE`. |
| `scripts/*.bat` | Inicio Python para pruebas y creación opcional de un solo ejecutable Windows. | Comentarios `REM` a lo largo de cada script. |

## 2. Flujo detallado de una operación

1. El usuario selecciona un módulo en el menú de `frontend/ui.py`.
2. La UI abre un formulario con metadatos del catálogo o de la orden.
3. El botón **Guardar** invoca un método de `backend/service.py`.
4. `Service` valida códigos, fechas, cantidades, importes y campos obligatorios.
5. `Database` utiliza parámetros `%s`, abre una conexión transaccional y ejecuta el `CALL` o SQL correspondiente.
6. PostgreSQL verifica claves foráneas, reglas de integridad, funciones y triggers.
7. Si todo termina correctamente se realiza `COMMIT`; ante error se realiza `ROLLBACK` y la interfaz muestra el mensaje.

**Nota sobre el EXE:** se conserva `04_Ejecutable/SupermixGDI.exe` tal como se recibió. Los comentarios no se ven al ejecutar la aplicación y no exigen recompilación. Solo recompila para incorporar cambios funcionales posteriores.

## 3. Operaciones por módulo

- **Catálogos:** la constante `CATALOGS` define tabla, clave primaria, campos y validación de áreas, empleados, productos/servicios y proveedores. La base de datos impide eliminar registros referenciados.
- **Requerimientos:** una cabecera puede tener varias líneas de producto o servicio; la protección de detalles corresponde también a triggers.
- **Evaluaciones:** seis criterios entre 0 y 2. Al tener los seis, resultado ACEPTADO desde 7 puntos; las calificaciones se registran dentro de una transacción.
- **Órdenes:** el usuario prepara un borrador de líneas. Al guardar se registra encabezado y detalles dentro de la misma transacción, con validaciones de cantidad y proveedor.
- **Reportes:** diez consultas parametrizadas o fijas, resultados en Treeview y exportación CSV UTF-8 con BOM. Los importes consideran IGV del 18 % según el caso académico.

## 4. Base de datos y orden de ejecución

El ZIP proporcionado contiene **tres** scripts SQL:

1. `base_de_datos/01_creacion_base_datos.sql`: crea tablas, claves, restricciones e índices. Antes se debe crear **manualmente** una base nueva `supermix_gdi` en PostgreSQL.
2. `base_de_datos/02_insercion_datos_prueba.sql`: **opcional**, carga registros ficticios; ejecutar una sola vez, solo en una base vacía para pruebas.
3. `base_de_datos/03_procedimientos_funciones_triggers.sql`: 17 procedimientos, 3 funciones y 5 triggers, que complementan las validaciones de Python.

No existe un archivo `04_consultas_sql_referencia.sql` en **esta copia**: las diez consultas utilizadas por la aplicación están en `supermix_app/backend/reports.py`.

**Importante:** conectarse a la base `supermix_gdi` en el Query Tool, no a otra como `veterinaria` ni a la base predeterminada `postgres`. No repitas la carga de datos ficticios: contiene claves fijas. Antes de volver a ejecutar SQL sobre una base existente realiza respaldo.

## 5. Conexión a PostgreSQL

La configuración se mantiene fuera del código fuente en `%APPDATA%\SupermixGDI\conexion.json` (Windows). Se requiere host, puerto, base, rol y contraseña reales. El JSON de ejemplo se encuentra en `configuracion/conexion.ejemplo.json`; su guía campo a campo está en `configuracion/GUIA_CONEXION.md`. **La versión actual no cifra la contraseña guardada localmente.**

## 6. Ejecutar, probar y recompilar

En PowerShell, situándote en `03_Codigo_Fuente`:

```powershell
py -m pip install -r requirements.txt
py main.py
py -m unittest discover -s tests -v
```

También puedes usar `scripts/iniciar_desarrollo_windows.bat` para abrir el código fuente o `scripts/compilar_windows_un_archivo.bat` para producir un EXE en Windows. La carpeta `tests` y los BAT **no se necesitan para abrir el EXE ya compilado**, pero se incluyen para que se pueda revisar, verificar y reproducir el desarrollo.

Las pruebas automatizadas emplean un adaptador simulado. No sustituyen una prueba con PostgreSQL real ni la prueba del ejecutable en otra computadora. El EXE no instala PostgreSQL automáticamente.

## 7. Alcance de esta actualización

Se añadieron comentarios explicativos a **todos los módulos Python**, cada función o método, así como a rutas de conexión, validaciones y llamadas importantes. Se conservaron las sentencias ejecutables Python originales (verificación mediante comparación de AST) y el EXE compilado original. Los cambios en guías corrigen nombres de archivos que no existen en esta versión del ZIP.
