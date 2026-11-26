# Guía comentada de `conexion.ejemplo.json`

## ¿Por qué el archivo JSON no contiene comentarios?

El programa lee la configuración con `json.loads` de la biblioteca estándar de Python. **JSON estándar no admite comentarios** con `//`, `#` ni `/* ... */`: agregarlos impediría cargar la configuración. Por eso se conserva un ejemplo válido y se explica aquí, campo por campo.

El archivo `conexion.ejemplo.json` es únicamente una **plantilla de referencia**; no se carga automáticamente durante el inicio. La aplicación almacena los datos que el usuario introduce en la pantalla «Configurar PostgreSQL» en `%APPDATA%\GestionRequerimientosAdquisiciones\conexion.json` (Windows). Este último archivo se crea durante el primer guardado.

| Campo | Ejemplo | Explicación |
| --- | --- | --- |
| `host` | `localhost` | Nombre o IP del equipo donde escucha PostgreSQL. `localhost` significa el mismo equipo donde se abre la aplicación. |
| `port` | `5432` | Puerto TCP configurado para PostgreSQL. La aplicación comprueba que esté entre 1 y 65535. Puede variar según la instalación. |
| `dbname` | `gestion_adquisiciones` | Nombre **exacto** de la base que contiene las doce tablas, procedimientos y triggers del proyecto. No es lo mismo que el nombre del servidor registrado en pgAdmin. |
| `user` | `postgres` | Rol de PostgreSQL autorizado a conectarse y operar en la base. `postgres` es solo un ejemplo de usuario administrador; en uso real conviene un rol con permisos mínimos. |
| `password` | `""` | Contraseña asignada al rol en el servidor. Vacío significa que el ejemplo **no proporciona credenciales reales**; cada instalación requiere su propia contraseña. |

## Camino que sigue la conexión

1. `main.py` crea la ventana de Tkinter.
2. `frontend/ui.py` muestra «Configurar PostgreSQL» y reúne los cinco campos.
3. `config/settings.py:save_config` valida el puerto y guarda los valores en un JSON local del usuario.
4. Al pulsar «Comprobar conexión», `config/settings.py:load_config` obtiene los campos y `backend/database.py:Database.transaction` abre la conexión con `psycopg2.connect`.
5. `Database.verify` consulta los catálogos de PostgreSQL para comprobar las doce tablas y los procedimientos y triggers mínimos. Si falta alguno, informa del objeto ausente.
6. Si la validación termina correctamente, la interfaz permite abrir los módulos.

## Seguridad y recomendaciones

- No escribas contraseñas reales en el ejemplo que subes al repositorio o al ZIP.
- La versión actual guarda la contraseña local **sin cifrado**. Restringe el acceso al perfil del usuario de Windows y no compartas `%APPDATA%\GestionRequerimientosAdquisiciones\conexion.json`.
- El ejecutable no instala PostgreSQL ni crea automáticamente la base: el servidor y sus scripts deben estar preparados primero.
- pgAdmin 4 es una herramienta para administrar PostgreSQL; no reemplaza el servicio de base de datos.
- Esta documentación describe la configuración del proyecto, no una conexión verificada en otra computadora.
