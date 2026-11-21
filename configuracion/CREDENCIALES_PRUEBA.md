# Credenciales y conexión de prueba

Este software **no tiene cuentas internas de prueba** ni contraseñas embebidas.

Para probarlo, crea o utiliza una instalación local de PostgreSQL que controles y configura los campos desde **Configurar PostgreSQL**:

| Campo | Valor orientativo |
|---|---|
| Host | `localhost` (si PostgreSQL corre en tu equipo) |
| Puerto | `5432` (si no lo modificaste) |
| Base | `supermix_gdi` |
| Usuario | Usuario de PostgreSQL que hayas creado o autorizado |
| Contraseña | Contraseña asignada a ese usuario (no incluida en el ZIP) |

`conexion.ejemplo.json` es solo una plantilla sin clave; **no representa credenciales operativas**.

El paquete incluye registros SQL de prueba académicos en `base_de_datos/02_insercion_datos_prueba.sql`; cárgalos únicamente en una base nueva de pruebas.
