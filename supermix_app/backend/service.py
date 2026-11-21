# ============================================================================
# MÓDULO: CAPA DE SERVICIO / REGLAS DEL NEGOCIO
#   No dibuja ventanas. Valida entradas y utiliza Database para llamadas parametrizadas.
#   Catálogos: áreas, empleados, productos/servicios y proveedores.
#   Proceso: requerimientos -> evaluación de proveedor -> órdenes -> reportes.
# ============================================================================

"""Controlador: reglas de validación y operaciones atómicas con procedimientos PostgreSQL."""
from datetime import date
from decimal import Decimal, InvalidOperation
import re

# Criterios establecidos para la evaluacion (cada nota: 0, 1 o 2).
CRITERIA = ('Certificaciones de calidad','Relacion calidad precio','Cotizacion',
            'Cumplimiento de plazos','Aspectos administrativos','Referencia comercial')

# Metadatos reutilizados por el backend y los formularios de catalogos.
CATALOGS = {
 'Áreas': ('area', 'numero_area', [('numero_area','Número de área','code3'),('nombre_area','Nombre del área','text')]),
 'Empleados': ('empleado','numero_empleado',[
     ('numero_empleado','Número de empleado','code3'),('nombre','Nombres','text'),
     ('apellido','Apellidos','text'),('cargo','Cargo','text'),('correo','Correo (opcional)','optional'),
     ('telefono','Teléfono (opcional)','phone'),('numero_area','Área','area')]),
 'Productos y servicios': ('producto_servicio','numero_producto_servicio',[
     ('numero_producto_servicio','Código','code3'),('nombre_producto_servicio','Nombre','text'),
     ('categoria','Categoría','text'),('tipo','Tipo','tipo'),('descripcion','Descripción','text'),
     ('unidad_medida','Unidad de medida','text')]),
 'Proveedores': ('proveedor','ruc',[
     ('ruc','RUC','ruc'),('razon_social','Razón social','text'),('direccion','Dirección (opcional)','optional'),
     ('ciudad','Ciudad','text'),('telefono','Teléfono (opcional)','phone'),('correo','Correo (opcional)','optional')])
}


# -----------------------------------------------------------------
# FUNCIÓN: validate_code
# Objetivo: Valida identificadores que el esquema guarda como texto de dígitos.
# Entradas: value; length exacto o maximum permitido.
# Salida/reglas: Retorna texto preservando ceros a la izquierda; lanza ValueError ante error.
# -----------------------------------------------------------------
def validate_code(value, length=None, maximum=None):
    """Valida que un identificador contenga solo digitos y respete su longitud."""
    value=str(value).strip()
    if not value.isdigit() or (length and len(value)!=length) or (maximum and len(value)>maximum):
        raise ValueError('El código debe contener solo dígitos y respetar su longitud')
    return value


# -----------------------------------------------------------------
# FUNCIÓN: valid_date
# Objetivo: Interpreta fechas ISO como objeto date de Python.
# Entradas: value: fecha AAAA-MM-DD.
# Salida/reglas: Retorna date para el adaptador PostgreSQL; informa formato inválido.
# -----------------------------------------------------------------
def valid_date(value):
    """Convierte una fecha ISO (AAAA-MM-DD) en date; informa si es incorrecta."""
    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, TypeError) as error:
        raise ValueError('La fecha debe tener formato AAAA-MM-DD') from error


# -----------------------------------------------------------------
# FUNCIÓN: positive_integer
# Objetivo: Impide cantidades fraccionarias, nulas o demasiado grandes.
# Entradas: value: texto o entero capturado en UI.
# Salida/reglas: Retorna int entre 1 y 999999 o lanza ValueError.
# -----------------------------------------------------------------
def positive_integer(value):
    """Valida cantidades enteras entre 1 y 999999."""
    try: number=int(str(value).strip())
    except ValueError as error: raise ValueError('La cantidad debe ser un entero') from error
    if not (1<=number<=999999): raise ValueError('La cantidad debe estar entre 1 y 999999')
    return number


# -----------------------------------------------------------------
# FUNCIÓN: money
# Objetivo: Normaliza montos de dinero sin usar coma flotante binaria.
# Entradas: value: monto; positive=False permite descuento cero.
# Salida/reglas: Retorna Decimal con dos decimales y rechaza cifras fuera de rango.
# -----------------------------------------------------------------
def money(value, positive=True):
    """Convierte un importe a Decimal con dos decimales y comprueba su rango."""
    try: amount=Decimal(str(value).strip()).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError) as error: raise ValueError('Importe decimal inválido') from error
    if not amount.is_finite() or amount < (Decimal('0.01') if positive else 0):
        raise ValueError('El importe debe ser positivo' if positive else 'El importe no puede ser negativo')
    if amount>=Decimal('100000000'): raise ValueError('Importe demasiado grande')
    return amount


# -----------------------------------------------------------------
# FUNCIÓN: empty_to_none
# Objetivo: Transforma campo opcional en SQL NULL cuando queda vacío.
# Entradas: value: entrada de formulario.
# Salida/reglas: Retorna texto recortado o None para psycopg2.
# -----------------------------------------------------------------
def empty_to_none(value):
    """Convierte cadenas vacias en NULL (None) para columnas opcionales."""
    return str(value).strip() or None

# -----------------------------------------------------------------
# CLASE: Service
# Objetivo: Concentra operaciones de negocio, independientemente de Tkinter.
# Entradas: Database: adaptador de PostgreSQL suministrado al construirlo.
# Salida/reglas: La interfaz no debe emitir SQL por su cuenta; Service aplica validaciones previas.
# -----------------------------------------------------------------
class Service:
    """Implementa las reglas de negocio y coordina las llamadas a PostgreSQL."""
    # -----------------------------------------------------------------
    # FUNCIÓN: Service.__init__
    # Objetivo: Recibe el objeto de conexión o su sustituto para pruebas.
    # Entradas: db: Database real o FakeDB del conjunto unittest.
    # Salida/reglas: Guarda la referencia; permite probar reglas sin un servidor.
    # -----------------------------------------------------------------
    def __init__(self, db):
        """Almacena el acceso a datos inyectado para facilitar pruebas."""
        self.db=db

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.lookup
    # Objetivo: Recupera opciones de selección válidas para combos.
    # Entradas: what: área, empleado, requerimiento, proveedor o producto.
    # Salida/reglas: Devuelve filas con columnas code y label ordenadas desde PostgreSQL.
    # -----------------------------------------------------------------
    def lookup(self, what):
        """Recupera opciones de seleccion (codigo y descripcion) para formularios."""
        queries={
          'area': "SELECT numero_area AS code, nombre_area AS label FROM area ORDER BY numero_area",
          'empleado': "SELECT numero_empleado AS code,nombre||' '||apellido AS label FROM empleado ORDER BY numero_empleado",
          'requerimiento': "SELECT num_requerimiento AS code,fecha_requerimiento::TEXT AS label FROM requerimiento_compra ORDER BY num_requerimiento DESC",
          'proveedor': "SELECT ruc AS code,razon_social AS label FROM proveedor ORDER BY razon_social",
          'producto': "SELECT numero_producto_servicio AS code,nombre_producto_servicio||' ('||tipo||')' AS label FROM producto_servicio ORDER BY numero_producto_servicio"
        }
        return self.db.query(queries[what])

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.catalog
    # Objetivo: Consulta el catálogo cuyos nombres de columnas son conocidos.
    # Entradas: name: clave de CATALOGS, no texto SQL arbitrario.
    # Salida/reglas: Devuelve registros completos para el módulo de mantenimiento.
    # -----------------------------------------------------------------
    def catalog(self, name):
        """Consulta las columnas del catalogo seleccionado, usando nombres internos permitidos."""
        # Usar los metadatos limita los identificadores SQL a catálogos predefinidos.
        table,pk,fields=CATALOGS[name]
        cols=','.join(field for field,_,_ in fields)
        return self.db.query(f'SELECT {cols} FROM {table} ORDER BY {pk}')

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.save_catalog
    # Objetivo: Valida y crea/actualiza registros de cuatro catálogos.
    # Entradas: name, data y old_id: tipo, campos y clave si se edita.
    # Salida/reglas: Usa parámetros %s; impide editar clave primaria y valida RUC/correos/códigos.
    # -----------------------------------------------------------------
    def save_catalog(self,name,data,old_id=None):
        """Valida campos de catalogo y registra o actualiza datos mediante SQL parametrizado."""
        table,pk,fields=CATALOGS[name]
        values=[]
        # Cada campo posee una regla: código, RUC, correo, teléfono o texto obligatorio.
        for key,label,kind in fields:
            value=str(data.get(key,'')).strip()
            if key==pk and old_id and value!=str(old_id):
                raise ValueError('No puede modificarse la clave primaria')
            if kind=='code3': value=validate_code(value, length=3)
            elif kind=='ruc': value=validate_code(value,length=11)
            elif kind=='phone':
                if value: value=validate_code(value,length=9)
                else: value=None
            elif kind=='optional':
                value=empty_to_none(value)
                if key=='correo' and value and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',value):
                    raise ValueError('Correo electrónico inválido')
            elif kind=='tipo':
                if value not in ('Producto','Servicio'): raise ValueError('Tipo no válido')
            elif kind=='area': value=validate_code(value,length=3)
            elif not value: raise ValueError(f'{label} es obligatorio')
            values.append(value)
        # Proveedores y productos usan procedimientos almacenados; los demas catalogos, SQL parametrizado.
        # Proveedores requieren procedimientos que concentran sus validaciones en PostgreSQL.
        if name=='Proveedores':
            proc='sp_actualizar_proveedor' if old_id else 'sp_registrar_proveedor'
            self.db.execute(f'CALL {proc}('+','.join(['%s']*6)+')',tuple(values));return
        if name=='Productos y servicios' and not old_id:
            self.db.execute('CALL sp_registrar_producto_servicio(%s,%s,%s,%s,%s,%s)',values);return
        # Si hay clave previa, se actualizan los campos editables sin tocar la PK.
        if old_id:
            cols=[f[0] for f in fields if f[0]!=pk]
            self.db.execute(f'UPDATE {table} SET '+','.join(f'{c}=%s' for c in cols)+f' WHERE {pk}=%s',values[1:]+[old_id])
        else:
            cols=[f[0] for f in fields]
            self.db.execute(f'INSERT INTO {table} ('+','.join(cols)+') VALUES ('+','.join('%s' for _ in cols)+')',values)

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.delete_catalog
    # Objetivo: Elimina una fila de catálogo identificada por su clave.
    # Entradas: name y code: catálogo permitido e identificador.
    # Salida/reglas: Las restricciones FK de PostgreSQL pueden rechazar eliminaciones vinculadas.
    # -----------------------------------------------------------------
    def delete_catalog(self,name,code):
        """Elimina el registro del catalogo indicado; las claves foraneas siguen siendo respetadas."""
        if name not in CATALOGS: raise ValueError('Catálogo desconocido')
        table,pk,_=CATALOGS[name]
        self.db.execute(f'DELETE FROM {table} WHERE {pk}=%s',(code,))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.requirements
    # Objetivo: Lista solicitudes con datos del área y solicitante.
    # Entradas: No requiere parámetros; aplica joins de catálogos.
    # Salida/reglas: Entrega filas ordenadas por fecha/código más recientes.
    # -----------------------------------------------------------------
    def requirements(self):
        """Lista requerimientos con el area y el empleado solicitante."""
        return self.db.query('''SELECT r.num_requerimiento AS numero,r.fecha_requerimiento AS fecha,
          a.nombre_area AS area,(e.nombre||' '||e.apellido) AS solicitante,
          COALESCE(r.observaciones,'') AS observaciones FROM requerimiento_compra r
          JOIN area a USING(numero_area) JOIN empleado e ON e.numero_empleado=r.numero_empleado_solicita
          ORDER BY r.fecha_requerimiento DESC,r.num_requerimiento DESC''')

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.requirement_lines
    # Objetivo: Extrae los detalles registrados para un requerimiento.
    # Entradas: code: número de solicitud; kind: Producto/Servicio opcional.
    # Salida/reglas: Devuelve cantidad y especificaciones; construye filtro usando parámetros.
    # -----------------------------------------------------------------
    def requirement_lines(self,code,kind=None):
        """Obtiene los detalles de un requerimiento y, si se indica, filtra Producto o Servicio."""
        sql='''SELECT d.numero_producto_servicio AS codigo,ps.nombre_producto_servicio AS nombre,
          ps.tipo,d.cantidad,ps.unidad_medida AS unidad,
          COALESCE(d.especificaciones_tecnicas,'') AS especificaciones
          FROM requerimiento_producto_servicio d JOIN producto_servicio ps USING(numero_producto_servicio)
          WHERE d.num_requerimiento=%s'''
        args=[code]
        # El filtro adicional se inserta como placeholder, nunca con texto de usuario en SQL.
        if kind:
            sql+=' AND ps.tipo=%s';args.append(kind)
        return self.db.query(sql+' ORDER BY ps.nombre_producto_servicio',args)

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.new_requirement
    # Objetivo: Crea la cabecera del requerimiento usando procedimiento almacenado.
    # Entradas: number, when, area, employee y observations.
    # Salida/reglas: Valida formato y longitud antes de llamar sp_registrar_requerimiento.
    # -----------------------------------------------------------------
    def new_requirement(self,number,when,area,employee,observations):
        """Registra un requerimiento, tras validar codigo, fecha, area y empleado."""
        self.db.execute('CALL sp_registrar_requerimiento(%s,%s,%s,%s,%s)',
            (validate_code(number,maximum=8),valid_date(when),empty_to_none(observations),
             validate_code(area,length=3),validate_code(employee,length=3)))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.add_requirement_line
    # Objetivo: Inserta o modifica el detalle de un requerimiento existente.
    # Entradas: req, product, qty, spec y update.
    # Salida/reglas: La BD controla que el requerimiento no esté cerrado por una orden.
    # -----------------------------------------------------------------
    def add_requirement_line(self,req,product,qty,spec='',update=False):
        """Agrega o actualiza una linea del requerimiento mediante el procedimiento apropiado."""
        self.db.execute('CALL '+('sp_actualizar_detalle_requerimiento' if update else 'sp_agregar_detalle_requerimiento')+
            '(%s,%s,%s,%s)',(req,product,positive_integer(qty),empty_to_none(spec)))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.delete_requirement_line
    # Objetivo: Quita un producto o servicio de la solicitud.
    # Entradas: req y product: clave compuesta del detalle.
    # Salida/reglas: Los triggers de integridad bloquean borrados sobre órdenes ya emitidas.
    # -----------------------------------------------------------------
    def delete_requirement_line(self,req,product):
        """Elimina una linea, salvo que las restricciones o triggers de la BD lo impidan."""
        self.db.execute('''DELETE FROM requerimiento_producto_servicio
            WHERE num_requerimiento=%s AND numero_producto_servicio=%s''',(req,product))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.evaluations
    # Objetivo: Calcula un resumen de evaluaciones y sus estados.
    # Entradas: Seis criterios con puntuación de cero a dos.
    # Salida/reglas: INCOMPLETA si faltan notas, ACEPTADO desde siete y RECHAZADO en otro caso.
    # -----------------------------------------------------------------
    def evaluations(self):
        """Lista evaluaciones y calcula el resultado a partir de los seis criterios."""
        return self.db.query('''SELECT ev.numero_evaluacion AS numero,ev.fecha_evaluacion AS fecha,
          ev.num_requerimiento AS requerimiento,p.razon_social AS proveedor,
          COUNT(ec.criterio)::INTEGER AS criterios,COALESCE(SUM(ec.calificacion),0)::INTEGER AS puntos,
          CASE WHEN COUNT(ec.criterio)<6 THEN 'INCOMPLETA'
          WHEN SUM(ec.calificacion)>=7 THEN 'ACEPTADO' ELSE 'RECHAZADO' END AS resultado
          FROM evaluacion_proveedor ev JOIN proveedor p USING(ruc)
          LEFT JOIN evaluacion_criterio ec USING(numero_evaluacion)
          GROUP BY ev.numero_evaluacion,p.razon_social
          ORDER BY ev.fecha_evaluacion DESC,ev.numero_evaluacion DESC''')

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.evaluation_lines
    # Objetivo: Consulta las notas individuales de una evaluación.
    # Entradas: code: identificador de evaluación.
    # Salida/reglas: Retorna pares criterio/calificación para rellenar formulario de edición.
    # -----------------------------------------------------------------
    def evaluation_lines(self,code):
        """Consulta los criterios y las calificaciones de una evaluacion."""
        return self.db.query('''SELECT criterio,calificacion FROM evaluacion_criterio
            WHERE numero_evaluacion=%s ORDER BY criterio''',(code,))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.save_evaluation
    # Objetivo: Registra o actualiza las seis notas de una evaluación.
    # Entradas: number, when, req, ruc, scores, edit.
    # Salida/reglas: Usa transacción única; impide editar proveedor con orden emitida.
    # -----------------------------------------------------------------
    def save_evaluation(self,number,when,req,ruc,scores,edit=False):
        """Guarda las seis notas en una transaccion; bloquea ediciones vinculadas a ordenes."""
        # Las seis calificaciones se normalizan antes de iniciar cambios en la base.
        scores=[int(x) for x in scores]
        if len(scores)!=6 or any(x<0 or x>2 for x in scores):
            raise ValueError('Debe calificar los seis criterios entre 0 y 2')
        if not edit:
            number=validate_code(number,maximum=6)
        else:
            # Una evaluación que ya respaldó una orden no puede cambiar sus resultados.
            linked=self.db.query('''SELECT 1 FROM evaluacion_proveedor e WHERE e.numero_evaluacion=%s
                AND (EXISTS(SELECT 1 FROM orden_compra c WHERE c.num_requerimiento=e.num_requerimiento AND c.ruc=e.ruc)
                OR EXISTS(SELECT 1 FROM orden_servicio s WHERE s.num_requerimiento=e.num_requerimiento AND s.ruc=e.ruc)) LIMIT 1''',(number,))
            if linked: raise ValueError('No se pueden modificar las calificaciones de un proveedor con órdenes emitidas')
        # Encabezado y seis notas se guardan en una unica transaccion.
        # La transacción hace que todas las operaciones se guarden juntas o ninguna.
        with self.db.transaction() as cur:
            if not edit:
                cur.execute('CALL sp_registrar_evaluacion(%s,%s,%s,%s)',
                    (number,valid_date(when),req,ruc))
            for criterion,score in zip(CRITERIA,scores):
                cur.execute('CALL sp_calificar_criterio(%s,%s,%s)',(number,criterion,score))
        return sum(scores)

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.orders
    # Objetivo: Calcula el listado de órdenes y sus importes brutos por tipo.
    # Entradas: kind: Compra o Servicio, selecciona tablas conocidas.
    # Salida/reglas: Retorna total con IGV; descuenta importe de compra sin mezclar monedas.
    # -----------------------------------------------------------------
    def orders(self,kind):
        """Consulta las ordenes por tipo y sus montos con IGV."""
        # La elección de tabla procede de dos valores fijos, no del texto de un formulario.
        table='orden_compra' if kind=='Compra' else 'orden_servicio'
        idcol='num_orden_compra' if kind=='Compra' else 'num_orden_servicio'
        detail='orden_compra_producto_servicio' if kind=='Compra' else 'orden_servicio_producto_servicio'
        extra='oc.moneda' if kind=='Compra' else 'oc.lugar_servicio AS lugar'
        disc='COALESCE(oc.descuento,0)' if kind=='Compra' else '0'
        return self.db.query(f'''SELECT oc.{idcol} AS numero,oc.fecha,
            oc.num_requerimiento AS requerimiento,p.razon_social AS proveedor,{extra},
            GREATEST(COALESCE(SUM(d.cantidad*d.precio_unitario),0)-{disc},0) AS total_con_igv
            FROM {table} oc JOIN proveedor p USING(ruc)
            LEFT JOIN {detail} d USING({idcol}) GROUP BY oc.{idcol},p.razon_social
            ORDER BY oc.fecha DESC,oc.{idcol} DESC''')

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.order_lines
    # Objetivo: Recupera ítems de una orden y multiplica cantidad por precio.
    # Entradas: kind y number: tipo/número de orden.
    # Salida/reglas: Devuelve cada línea con importe numérico a dos decimales.
    # -----------------------------------------------------------------
    def order_lines(self,kind,number):
        """Consulta los productos o servicios y los importes de una orden determinada."""
        table='orden_compra_producto_servicio' if kind=='Compra' else 'orden_servicio_producto_servicio'
        idcol='num_orden_compra' if kind=='Compra' else 'num_orden_servicio'
        return self.db.query(f'''SELECT d.numero_producto_servicio AS codigo,
            p.nombre_producto_servicio AS nombre,d.cantidad,p.unidad_medida AS unidad,
            d.precio_unitario,(d.cantidad*d.precio_unitario)::NUMERIC(14,2) AS importe
            FROM {table} d JOIN producto_servicio p USING(numero_producto_servicio)
            WHERE d.{idcol}=%s ORDER BY p.nombre_producto_servicio''',(number,))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.new_order
    # Objetivo: Registra encabezado y detalles de orden de manera atómica.
    # Entradas: kind, form y lines: tipo, formulario y líneas del borrador.
    # Salida/reglas: Valida duplicados, precios, fechas, responsables y proveedores; usa CALL SQL.
    # -----------------------------------------------------------------
    def new_order(self,kind,form,lines):
        """Valida el encabezado y los detalles; los registra juntos en una sola transaccion."""
        if kind not in ('Compra','Servicio'): raise ValueError('Tipo de orden inválido')
        number=validate_code(form['numero'],maximum=6)
        when=valid_date(form['fecha'])
        req=validate_code(form['requerimiento'],maximum=8)
        generate=validate_code(form['genera'],length=3)
        approve=validate_code(form['aprueba'],length=3)
        ruc=validate_code(form['proveedor'],length=11)
        # Una orden sin detalles no satisface las reglas del proceso de adquisición.
        if not lines: raise ValueError('Agrega al menos un detalle antes de registrar la orden')
        if len(lines)!=len({line['codigo'] for line in lines}):
            raise ValueError('No se permite repetir el mismo elemento en una orden')
        # Compra y Servicio poseen campos distintos; la lógica selecciona el CALL correspondiente.
        if kind=='Compra':
            if form['moneda'] not in ('Soles','Dolares'): raise ValueError('Moneda inválida')
            if not form['pago'].strip() or not form['lugar'].strip():
                raise ValueError('Condición de pago y punto de entrega son obligatorios')
            args=(number,when,form['moneda'],form['pago'],money(form['descuento'],False),
                  form['lugar'],empty_to_none(form.get('justificacion','')),generate,approve,req,ruc)
            proc='sp_generar_orden_compra';detail_proc='sp_agregar_detalle_compra'
        else:
            if not form['lugar'].strip(): raise ValueError('Indica el lugar del servicio')
            args=(number,when,form['lugar'],empty_to_none(form.get('pago','')),generate,approve,req,ruc)
            proc='sp_generar_orden_servicio';detail_proc='sp_agregar_detalle_servicio'
        # Se registra encabezado y líneas de forma atómica. El trigger también valida cantidades.
        with self.db.transaction() as cur:
            cur.execute('CALL '+proc+'('+','.join('%s' for _ in args)+')',args)
            for line in lines:
                cur.execute('CALL '+detail_proc+'(%s,%s,%s,%s)',(
                    number,validate_code(line['codigo'],length=3),
                    positive_integer(line['cantidad']),money(line['precio'])))

    # -----------------------------------------------------------------
    # FUNCIÓN: Service.summary
    # Objetivo: Calcula conteos globales para el dashboard.
    # Entradas: Tablas de requerimientos, proveedores, evaluaciones y órdenes.
    # Salida/reglas: Devuelve un diccionario con cinco métricas.
    # -----------------------------------------------------------------
    def summary(self):
        """Devuelve conteos para las tarjetas de resumen del panel principal."""
        sql='''SELECT
            (SELECT COUNT(*) FROM requerimiento_compra)::INTEGER AS requerimientos,
            (SELECT COUNT(*) FROM proveedor)::INTEGER AS proveedores,
            (SELECT COUNT(*) FROM evaluacion_proveedor)::INTEGER AS evaluaciones,
            (SELECT COUNT(*) FROM orden_compra)::INTEGER AS compras,
            (SELECT COUNT(*) FROM orden_servicio)::INTEGER AS servicios'''
        return self.db.query(sql)[0]
