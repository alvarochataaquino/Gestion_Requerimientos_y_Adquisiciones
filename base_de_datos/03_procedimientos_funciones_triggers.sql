-- ============================================================================
-- LECTURA DEL SCRIPT:
--   PROCEDURE: se llama desde Python con CALL y opera sobre las tablas.
--   FUNCTION RETURNS TRIGGER: se ejecuta por un evento de la base, no por CALL.
--   TRIGGER: asocia una funcion al INSERT/UPDATE/DELETE de una tabla.
--   RAISE EXCEPTION detiene operaciones no validas y revierte la transaccion.
-- APLICATIVO PARA GESTIÓN DE REQUERIMIENTOS Y ADQUISICIONES | 03 - PROCEDIMIENTOS, FUNCIONES Y TRIGGERS
-- Requiere: 01_creacion_base_datos.sql (y opcionalmente los datos de prueba).
-- Los procedimientos materializan operaciones del negocio; los triggers protegen
-- invariantes aun cuando las tablas sean modificadas fuera de la interfaz Python.
-- NOTA: las funciones con RETURN TRIGGER no se llaman manualmente desde el cliente.
-- ============================================================================
-- Ejecutar después de 01_creacion_base_datos.sql.
-- 17 procedimientos extraídos del documento; se restituyó el encabezado omitido en la tabla de origen.
-- Procedimiento sp_registrar_proveedor
-- Finalidad: Crea un proveedor; la tabla verifica RUC, correo y campos obligatorios.
CREATE OR REPLACE PROCEDURE sp_registrar_proveedor(
    IN p_ruc TEXT,
    IN p_razon_social TEXT,
    IN p_direccion TEXT,
    IN p_ciudad TEXT,
    IN p_telefono TEXT,
    IN p_correo TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO proveedor
        (ruc, razon_social, direccion, ciudad, telefono, correo)
    VALUES
        (p_ruc, p_razon_social, p_direccion,
         p_ciudad, p_telefono, p_correo);
END;
$$;

-- Procedimiento sp_actualizar_proveedor
-- Finalidad: Actualiza datos de proveedor y lanza error si el RUC no existe.
CREATE OR REPLACE PROCEDURE sp_actualizar_proveedor(
    IN p_ruc TEXT,
    IN p_razon_social TEXT,
    IN p_direccion TEXT,
    IN p_ciudad TEXT,
    IN p_telefono TEXT,
    IN p_correo TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE proveedor AS p
    SET razon_social = p_razon_social,
        direccion = p_direccion,
        ciudad = p_ciudad,
        telefono = p_telefono,
        correo = p_correo
    WHERE p.ruc = p_ruc;
 
    IF NOT FOUND THEN
        RAISE EXCEPTION 'No existe el proveedor con RUC %', p_ruc;
    END IF;
END;
$$;

-- Procedimiento sp_registrar_producto_servicio
-- Finalidad: Da de alta un producto o servicio en el catalogo comun.
CREATE OR REPLACE PROCEDURE sp_registrar_producto_servicio(
    IN p_numero TEXT,
    IN p_nombre TEXT,
    IN p_categoria TEXT,
    IN p_tipo TEXT,
    IN p_descripcion TEXT,
    IN p_unidad_medida TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO producto_servicio
        (numero_producto_servicio, nombre_producto_servicio,
         categoria, tipo, descripcion, unidad_medida)
    VALUES
        (p_numero, p_nombre, p_categoria,
         p_tipo, p_descripcion, p_unidad_medida);
END;
$$;

-- Procedimiento sp_registrar_requerimiento
-- Finalidad: Crea una solicitud; verifica que el empleado pertenezca al area.
CREATE OR REPLACE PROCEDURE sp_registrar_requerimiento(
    IN p_num_requerimiento TEXT,
    IN p_fecha DATE,
    IN p_observaciones TEXT,
    IN p_numero_area TEXT,
    IN p_empleado_solicita TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM empleado AS e
        WHERE e.numero_empleado = p_empleado_solicita
          AND e.numero_area = p_numero_area
    ) THEN
        RAISE EXCEPTION
            'El empleado % no pertenece al area %',
            p_empleado_solicita, p_numero_area;
    END IF;

    INSERT INTO requerimiento_compra
        (num_requerimiento, fecha_requerimiento,
         observaciones, numero_area, numero_empleado_solicita)
    VALUES
        (p_num_requerimiento, p_fecha,
         p_observaciones, p_numero_area, p_empleado_solicita);
END;
$$;

-- Procedimiento sp_agregar_detalle_requerimiento
-- Finalidad: Agrega una linea de solicitud y verifica producto y cantidad.
CREATE OR REPLACE PROCEDURE sp_agregar_detalle_requerimiento(
    IN p_num_requerimiento TEXT,
    IN p_producto_servicio TEXT,
    IN p_cantidad INTEGER,
    IN p_especificaciones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM orden_compra AS oc
        WHERE oc.num_requerimiento = p_num_requerimiento
    ) OR EXISTS (
        SELECT 1 FROM orden_servicio AS os
        WHERE os.num_requerimiento = p_num_requerimiento

    ) THEN
        RAISE EXCEPTION
            'El requerimiento % ya tiene una orden asociada',
            p_num_requerimiento;
    END IF;
    INSERT INTO requerimiento_producto_servicio
        (num_requerimiento, numero_producto_servicio,
         cantidad, especificaciones_tecnicas)
    VALUES
        (p_num_requerimiento, p_producto_servicio,
         p_cantidad, p_especificaciones);
END;
$$;

-- Procedimiento sp_actualizar_detalle_requerimiento
-- Finalidad: Actualiza cantidad y especificaciones de un detalle.
CREATE OR REPLACE PROCEDURE sp_actualizar_detalle_requerimiento(
    IN p_num_requerimiento TEXT,
    IN p_producto_servicio TEXT,
    IN p_cantidad INTEGER,
    IN p_especificaciones TEXT
)LANGUAGE plpgsql
AS $$

BEGIN
    IF EXISTS (
        SELECT 1 FROM orden_compra AS oc
        WHERE oc.num_requerimiento = p_num_requerimiento
    ) OR EXISTS (
        SELECT 1 FROM orden_servicio AS os
        WHERE os.num_requerimiento = p_num_requerimiento
    ) THEN
        RAISE EXCEPTION
            'No se puede modificar un requerimiento con orden';
    END IF;
    UPDATE requerimiento_producto_servicio AS d
    SET cantidad = p_cantidad,
        especificaciones_tecnicas = p_especificaciones
    WHERE d.num_requerimiento = p_num_requerimiento
      AND d.numero_producto_servicio = p_producto_servicio;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'No se encontro el detalle solicitado';
    END IF;
END;
$$;

-- Procedimiento sp_registrar_evaluacion
-- Finalidad: Registra una evaluacion vinculada a requerimiento y proveedor.
CREATE OR REPLACE PROCEDURE sp_registrar_evaluacion(
    IN p_numero_evaluacion TEXT,
    IN p_fecha DATE,
    IN p_num_requerimiento TEXT,
    IN p_ruc TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM requerimiento_producto_servicio AS d
        WHERE d.num_requerimiento = p_num_requerimiento
    ) THEN
        RAISE EXCEPTION
            'El requerimiento % no contiene productos o servicios',
            p_num_requerimiento;
    END IF;


    INSERT INTO evaluacion_proveedor
        (numero_evaluacion, fecha_evaluacion,
         num_requerimiento, ruc)
    VALUES
        (p_numero_evaluacion, p_fecha,
         p_num_requerimiento, p_ruc);
END;
$$;

-- Procedimiento sp_calificar_criterio
-- Finalidad: Registra o reemplaza la calificacion de un criterio mediante UPSERT.
CREATE OR REPLACE PROCEDURE sp_calificar_criterio(
    IN p_numero_evaluacion TEXT,
    IN p_criterio TEXT,
    IN p_calificacion INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO evaluacion_criterio
        (numero_evaluacion, criterio, calificacion)
    VALUES
        (p_numero_evaluacion, p_criterio, p_calificacion)
    ON CONFLICT (numero_evaluacion, criterio)
    DO UPDATE SET calificacion = EXCLUDED.calificacion;
END;
$$;

-- Procedimiento sp_resultado_evaluacion
-- Finalidad: Cuenta criterios, suma notas y clasifica INCOMPLETA/ACEPTADO/RECHAZADO (6 notas, umbral 7).
CREATE OR REPLACE PROCEDURE sp_resultado_evaluacion(
    IN p_numero_evaluacion TEXT,
    INOUT p_criterios INTEGER,
    INOUT p_puntos INTEGER,
    INOUT p_resultado TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    IF NOT EXISTS (
        SELECT 1 FROM evaluacion_proveedor AS ev
        WHERE ev.numero_evaluacion = p_numero_evaluacion
    ) THEN
        RAISE EXCEPTION 'La evaluacion % no existe',
            p_numero_evaluacion;
    END IF;
 
    SELECT COUNT(*)::INTEGER,
           COALESCE(SUM(ec.calificacion), 0)::INTEGER
    INTO p_criterios, p_puntos
    FROM evaluacion_criterio AS ec
    WHERE ec.numero_evaluacion = p_numero_evaluacion;
 
    -- Se requiere completar los seis criterios antes de clasificar el proveedor.
    p_resultado := CASE
        WHEN p_criterios < 6 THEN 'INCOMPLETA'
        WHEN p_puntos >= 7 THEN 'ACEPTADO'
        ELSE 'RECHAZADO'
    END;
END;
$$;

-- Procedimiento sp_generar_orden_compra
-- Finalidad: Genera una compra solo con productos solicitados y proveedor con evaluacion aceptada.
CREATE OR REPLACE PROCEDURE sp_generar_orden_compra(
    IN p_num_orden TEXT,
    IN p_fecha DATE,
    IN p_moneda TEXT,
    IN p_condicion_pago TEXT,
    IN p_descuento NUMERIC,
    IN p_punto_entrega TEXT,
    IN p_justificacion TEXT,
    IN p_empleado_genera TEXT,
    IN p_empleado_aprueba TEXT,
    IN p_num_requerimiento TEXT,
    IN p_ruc TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM requerimiento_producto_servicio AS d

        JOIN producto_servicio AS ps
          ON ps.numero_producto_servicio = d.numero_producto_servicio
        WHERE d.num_requerimiento = p_num_requerimiento
          AND ps.tipo = 'Producto'
    ) THEN
        RAISE EXCEPTION 'El requerimiento no contiene productos';
    END IF;
 
    IF NOT EXISTS (
        SELECT 1
        FROM evaluacion_proveedor AS ev
        JOIN evaluacion_criterio AS ec
          ON ev.numero_evaluacion = ec.numero_evaluacion
        WHERE ev.num_requerimiento = p_num_requerimiento
          AND ev.ruc = p_ruc
        GROUP BY ev.numero_evaluacion
        HAVING COUNT(*) = 6 AND SUM(ec.calificacion) >= 7
    ) THEN
        RAISE EXCEPTION
            'El proveedor no tiene evaluacion aceptada para la solicitud';
    END IF;

    INSERT INTO orden_compra
        (num_orden_compra, fecha, moneda, condicion_pago,
         descuento, punto_entrega, justificacion,
         numero_empleado_genera, numero_empleado_aprueba,
         num_requerimiento, ruc)
    VALUES
        (p_num_orden, p_fecha, p_moneda, p_condicion_pago,
         p_descuento, p_punto_entrega, p_justificacion,
         p_empleado_genera, p_empleado_aprueba,
         p_num_requerimiento, p_ruc);
END;
$$;

-- Procedimiento sp_agregar_detalle_compra
-- Finalidad: Vincula producto a compra y controla que la cantidad total no supere lo solicitado.
CREATE OR REPLACE PROCEDURE sp_agregar_detalle_compra(
    IN p_num_orden TEXT,
    IN p_producto_servicio TEXT,
    IN p_cantidad INTEGER,
    IN p_precio_unitario NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_requerimiento TEXT;
    v_cantidad_solicitada INTEGER;
    v_cantidad_ordenada BIGINT;
BEGIN
    SELECT oc.num_requerimiento
    INTO STRICT v_requerimiento
    FROM orden_compra AS oc
    WHERE oc.num_orden_compra = p_num_orden;
    SELECT d.cantidad INTO v_cantidad_solicitada
    FROM requerimiento_producto_servicio AS d
    JOIN producto_servicio AS ps
      ON ps.numero_producto_servicio = d.numero_producto_servicio
    WHERE d.num_requerimiento = v_requerimiento
      AND d.numero_producto_servicio = p_producto_servicio
      AND ps.tipo = 'Producto';
 

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El producto no pertenece al requerimiento de la orden';
    END IF;
    SELECT COALESCE(SUM(od.cantidad), 0)
    INTO v_cantidad_ordenada
    FROM orden_compra AS oc
    JOIN orden_compra_producto_servicio AS od
      ON oc.num_orden_compra = od.num_orden_compra
    WHERE oc.num_requerimiento = v_requerimiento
      AND od.numero_producto_servicio = p_producto_servicio;
    IF v_cantidad_ordenada + p_cantidad > v_cantidad_solicitada THEN
        RAISE EXCEPTION
            'Cantidad acumulada mayor a la solicitada (%)',
            v_cantidad_solicitada;
    END IF;

    INSERT INTO orden_compra_producto_servicio
        (num_orden_compra, numero_producto_servicio,
         cantidad, precio_unitario)
    VALUES
        (p_num_orden, p_producto_servicio,
         p_cantidad, p_precio_unitario);
END;
$$;

-- Procedimiento sp_generar_orden_servicio
-- Finalidad: Genera una orden de servicio con proveedor evaluado y servicios solicitados.
CREATE OR REPLACE PROCEDURE sp_generar_orden_servicio(
    IN p_num_orden TEXT,
    IN p_fecha DATE,
    IN p_lugar_servicio TEXT,
    IN p_condicion_pago TEXT,
    IN p_empleado_genera TEXT,
    IN p_empleado_aprueba TEXT,
    IN p_num_requerimiento TEXT, 


    IN p_ruc TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM requerimiento_producto_servicio AS d
        JOIN producto_servicio AS ps
          ON ps.numero_producto_servicio = d.numero_producto_servicio
        WHERE d.num_requerimiento = p_num_requerimiento
          AND ps.tipo = 'Servicio'
    ) THEN
        RAISE EXCEPTION 'El requerimiento no contiene servicios';
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM evaluacion_proveedor AS ev
        JOIN evaluacion_criterio AS ec
          ON ev.numero_evaluacion = ec.numero_evaluacion
        WHERE ev.num_requerimiento = p_num_requerimiento

          AND ev.ruc = p_ruc
       GROUP BY ev.numero_evaluacion
        HAVING COUNT(*) = 6 AND SUM(ec.calificacion) >= 7
    ) THEN
        RAISE EXCEPTION
            'El proveedor no tiene evaluacion aceptada para la solicitud';
    END IF;
    INSERT INTO orden_servicio
        (num_orden_servicio, fecha, lugar_servicio,
         condicion_pago, numero_empleado_genera,
         numero_empleado_aprueba, num_requerimiento, ruc)
    VALUES
        (p_num_orden, p_fecha, p_lugar_servicio,
         p_condicion_pago, p_empleado_genera,
         p_empleado_aprueba, p_num_requerimiento, p_ruc);
END;
$$;

-- Procedimiento sp_agregar_detalle_servicio
-- Finalidad: Agrega servicio a orden y controla cantidad maxima del requerimiento.
CREATE OR REPLACE PROCEDURE sp_agregar_detalle_servicio(
    IN p_num_orden TEXT,
    IN p_producto_servicio TEXT,
    IN p_cantidad INTEGER,
    IN p_precio_unitario NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_requerimiento TEXT;
    v_cantidad_solicitada INTEGER;
    v_cantidad_ordenada BIGINT;
BEGIN
    SELECT os.num_requerimiento
    INTO STRICT v_requerimiento
    FROM orden_servicio AS os
    WHERE os.num_orden_servicio = p_num_orden;
    SELECT d.cantidad INTO v_cantidad_solicitada
    FROM requerimiento_producto_servicio AS d

    JOIN producto_servicio AS ps
      ON ps.numero_producto_servicio = d.numero_producto_servicio
    WHERE d.num_requerimiento = v_requerimiento
      AND d.numero_producto_servicio = p_producto_servicio
      AND ps.tipo = 'Servicio';
    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El servicio no pertenece al requerimiento de la orden';
    END IF;
    SELECT COALESCE(SUM(od.cantidad), 0)
    INTO v_cantidad_ordenada
    FROM orden_servicio AS os
    JOIN orden_servicio_producto_servicio AS od
      ON os.num_orden_servicio = od.num_orden_servicio
    WHERE os.num_requerimiento = v_requerimiento
      AND od.numero_producto_servicio = p_producto_servicio;
 
    IF v_cantidad_ordenada + p_cantidad > v_cantidad_solicitada THEN
        RAISE EXCEPTION
            'Cantidad acumulada mayor a la solicitada (%)',
            v_cantidad_solicitada;

 END IF;    
INSERT INTO orden_servicio_producto_servicio
        (num_orden_servicio, numero_producto_servicio,
         cantidad, precio_unitario)
    VALUES
        (p_num_orden, p_producto_servicio,
         p_cantidad, p_precio_unitario);
END;
$$;

-- Procedimiento sp_montos_orden_compra
-- Finalidad: Calcula total de compra con descuento; separa base e IGV incluido (18 %).
CREATE OR REPLACE PROCEDURE sp_montos_orden_compra(
    IN p_num_orden TEXT,
    INOUT p_valor_sin_igv NUMERIC,
    INOUT p_igv NUMERIC,
    INOUT p_total NUMERIC
)
LANGUAGE plpgsql

AS $$
DECLARE
    v_importe_bruto NUMERIC;
    v_descuento NUMERIC;
BEGIN
    SELECT oc.descuento INTO v_descuento
    FROM orden_compra AS oc
    WHERE oc.num_orden_compra = p_num_orden;
 
    IF NOT FOUND THEN
        RAISE EXCEPTION 'La orden de compra % no existe', p_num_orden;
    END IF;
    SELECT COALESCE(SUM(d.cantidad * d.precio_unitario), 0)
    INTO v_importe_bruto
    FROM orden_compra_producto_servicio AS d
    WHERE d.num_orden_compra = p_num_orden;
    -- El descuento reduce el total con IGV antes de desagregar el impuesto.
    p_total := GREATEST(v_importe_bruto - COALESCE(v_descuento, 0), 0);
    -- Los precios ya incluyen IGV: se divide entre 1.18 para hallar la base.
    p_valor_sin_igv := ROUND(p_total / 1.18, 2);
    p_igv := p_total - p_valor_sin_igv;
END;
$$;

-- Procedimiento sp_montos_orden_servicio
-- Finalidad: Calcula total contratado y separa base imponible e IGV incluido (18 %).
CREATE OR REPLACE PROCEDURE sp_montos_orden_servicio(
    IN p_num_orden TEXT,
    INOUT p_valor_sin_igv NUMERIC,
    INOUT p_igv NUMERIC,
    INOUT p_total NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM orden_servicio AS os
        WHERE os.num_orden_servicio = p_num_orden
    ) THEN
        RAISE EXCEPTION 'La orden de servicio % no existe', p_num_orden;
    END IF;

SELECT COALESCE(SUM(d.cantidad * d.precio_unitario), 0)
    INTO p_total
    FROM orden_servicio_producto_servicio AS d
    WHERE d.num_orden_servicio = p_num_orden;
    p_valor_sin_igv := ROUND(p_total / 1.18, 2);
    p_igv := p_total - p_valor_sin_igv;
END;
$$;

-- Procedimiento sp_requerimientos_pendientes
-- Finalidad: Abre un cursor con requerimientos que aun no tienen orden de compra ni servicio.
CREATE OR REPLACE PROCEDURE sp_requerimientos_pendientes(
    INOUT p_cursor REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    OPEN p_cursor FOR
        SELECT r.num_requerimiento,

               r.fecha_requerimiento,
               a.nombre_area,
               e.nombre || ' ' || e.apellido AS solicitante,
               r.observaciones
        FROM requerimiento_compra AS r
        JOIN area AS a
          ON r.numero_area = a.numero_area
        JOIN empleado AS e
          ON r.numero_empleado_solicita = e.numero_empleado
        WHERE NOT EXISTS (
            SELECT 1 FROM orden_compra AS oc
            WHERE oc.num_requerimiento = r.num_requerimiento
        )
        AND NOT EXISTS (
            SELECT 1 FROM orden_servicio AS os
            WHERE os.num_requerimiento = r.num_requerimiento
        )
        ORDER BY r.fecha_requerimiento, r.num_requerimiento;
END;
$$;

-- Procedimiento sp_resumen_mensual_adquisiciones
-- Finalidad: Consolida adquisiciones por mes con montos e IGV.
CREATE OR REPLACE PROCEDURE sp_resumen_mensual_adquisiciones(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    INOUT p_cursor REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_fecha_fin < p_fecha_inicio THEN
        RAISE EXCEPTION 'La fecha final no puede ser anterior';
    END IF;
    OPEN p_cursor FOR
        WITH montos AS (
            SELECT DATE_TRUNC('month', oc.fecha)::DATE AS mes,
                   'Compra'::TEXT AS tipo_orden,
                   oc.moneda::TEXT AS moneda,
                   GREATEST(

                       COALESCE(SUM(d.cantidad * d.precio_unitario), 0)
                       - COALESCE(oc.descuento, 0), 0
                   ) AS total_con_igv
            FROM orden_compra AS oc
            LEFT JOIN orden_compra_producto_servicio AS d
              ON oc.num_orden_compra = d.num_orden_compra
            WHERE oc.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
            GROUP BY oc.num_orden_compra, oc.fecha,
                     oc.moneda, oc.descuento
            UNION ALL
            SELECT DATE_TRUNC('month', os.fecha)::DATE AS mes,
                   'Servicio'::TEXT AS tipo_orden,
                   'No registrada'::TEXT AS moneda,
                   COALESCE(SUM(d.cantidad * d.precio_unitario), 0)
            FROM orden_servicio AS os
            LEFT JOIN orden_servicio_producto_servicio AS d
              ON os.num_orden_servicio = d.num_orden_servicio
            WHERE os.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
            GROUP BY os.num_orden_servicio, os.fecha

        )
        SELECT TO_CHAR(mes, 'YYYY-MM') AS periodo,
               tipo_orden,
               moneda,
               COUNT(*) AS numero_ordenes,
               SUM(ROUND(total_con_igv / 1.18, 2)) AS valor_sin_igv,
               SUM(total_con_igv - ROUND(total_con_igv / 1.18, 2))
                   AS igv,
               SUM(total_con_igv) AS total_con_igv
        FROM montos
        GROUP BY mes, tipo_orden, moneda
        ORDER BY mes, tipo_orden, moneda;
END;
$$;

-- Triggers recuperados del documento; corregido el terminador $$;
-- Funcion trigger: fn_validar_proveedor_orden
-- Finalidad: Antes de una compra o servicio valida que el requerimiento tenga el tipo correcto y proveedor con 6 criterios y al menos 7 puntos.
CREATE OR REPLACE FUNCTION fn_validar_proveedor_orden()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_tipo TEXT;
BEGIN
    IF TG_TABLE_NAME = 'orden_compra' THEN
        v_tipo := 'Producto';
    ELSIF TG_TABLE_NAME = 'orden_servicio' THEN
        v_tipo := 'Servicio';
    ELSE
        RAISE EXCEPTION 'Funcion asignada a una tabla no prevista: %', TG_TABLE_NAME;

    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM requerimiento_producto_servicio AS d
        JOIN producto_servicio AS ps
          ON ps.numero_producto_servicio = d.numero_producto_servicio
        WHERE d.num_requerimiento = NEW.num_requerimiento
          AND ps.tipo = v_tipo
    ) THEN
        RAISE EXCEPTION
            'El requerimiento % no contiene elementos del tipo %',
            NEW.num_requerimiento, v_tipo;
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM evaluacion_proveedor AS ev
        JOIN evaluacion_criterio AS ec
          ON ec.numero_evaluacion = ev.numero_evaluacion
        WHERE ev.num_requerimiento = NEW.num_requerimiento
          AND ev.ruc = NEW.ruc
        GROUP BY ev.numero_evaluacion

        HAVING COUNT(*) = 6 AND SUM(ec.calificacion) >= 7
    ) THEN
        RAISE EXCEPTION
            'El proveedor % no tiene una evaluacion aceptada para el requerimiento %',
            NEW.ruc, NEW.num_requerimiento;
    END IF;
    RETURN NEW;
END;
$$;
-- Trigger trg_validar_proveedor_compra: Valida el proveedor antes de agregar o cambiar una orden de compra.
-- Se elimina si existe para permitir reejecutar solo este bloque de triggers.
DROP TRIGGER IF EXISTS trg_validar_proveedor_compra ON orden_compra;
CREATE TRIGGER trg_validar_proveedor_compra
BEFORE INSERT OR UPDATE OF num_requerimiento, ruc
ON orden_compra
FOR EACH ROW
EXECUTE FUNCTION fn_validar_proveedor_orden();
-- Trigger trg_validar_proveedor_servicio: Valida el proveedor antes de agregar o cambiar una orden de servicio.
-- Se elimina si existe para permitir reejecutar solo este bloque de triggers.
DROP TRIGGER IF EXISTS trg_validar_proveedor_servicio ON orden_servicio;
CREATE TRIGGER trg_validar_proveedor_servicio
BEFORE INSERT OR UPDATE OF num_requerimiento, ruc
ON orden_servicio
FOR EACH ROW
EXECUTE FUNCTION fn_validar_proveedor_orden();

-- Funcion trigger: fn_validar_cantidad_orden
-- Finalidad: Evita cantidades/precios no positivos y excesos acumulados en los detalles; bloquea la linea del requerimiento al comparar.
CREATE OR REPLACE FUNCTION fn_validar_cantidad_orden()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_requerimiento TEXT;
    v_tipo TEXT;
    v_cantidad_solicitada INTEGER;
    v_cantidad_ordenada BIGINT;
    v_orden_anterior TEXT;
    v_producto_anterior TEXT;
BEGIN
    IF NEW.cantidad IS NULL OR NEW.cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor que cero';
    END IF;
    IF NEW.precio_unitario IS NULL OR NEW.precio_unitario <= 0 THEN
        RAISE EXCEPTION 'El precio unitario debe ser mayor que cero';

    END IF;
    IF TG_TABLE_NAME = 'orden_compra_producto_servicio' THEN
        v_tipo := 'Producto';
        SELECT oc.num_requerimiento
          INTO v_requerimiento
          FROM orden_compra AS oc
         WHERE oc.num_orden_compra = NEW.num_orden_compra;

        IF TG_OP = 'UPDATE' THEN
            v_orden_anterior := OLD.num_orden_compra;
            v_producto_anterior := OLD.numero_producto_servicio;
        END IF;
    ELSIF TG_TABLE_NAME = 'orden_servicio_producto_servicio' THEN
        v_tipo := 'Servicio';
        SELECT os.num_requerimiento
          INTO v_requerimiento
          FROM orden_servicio AS os
         WHERE os.num_orden_servicio = NEW.num_orden_servicio;
        IF TG_OP = 'UPDATE' THEN
            v_orden_anterior := OLD.num_orden_servicio;


            v_producto_anterior := OLD.numero_producto_servicio;
        END IF;
    ELSE
        RAISE EXCEPTION 'Funcion asignada a una tabla no prevista: %', TG_TABLE_NAME;
    END IF;

    IF v_requerimiento IS NULL THEN
        RAISE EXCEPTION 'La orden indicada no existe';
    END IF;

    SELECT d.cantidad
      INTO v_cantidad_solicitada
      FROM requerimiento_producto_servicio AS d
      JOIN producto_servicio AS ps
        ON ps.numero_producto_servicio = d.numero_producto_servicio
     WHERE d.num_requerimiento = v_requerimiento
       AND d.numero_producto_servicio = NEW.numero_producto_servicio
       AND ps.tipo = v_tipo
     FOR UPDATE OF d;


    IF NOT FOUND THEN
        RAISE EXCEPTION
            'El elemento % no fue solicitado en el requerimiento % como %',
            NEW.numero_producto_servicio, v_requerimiento, v_tipo;
    END IF;
    IF v_tipo = 'Producto' THEN
        SELECT COALESCE(SUM(det.cantidad), 0)
          INTO v_cantidad_ordenada
          FROM orden_compra_producto_servicio AS det
          JOIN orden_compra AS oc
            ON oc.num_orden_compra = det.num_orden_compra
         WHERE oc.num_requerimiento = v_requerimiento
           AND det.numero_producto_servicio = NEW.numero_producto_servicio
           AND (
               v_orden_anterior IS NULL
               OR det.num_orden_compra IS DISTINCT FROM v_orden_anterior
               OR det.numero_producto_servicio IS DISTINCT FROM v_producto_anterior
           );
    ELSE
        SELECT COALESCE(SUM(det.cantidad), 0)

          INTO v_cantidad_ordenada
          FROM orden_servicio_producto_servicio AS det
          JOIN orden_servicio AS os
            ON os.num_orden_servicio = det.num_orden_servicio
         WHERE os.num_requerimiento = v_requerimiento
           AND det.numero_producto_servicio = NEW.numero_producto_servicio
           AND (
               v_orden_anterior IS NULL
               OR det.num_orden_servicio IS DISTINCT FROM v_orden_anterior
               OR det.numero_producto_servicio IS DISTINCT FROM v_producto_anterior
           );
    END IF;

    IF v_cantidad_ordenada + NEW.cantidad > v_cantidad_solicitada THEN
        RAISE EXCEPTION
            'Cantidad acumulada (%) supera la solicitada (%) para el elemento %',
            v_cantidad_ordenada + NEW.cantidad,
            v_cantidad_solicitada,
            NEW.numero_producto_servicio;
    END IF;

    RETURN NEW;
END;
$$;
-- Trigger trg_validar_cantidad_compra: Evita cantidades excesivas o precios invalidos en detalles de compra.
-- Se elimina si existe para permitir reejecutar solo este bloque de triggers.
DROP TRIGGER IF EXISTS trg_validar_cantidad_compra ON orden_compra_producto_servicio;
CREATE TRIGGER trg_validar_cantidad_compra
BEFORE INSERT OR UPDATE
ON orden_compra_producto_servicio
FOR EACH ROW
EXECUTE FUNCTION fn_validar_cantidad_orden();
-- Trigger trg_validar_cantidad_servicio: Evita cantidades excesivas o precios invalidos en detalles de servicio.
-- Se elimina si existe para permitir reejecutar solo este bloque de triggers.
DROP TRIGGER IF EXISTS trg_validar_cantidad_servicio ON orden_servicio_producto_servicio;
CREATE TRIGGER trg_validar_cantidad_servicio
BEFORE INSERT OR UPDATE
ON orden_servicio_producto_servicio
FOR EACH ROW
EXECUTE FUNCTION fn_validar_cantidad_orden();

-- Funcion trigger: fn_proteger_detalle_requerimiento
-- Finalidad: Impide insertar, editar o borrar detalles de un requerimiento que ya tenga una orden emitida.
CREATE OR REPLACE FUNCTION fn_proteger_detalle_requerimiento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_requerimiento_anterior TEXT;
    v_requerimiento_nuevo TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_requerimiento_nuevo := NEW.num_requerimiento;
    ELSIF TG_OP = 'DELETE' THEN
        v_requerimiento_anterior := OLD.num_requerimiento;
    ELSE
        v_requerimiento_anterior := OLD.num_requerimiento;
        v_requerimiento_nuevo := NEW.num_requerimiento;
    END IF;
    IF EXISTS (
        SELECT 1
        FROM orden_compra AS oc

        WHERE oc.num_requerimiento IN (
            v_requerimiento_anterior, v_requerimiento_nuevo
        )
    ) OR EXISTS (
        SELECT 1
        FROM orden_servicio AS os
        WHERE os.num_requerimiento IN (
            v_requerimiento_anterior, v_requerimiento_nuevo
        )
    ) THEN
        RAISE EXCEPTION
            'No se puede modificar el detalle: el requerimiento ya tiene una orden asociada';
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$;

-- Trigger trg_proteger_detalle_requerimiento: Bloquea cambios al detalle de una solicitud con orden existente.
-- Se elimina si existe para permitir reejecutar solo este bloque de triggers.
DROP TRIGGER IF EXISTS trg_proteger_detalle_requerimiento ON requerimiento_producto_servicio;
CREATE TRIGGER trg_proteger_detalle_requerimiento
BEFORE INSERT OR UPDATE OR DELETE
ON requerimiento_producto_servicio
FOR EACH ROW
EXECUTE FUNCTION fn_proteger_detalle_requerimiento();
