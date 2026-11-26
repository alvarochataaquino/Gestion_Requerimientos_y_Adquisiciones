# ============================================================================
# MÓDULO: CATÁLOGO DE REPORTES SQL
#   Las claves de REPORTS son los nombres mostrados en el selector de la interfaz.
#   Cada valor es un SELECT; no incluye órdenes INSERT/UPDATE/DELETE.
#   Se separa IGV (18 %) cuando corresponde, sin mezclar monedas.
# ============================================================================

"""Diez informes; los importes contienen IGV 18% y las monedas no se mezclan."""
# Cada clave es la opcion visible en la pantalla de Reportes; el valor es su SELECT.
# Las consultas de montos separan el IGV incluido (18 %): base = total / 1.18.
# Las monedas permanecen en grupos distintos; no se aplica conversion cambiaria.
REPORTS = {
# Informe 01: Requerimientos y sus responsables.
'01 · Requerimientos por área y empleado': '''
 SELECT r.num_requerimiento AS requerimiento,r.fecha_requerimiento AS fecha,
 a.nombre_area AS area,(e.nombre||' '||e.apellido) AS solicitante,
 COALESCE(r.observaciones,'') AS observaciones FROM requerimiento_compra r
 JOIN area a USING(numero_area) JOIN empleado e ON e.numero_empleado=r.numero_empleado_solicita
 ORDER BY r.fecha_requerimiento DESC''',
# Informe 02: Detalle de los productos o servicios solicitados.
'02 · Detalle de requerimientos': '''
 SELECT d.num_requerimiento AS requerimiento,ps.numero_producto_servicio AS codigo,
 ps.nombre_producto_servicio AS elemento,ps.tipo,d.cantidad,ps.unidad_medida AS unidad,
 COALESCE(d.especificaciones_tecnicas,'') AS especificaciones
 FROM requerimiento_producto_servicio d JOIN producto_servicio ps USING(numero_producto_servicio)
 ORDER BY d.num_requerimiento DESC,ps.nombre_producto_servicio''',
# Informe 03: Requerimientos todavia sin orden.
'03 · Requerimientos sin orden': '''
 SELECT r.num_requerimiento AS requerimiento,r.fecha_requerimiento AS fecha,
 a.nombre_area AS area FROM requerimiento_compra r JOIN area a USING(numero_area)
 WHERE NOT EXISTS(SELECT 1 FROM orden_compra c WHERE c.num_requerimiento=r.num_requerimiento)
 AND NOT EXISTS(SELECT 1 FROM orden_servicio s WHERE s.num_requerimiento=r.num_requerimiento)
 ORDER BY r.fecha_requerimiento DESC''',
# Informe 04: Evaluaciones y puntajes.
'04 · Resultados de evaluaciones': '''
 SELECT e.numero_evaluacion AS evaluacion,e.num_requerimiento AS requerimiento,
 p.razon_social AS proveedor,COUNT(c.criterio)::INTEGER AS criterios,
 COALESCE(SUM(c.calificacion),0)::INTEGER AS puntos,
 CASE WHEN COUNT(c.criterio)<6 THEN 'INCOMPLETA' WHEN SUM(c.calificacion)>=7 THEN 'ACEPTADO'
 ELSE 'RECHAZADO' END AS resultado FROM evaluacion_proveedor e JOIN proveedor p USING(ruc)
 LEFT JOIN evaluacion_criterio c USING(numero_evaluacion)
 GROUP BY e.numero_evaluacion,p.razon_social ORDER BY e.numero_evaluacion DESC''',
# Informe 05: Comparacion de proveedores calificados.
'05 · Comparación de proveedores': '''
 SELECT e.num_requerimiento AS requerimiento,p.razon_social AS proveedor,
 e.numero_evaluacion AS evaluacion, COUNT(c.criterio)::INTEGER AS criterios,
 COALESCE(SUM(c.calificacion),0)::INTEGER AS puntos,
 CASE WHEN COUNT(c.criterio)<6 THEN 'INCOMPLETA' WHEN SUM(c.calificacion)>=7 THEN 'ACEPTADO'
 ELSE 'RECHAZADO' END AS resultado FROM evaluacion_proveedor e JOIN proveedor p USING(ruc)
 LEFT JOIN evaluacion_criterio c USING(numero_evaluacion)
 GROUP BY e.numero_evaluacion,p.razon_social ORDER BY e.num_requerimiento,puntos DESC''',
# Informe 06: Importes de ordenes de compra e IGV.
'06 · Órdenes de compra e IGV': '''
 WITH m AS(SELECT oc.num_orden_compra,oc.fecha,oc.num_requerimiento,oc.moneda,oc.ruc,
 GREATEST(COALESCE(SUM(d.cantidad*d.precio_unitario),0)-COALESCE(oc.descuento,0),0) AS total
 FROM orden_compra oc LEFT JOIN orden_compra_producto_servicio d USING(num_orden_compra)
 GROUP BY oc.num_orden_compra)
 SELECT m.num_orden_compra AS orden,m.fecha,m.num_requerimiento AS requerimiento,
 p.razon_social AS proveedor,m.moneda,m.total AS total_con_igv,
 ROUND(m.total/1.18,2) AS valor_sin_igv,m.total-ROUND(m.total/1.18,2) AS igv
 FROM m JOIN proveedor p USING(ruc) ORDER BY m.fecha DESC''',
# Informe 07: Importes de ordenes de servicio e IGV.
'07 · Órdenes de servicio e IGV': '''
 WITH m AS(SELECT os.num_orden_servicio,os.fecha,os.num_requerimiento,os.lugar_servicio,os.ruc,
 COALESCE(SUM(d.cantidad*d.precio_unitario),0) AS total FROM orden_servicio os
 LEFT JOIN orden_servicio_producto_servicio d USING(num_orden_servicio)
 GROUP BY os.num_orden_servicio)
 SELECT m.num_orden_servicio AS orden,m.fecha,m.num_requerimiento AS requerimiento,
 p.razon_social AS proveedor,m.lugar_servicio AS lugar,m.total AS total_con_igv,
 ROUND(m.total/1.18,2) AS valor_sin_igv,m.total-ROUND(m.total/1.18,2) AS igv
 FROM m JOIN proveedor p USING(ruc) ORDER BY m.fecha DESC''',
# Informe 08: Resumen por periodo, tipo y moneda.
'08 · Resumen mensual y moneda': '''
 WITH m AS(
 SELECT DATE_TRUNC('month',oc.fecha)::DATE AS mes,'Compra'::TEXT AS tipo,oc.moneda::TEXT AS moneda,
 GREATEST(COALESCE(SUM(d.cantidad*d.precio_unitario),0)-COALESCE(oc.descuento,0),0) AS total
 FROM orden_compra oc LEFT JOIN orden_compra_producto_servicio d USING(num_orden_compra)
 GROUP BY oc.num_orden_compra UNION ALL
 SELECT DATE_TRUNC('month',os.fecha)::DATE,'Servicio'::TEXT,'No especificada'::TEXT,
 COALESCE(SUM(d.cantidad*d.precio_unitario),0) FROM orden_servicio os
 LEFT JOIN orden_servicio_producto_servicio d USING(num_orden_servicio)
 GROUP BY os.num_orden_servicio)
 SELECT TO_CHAR(mes,'YYYY-MM') AS periodo,tipo,moneda,COUNT(*)::INTEGER AS ordenes,
 SUM(ROUND(total/1.18,2)) AS valor_sin_igv,
 SUM(total-ROUND(total/1.18,2)) AS igv,SUM(total) AS total_con_igv
 FROM m GROUP BY mes,tipo,moneda ORDER BY mes DESC,tipo,moneda''',
# Informe 09: Elementos con mayor demanda.
'09 · Productos y servicios más solicitados': '''
 SELECT ps.numero_producto_servicio AS codigo,ps.nombre_producto_servicio AS elemento,
 ps.tipo,ps.unidad_medida AS unidad,COUNT(DISTINCT d.num_requerimiento)::INTEGER AS requerimientos,
 SUM(d.cantidad) AS cantidad_total FROM requerimiento_producto_servicio d
 JOIN producto_servicio ps USING(numero_producto_servicio) GROUP BY ps.numero_producto_servicio
 ORDER BY cantidad_total DESC''',
# Informe 10: Compras y servicios agrupados por proveedor.
'10 · Monto por proveedor y moneda': '''
 WITH m AS(
 SELECT oc.ruc,'Compra'::TEXT AS tipo,oc.moneda::TEXT AS moneda,oc.num_orden_compra AS orden,
 GREATEST(COALESCE(SUM(d.cantidad*d.precio_unitario),0)-COALESCE(oc.descuento,0),0) AS total
 FROM orden_compra oc LEFT JOIN orden_compra_producto_servicio d USING(num_orden_compra)
 GROUP BY oc.num_orden_compra UNION ALL
 SELECT os.ruc,'Servicio'::TEXT,'No especificada'::TEXT,os.num_orden_servicio,
 COALESCE(SUM(d.cantidad*d.precio_unitario),0) FROM orden_servicio os
 LEFT JOIN orden_servicio_producto_servicio d USING(num_orden_servicio)
 GROUP BY os.num_orden_servicio)
 SELECT p.razon_social AS proveedor,m.tipo,m.moneda,COUNT(*)::INTEGER AS ordenes,
 SUM(ROUND(m.total/1.18,2)) AS valor_sin_igv,
 SUM(m.total-ROUND(m.total/1.18,2)) AS igv,SUM(m.total) AS total_con_igv
 FROM m JOIN proveedor p USING(ruc) GROUP BY p.ruc,m.tipo,m.moneda
 ORDER BY proveedor,moneda'''
}
