# ============================================================================
# MÓDULO: CAPA DE PERSISTENCIA / POSTGRESQL
#   Obtiene la configuración local y crea conexiones de corta duración con psycopg2.
#   Nunca se concatenan valores de formulario en SQL: se envían como parámetros.
#   Toda transacción exitosa confirma COMMIT; un error produce ROLLBACK y cierre.
# ============================================================================

"""Acceso parametrizado a PostgreSQL y validación explícita del esquema."""
from contextlib import contextmanager
from ..config.settings import load_config
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

# Contrato minimo del modelo fisico: presencia de las 12 tablas del proyecto.
EXPECTED_TABLES = (
    # El contrato de tablas se compara con information_schema durante verify().
    'area', 'empleado', 'requerimiento_compra', 'producto_servicio',
    'proveedor', 'evaluacion_proveedor', 'evaluacion_criterio',
    'orden_compra', 'orden_servicio', 'requerimiento_producto_servicio',
    'orden_compra_producto_servicio', 'orden_servicio_producto_servicio'
)
# Solo se enumeran los procedimientos que el aplicativo invoca directamente.
REQUIRED_PROCEDURES = (
    # Estos son los procedimientos mínimos invocados directamente por Service.
    'sp_registrar_proveedor', 'sp_actualizar_proveedor',
    'sp_registrar_producto_servicio', 'sp_registrar_requerimiento',
    'sp_agregar_detalle_requerimiento', 'sp_actualizar_detalle_requerimiento',
    'sp_registrar_evaluacion', 'sp_calificar_criterio',
    'sp_generar_orden_compra', 'sp_agregar_detalle_compra',
    'sp_generar_orden_servicio', 'sp_agregar_detalle_servicio'
)

# Triggers de integridad que complementan las validaciones del servicio.
REQUIRED_TRIGGERS = (
    # Triggers de integridad: evitan registros inconsistentes desde cualquier cliente SQL.
    'trg_validar_proveedor_compra', 'trg_validar_proveedor_servicio',
    'trg_validar_cantidad_compra', 'trg_validar_cantidad_servicio',
    'trg_proteger_detalle_requerimiento'
)

# -----------------------------------------------------------------
# CLASE: Database
# Objetivo: Abstrae PostgreSQL para no mezclar acceso SQL con interfaz.
# Entradas: Configuración opcional; por defecto se obtiene del perfil del usuario.
# Salida/reglas: Garantiza cursores como diccionarios y confirmación o reversión de operaciones.
# -----------------------------------------------------------------
class Database:
    """Centraliza conexiones, consultas parametrizadas y verificacion del esquema PostgreSQL."""
    # -----------------------------------------------------------------
    # FUNCIÓN: Database.__init__
    # Objetivo: Obtiene parámetros de conexión sin codificarlos en el fuente.
    # Entradas: config: dict con host, port, dbname, user y password; opcional.
    # Salida/reglas: Conserva configuración local para nuevas conexiones.
    # -----------------------------------------------------------------
    def __init__(self, config=None):
        """Recibe una configuracion o carga la configuracion local del usuario."""
        self.config = config or load_config()

    # -----------------------------------------------------------------
    # FUNCIÓN: Database.transaction
    # Objetivo: Gestiona la unidad de trabajo de PostgreSQL en un contextmanager.
    # Entradas: Se invoca con «with db.transaction() as cur».
    # Salida/reglas: Abre conexión; hace commit al éxito, rollback ante excepción, cierre siempre.
    # -----------------------------------------------------------------
    @contextmanager
    def transaction(self):
        """Abre una transaccion; confirma al terminar o revierte ante una excepcion. Cierra siempre la conexion."""
        if psycopg2 is None:
            raise RuntimeError('Falta psycopg2-binary. Instala las dependencias.')
        # Los campos se leen del dict de configuración; nunca se almacenan en este módulo.
        # connect_timeout limita el tiempo que tarda en fallar una conexión no disponible.
        conn = psycopg2.connect(host=self.config['host'], port=int(self.config['port']),
            dbname=self.config['dbname'], user=self.config['user'], password=self.config['password'],
            connect_timeout=5, application_name='GestionRequerimientosAdquisiciones')
        # El COMMIT se realiza solo si todo el bloque fue exitoso.
        try:
            # RealDictCursor permite acceder a columnas por nombre, p. ej. fila['ruc'].
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # FUNCIÓN: Database.query
    # Objetivo: Ejecuta SQL de consulta y conserva nombres de columnas.
    # Entradas: sql: sentencia parametrizada; args: valores por separado.
    # Salida/reglas: Devuelve lista de dict; también funciona si la sentencia no produce filas.
    # -----------------------------------------------------------------
    def query(self, sql, args=()):
        """Ejecuta una consulta parametrizada y entrega sus filas como diccionarios."""
        with self.transaction() as cur:
            cur.execute(sql, args)
            return [dict(row) for row in cur.fetchall()] if cur.description else []

    # -----------------------------------------------------------------
    # FUNCIÓN: Database.execute
    # Objetivo: Ejecuta sentencias de escritura o llamadas CALL parametrizadas.
    # Entradas: sql y args; los parámetros evitan concatenar datos del usuario en SQL.
    # Salida/reglas: Devuelve número de filas reportado por cursor; transacción se cierra sola.
    # -----------------------------------------------------------------
    def execute(self, sql, args=()):
        """Ejecuta una sentencia parametrizada y devuelve el numero de filas afectadas."""
        with self.transaction() as cur:
            cur.execute(sql, args)
            return cur.rowcount

    # -----------------------------------------------------------------
    # FUNCIÓN: Database.verify
    # Objetivo: Asegura que la BD configurada tenga los objetos mínimos del programa.
    # Entradas: Esquema public; busca tablas, procedimientos y triggers en catálogos del servidor.
    # Salida/reglas: Retorna True si están; en caso contrario detalla qué scripts faltan.
    # -----------------------------------------------------------------
    def verify(self):
        """Comprueba que existan las doce tablas, los procedimientos y los triggers esenciales; informa lo faltante."""
        # Busca tablas reales del esquema public; no basta con que exista una BD del mismo nombre.
        tables = {r['table_name'] for r in self.query('''SELECT table_name
             FROM information_schema.tables WHERE table_schema='public'
             AND table_type='BASE TABLE' ''')}
        # pg_proc con prokind=p representa procedimientos, no funciones comunes.
        procs = {r['proname'] for r in self.query('''SELECT p.proname FROM pg_proc p
             JOIN pg_namespace n ON p.pronamespace=n.oid
             WHERE n.nspname='public' AND p.prokind='p' ''')}
        # Se omiten los triggers internos generados por las propias claves foráneas.
        trigs = {r['tgname'] for r in self.query('''SELECT t.tgname FROM pg_trigger t
            JOIN pg_class c ON c.oid=t.tgrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND NOT t.tgisinternal''')}
        # Comparacion por conjuntos: se informan solo objetos obligatorios ausentes.
        missing_tables = sorted(set(EXPECTED_TABLES) - tables)
        missing_procs = sorted(set(REQUIRED_PROCEDURES) - procs)
        missing_trigs = sorted(set(REQUIRED_TRIGGERS) - trigs)
        if missing_tables or missing_procs or missing_trigs:
            pieces = []
            if missing_tables: pieces.append('Tablas: ' + ', '.join(missing_tables))
            if missing_procs: pieces.append('Procedimientos: ' + ', '.join(missing_procs))
            if missing_trigs: pieces.append('Triggers: ' + ', '.join(missing_trigs))
            raise RuntimeError('BD incompleta. Faltan ' + '; '.join(pieces) +
                '. Ejecuta 01_creacion_base_datos.sql y 03_procedimientos_funciones_triggers.sql, en ese orden, en la BD configurada.')
        return True
