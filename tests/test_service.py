# ============================================================================
# MÓDULO: PRUEBAS UNITARIAS SIN CONEXIÓN EXTERNA
#   Usa FakeDB y FakeCursor para inspeccionar SQL sin modificar datos reales.
#   Ejecutar desde la raíz 03_Codigo_Fuente: python -m unittest discover -s tests -v.
#   No reemplaza una prueba integral con PostgreSQL ni una prueba del EXE en Windows.
# ============================================================================

"""Pruebas unitarias sin servidor: validan entradas y llamadas SQL del servicio."""

import unittest
from contextlib import contextmanager
from decimal import Decimal
from gestion_app.backend.service import Service,validate_code,valid_date,positive_integer,money,CRITERIA
from gestion_app.backend.database import EXPECTED_TABLES,REQUIRED_PROCEDURES,REQUIRED_TRIGGERS
from gestion_app.backend.reports import REPORTS

# -----------------------------------------------------------------
# CLASE: FakeCursor
# Objetivo: Representa un cursor SQL que acumula comandos en vez de enviarlos a PostgreSQL.
# Entradas: Instancia de unittest y entradas del método.
# Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
# -----------------------------------------------------------------
class FakeCursor:
    """Simula un cursor SQL y registra las llamadas realizadas."""
    # -----------------------------------------------------------------
    # FUNCIÓN: FakeCursor.__init__
    # Objetivo: Conserva la bitácora compartida con la base ficticia.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    def __init__(self,log):
        """Inicializa la bitacora de sentencias del cursor simulado."""
        self.log=log
    # -----------------------------------------------------------------
    # FUNCIÓN: FakeCursor.execute
    # Objetivo: Almacena cada par SQL/argumentos que permitirán verificar las llamadas.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    def execute(self,sql,args=()):
        """Almacena la instruccion SQL y sus parametros sin acceder a PostgreSQL."""
        # Registra tanto el texto SQL como sus argumentos para verificar parametrización.
        self.log.append((sql,args))

# -----------------------------------------------------------------
# CLASE: FakeDB
# Objetivo: Sustituye el adaptador real para verificar los CALL y transacciones.
# Entradas: Instancia de unittest y entradas del método.
# Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
# -----------------------------------------------------------------
class FakeDB:
    """Sustituye la conexion real por una base de datos en memoria para pruebas de logica."""
    # -----------------------------------------------------------------
    # FUNCIÓN: FakeDB.__init__
    # Objetivo: Crea una bitácora en blanco antes de cada grupo de operaciones.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    def __init__(self):
        """Inicializa el registro de operaciones simuladas."""
        self.log=[]
    # -----------------------------------------------------------------
    # FUNCIÓN: FakeDB.execute
    # Objetivo: No consulta nada externo; registra instrucciones de escritura simuladas.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    def execute(self,sql,args=()):
        """Simula la ejecucion de una sentencia SQL."""
        self.log.append((sql,args))
    # -----------------------------------------------------------------
    # FUNCIÓN: FakeDB.query
    # Objetivo: Entrega lista vacía para consultas que no requieren registros reales.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    def query(self,sql,args=()):
        """Devuelve un conjunto vacio para consultas simuladas."""
        return []
    # -----------------------------------------------------------------
    # FUNCIÓN: FakeDB.transaction
    # Objetivo: Cede un cursor ficticio desde un administrador de contexto.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    @contextmanager
    def transaction(self):
        """Entrega un cursor simulado dentro de una transaccion falsa."""
        yield FakeCursor(self.log)

# -----------------------------------------------------------------
# CLASE: TestService
# Objetivo: Agrupa pruebas aisladas de validación y operaciones del módulo Service.
# Entradas: Instancia de unittest y entradas del método.
# Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
# -----------------------------------------------------------------
class TestService(unittest.TestCase):
    """Agrupa pruebas de validadores y operaciones de negocio sin servidor PostgreSQL."""
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.setUp
    # Objetivo: Construye FakeDB y Service nuevos para evitar contaminación entre casos.
    # Entradas: Instancia de unittest y entradas del método.
    # Salida/reglas: Permite observar lógica sin iniciar PostgreSQL ni ejecutar SQL real.
    # -----------------------------------------------------------------
    def setUp(self):
        """Crea una base simulada y el servicio bajo prueba para cada caso."""
        # Cada test comienza con una bitácora limpia y un Service nuevo.
        self.db=FakeDB();self.s=Service(self.db)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_lengths
    # Objetivo: Prueba: Verifica codigos numericos, longitud obligatoria y rechazo de letras.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_lengths(self):
        """Verifica codigos numericos, longitud obligatoria y rechazo de letras."""
        self.assertEqual(validate_code('001',length=3),'001')
        with self.assertRaises(ValueError):validate_code('1',length=3)
        with self.assertRaises(ValueError):validate_code('AA1',length=3)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_dates
    # Objetivo: Prueba: Verifica formato ISO de fechas y rechazo de formatos distintos.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_dates(self):
        """Verifica formato ISO de fechas y rechazo de formatos distintos."""
        self.assertEqual(valid_date('2026-11-19').year,2026)
        with self.assertRaises(ValueError):valid_date('19/11/2026')
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_quantities
    # Objetivo: Prueba: Comprueba que solo se acepten cantidades enteras positivas.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_quantities(self):
        """Comprueba que solo se acepten cantidades enteras positivas."""
        self.assertEqual(positive_integer('10'),10)
        for x in ('0','1.5','-1','foo'):
            with self.assertRaises(ValueError):positive_integer(x)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_money
    # Objetivo: Prueba: Valida importes decimales, numeros negativos y montos cero permitidos.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_money(self):
        """Valida importes decimales, numeros negativos y montos cero permitidos."""
        self.assertEqual(money('12.50'),Decimal('12.50'))
        with self.assertRaises(ValueError):money('-1')
        self.assertEqual(money('0',False),Decimal('0.00'))
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_catalog_call
    # Objetivo: Prueba: Verifica la llamada al procedimiento de alta de proveedores.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_catalog_call(self):
        """Verifica la llamada al procedimiento de alta de proveedores."""
        self.s.save_catalog('Proveedores',{'ruc':'20123456789','razon_social':'Prueba SAC',
            'direccion':'','ciudad':'Arequipa','telefono':'','correo':''})
        self.assertTrue(self.db.log[0][0].startswith('CALL sp_registrar_proveedor'))
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_req_call
    # Objetivo: Prueba: Verifica el procedimiento usado al crear un requerimiento.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_req_call(self):
        """Verifica el procedimiento usado al crear un requerimiento."""
        self.s.new_requirement('000001','2026-11-19','001','002','')
        self.assertTrue(self.db.log[0][0].startswith('CALL sp_registrar_requerimiento'))
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_eval_six_in_one_transaction
    # Objetivo: Prueba: Verifica las seis notas y las siete operaciones de una evaluacion.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_eval_six_in_one_transaction(self):
        """Verifica las seis notas y las siete operaciones de una evaluacion."""
        score=self.s.save_evaluation('000001','2026-11-19','000001','20123456789',[2]*6)
        self.assertEqual(score,12)
        self.assertEqual(len(self.db.log),7)
        self.assertEqual(sum('sp_calificar_criterio' in x[0] for x in self.db.log),6)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_purchase_atomic_six_param_types
    # Objetivo: Prueba: Comprueba la creacion atomica de encabezado y detalle de compra.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_purchase_atomic_six_param_types(self):
        """Comprueba la creacion atomica de encabezado y detalle de compra."""
        d={'numero':'0001','fecha':'2026-11-19','requerimiento':'000001',
           'proveedor':'20123456789','genera':'001','aprueba':'002',
           'moneda':'Soles','pago':'Contado','descuento':'0',
           'lugar':'Almacén','justificacion':''}
        self.s.new_order('Compra',d,[{'codigo':'001','cantidad':3,'precio':'12.50'}])
        self.assertEqual(len(self.db.log),2)
        self.assertIn('sp_generar_orden_compra',self.db.log[0][0])
        self.assertIn('sp_agregar_detalle_compra',self.db.log[1][0])
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_order_no_empty_lines
    # Objetivo: Prueba: Impide registrar ordenes sin productos o servicios.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_order_no_empty_lines(self):
        """Impide registrar ordenes sin productos o servicios."""
        with self.assertRaises(ValueError):self.s.new_order('Compra',{'numero':'1','fecha':'2026-11-19','requerimiento':'1','proveedor':'20123456789','genera':'001','aprueba':'002'},[])
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_report_count
    # Objetivo: Prueba: Verifica que el aplicativo disponga de diez reportes.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_report_count(self):
        """Verifica que el aplicativo disponga de diez reportes."""
        self.assertEqual(len(REPORTS),10)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_schema_count
    # Objetivo: Prueba: Verifica las doce tablas obligatorias del modelo fisico.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_schema_count(self):
        """Verifica las doce tablas obligatorias del modelo fisico."""
        self.assertEqual(len(EXPECTED_TABLES),12)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_procedures_count
    # Objetivo: Prueba: Verifica los doce procedimientos usados directamente por Python.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_procedures_count(self):
        """Verifica los doce procedimientos usados directamente por Python."""
        self.assertEqual(len(REQUIRED_PROCEDURES),12)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_criteria
    # Objetivo: Prueba: Verifica que existan seis criterios de evaluacion.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_criteria(self):
        """Verifica que existan seis criterios de evaluacion."""
        self.assertEqual(len(CRITERIA),6)
    # -----------------------------------------------------------------
    # FUNCIÓN: TestService.test_trigger_count
    # Objetivo: Prueba: Verifica los cinco triggers obligatorios.
    # Entradas: Ejecuta datos válidos/inválidos y llamadas simuladas.
    # Salida/reglas: Los assert y assertRaises documentan el resultado esperado.
    # -----------------------------------------------------------------
    def test_trigger_count(self):
        """Verifica los cinco triggers obligatorios."""
        self.assertEqual(len(REQUIRED_TRIGGERS),5)

if __name__=='__main__':unittest.main()
