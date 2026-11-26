# Cambio de denominación del aplicativo

**Nombre de entrega:** Aplicativo para Gestión de Requerimientos y Adquisiciones.

Se actualizó el título de la ventana, el panel lateral, la descripción de inicio, la exportación CSV, el nombre del proceso PostgreSQL y las referencias del código fuente y los datos SQL de prueba. La lógica de negocio, las doce tablas, los procedimientos y los diez reportes no se rediseñaron.

## Configuración de la base de datos

La base recomendada ahora se llama `gestion_adquisiciones`. Se puede crear una base nueva con ese nombre y ejecutar, en este orden:

1. `base_de_datos/01_creacion_base_datos.sql` — estructura.
2. `base_de_datos/02_insercion_datos_prueba.sql` — datos de demostración, opcional y únicamente sobre una base preparada para ello.
3. `base_de_datos/03_procedimientos_funciones_triggers.sql` — objetos de negocio.

**Si ya tienes datos en tu base actual:** no ejecutes nuevamente el script de creación o inserción sobre ella. Haz una copia de seguridad. Para conservar los datos y cambiar solo el nombre de la base, conéctate desde pgAdmin a la base de mantenimiento `postgres`, cierra las demás sesiones conectadas a tu base anterior y ejecuta sustituyendo el marcador por su nombre actual:

```sql
ALTER DATABASE "NOMBRE_ACTUAL" RENAME TO gestion_adquisiciones;
```

Después abre el ejecutable, pulsa «Configurar PostgreSQL» y guarda el nombre nuevo. Por el cambio de nombre de la aplicación, los ajustes de conexión se guardan ahora en `%APPDATA%\GestionRequerimientosAdquisiciones\conexion.json`; es necesario introducir la configuración una vez más.

## Ejecutable

`GestionRequerimientosAdquisiciones.exe` es un único archivo para Windows de 64 bits y conserva las dependencias empaquetadas del ejecutable recibido. Para conectarse sigue necesitando un servidor PostgreSQL configurado. No instala PostgreSQL ni pgAdmin 4 y no carga scripts automáticamente. El código incluye `scripts/compilar_windows_un_archivo.bat` para recompilar de forma convencional con PyInstaller en Windows.

Las pruebas automáticas y el arranque de la interfaz se verificaron con el código fuente. El ejecutable se verificó estructuralmente, pero no se ejecutó en Windows en este entorno. Antes de presentar la entrega se debe comprobar su inicio y conexión en una computadora Windows con PostgreSQL.
