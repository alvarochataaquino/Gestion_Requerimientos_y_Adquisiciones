-- ============================================================================
-- LECTURA DEL SCRIPT:
--   INSERT INTO agrega valores ficticios para probar pantallas y relaciones.
--   Las claves son fijas: repetir el archivo puede provocar conflictos de PK.
--   Solo se usa para demostraciones; no contiene usuarios finales reales.
-- SUPERMIX GDI | 02 - INSERCION OPCIONAL DE DATOS DE PRUEBA
-- Requiere que 01_creacion_base_datos.sql haya sido ejecutado.
-- Registros ficticios de fines academicos; no representan datos reales.
-- Solo ejecutar UNA VEZ en una base vacia de prueba (hay claves primarias fijas).
-- Orden de carga: catalogos y cabeceras primero, detalles al final por las FK.
-- ============================================================================
-- 3. INSERCION DE REGISTROS DE PRUEBA
-- Se insertan 15 registros por tabla, excepto EVALUACION_CRITERIO (90 registros).
-- Cada evaluacion tiene sus 6 criterios. El orden respeta las claves foraneas.

-- Datos de la tabla AREA
-- Proposito: Registra las areas que seran referenciadas por los empleados y solicitudes.
INSERT INTO area (numero_area, nombre_area) VALUES
('001', 'Logistica'),
('002', 'Operaciones'),
('003', 'Mantenimiento'),
('004', 'Administracion'),
('005', 'Produccion'),
('006', 'Almacen Central'),
('007', 'Seguridad Industrial'),
('008', 'Control de Calidad'),
('009', 'Transporte'),
('010', 'Recursos Humanos'),
('011', 'Compras'),
('012', 'Distribucion'),
('013', 'Contabilidad'),
('014', 'Tecnologia'),
('015', 'Infraestructura');

-- Datos de la tabla EMPLEADO
-- Proposito: Crea empleados asociados a areas ya existentes.
INSERT INTO empleado
(numero_empleado, nombre, apellido, cargo, correo, telefono, numero_area)
VALUES
('001', 'Jorge', 'Paredes', 'Supervisor logistico', 'jorge.paredes@supermix-ejemplo.test', '900000001', '001'),
('002', 'Rosa', 'Huaman', 'Jefa de operaciones', 'rosa.huaman@supermix-ejemplo.test', '900000002', '002'),
('003', 'Victor', 'Mamani', 'Tecnico de mantenimiento', 'victor.mamani@supermix-ejemplo.test', '900000003', '003'),
('004', 'Carmen', 'Salazar', 'Jefa administrativa', 'carmen.salazar@supermix-ejemplo.test', '900000004', '004'),
('005', 'Luis', 'Quispe', 'Encargado de produccion', 'luis.quispe@supermix-ejemplo.test', '900000005', '005'),
('006', 'Elena', 'Torres', 'Responsable de almacen', 'elena.torres@supermix-ejemplo.test', '900000006', '006'),
('007', 'Raul', 'Flores', 'Supervisor de seguridad', 'raul.flores@supermix-ejemplo.test', '900000007', '007'),
('008', 'Ana', 'Condori', 'Analista de calidad', 'ana.condori@supermix-ejemplo.test', '900000008', '008'),
('009', 'Marco', 'Zeballos', 'Coordinador de transporte', 'marco.zeballos@supermix-ejemplo.test', '900000009', '009'),
('010', 'Patricia', 'Rivera', 'Analista de personal', 'patricia.rivera@supermix-ejemplo.test', '900000010', '010'),
('011', 'Diego', 'Nina', 'Analista de compras', 'diego.nina@supermix-ejemplo.test', '900000011', '011'),
('012', 'Sandra', 'Vilca', 'Coordinadora de distribucion', 'sandra.vilca@supermix-ejemplo.test', '900000012', '012'),
('013', 'Oscar', 'Vargas', 'Contador', 'oscar.vargas@supermix-ejemplo.test', '900000013', '013'),
('014', 'Lucia', 'Medina', 'Analista de sistemas', 'lucia.medina@supermix-ejemplo.test', '900000014', '014'),
('015', 'Felipe', 'Caceres', 'Supervisor de infraestructura', 'felipe.caceres@supermix-ejemplo.test', '900000015', '015');


-- Datos de la tabla REQUERIMIENTO_COMPRA
-- Proposito: Crea requerimientos referenciando areas y empleados.
INSERT INTO requerimiento_compra
(num_requerimiento, fecha_requerimiento, observaciones, numero_area, numero_empleado_solicita)
VALUES
('00000141', '2026-08-01', 'Abastecimiento de cemento para produccion', '005', '005'),
('00000142', '2026-08-02', 'Reposicion de arena para almacen', '006', '006'),
('00000143', '2026-08-03', 'Agregado para obras programadas', '002', '002'),
('00000144', '2026-08-04', 'Reposicion de guantes de seguridad', '007', '007'),
('00000145', '2026-08-05', 'Cascos para personal de transporte', '009', '009'),
('00000146', '2026-08-06', 'Compra de acero para obras', '015', '015'),
('00000147', '2026-08-07', 'Aditivo para mezcla de concreto', '005', '005'),
('00000148', '2026-08-08', 'Lentes para mantenimiento (pendiente)', '003', '003'),
('00000149', '2026-08-09', 'Mantenimiento de mezcladora principal', '003', '003'),
('00000150', '2026-08-10', 'Calibracion de balanza de planta', '008', '008'),
('00000151', '2026-08-11', 'Traslado de agregados al proyecto', '009', '009'),
('00000152', '2026-08-12', 'Revision del tablero electrico', '003', '003'),
('00000153', '2026-08-13', 'Limpieza programada de silo', '005', '005'),
('00000154', '2026-08-14', 'Capacitacion en seguridad laboral', '007', '007'),
('00000155', '2026-08-15', 'Reparacion de faja (pendiente)', '003', '003');


-- Datos de la tabla PRODUCTO_SERVICIO
-- Proposito: Carga catalogo mixto de productos fisicos y servicios.
INSERT INTO producto_servicio
(numero_producto_servicio, nombre_producto_servicio, categoria, tipo, descripcion, unidad_medida)
VALUES
('001', 'Cemento Portland Tipo I', 'Materiales', 'Producto', 'Bolsa de cemento de 42.5 kg', 'Bolsa'),
('002', 'Arena gruesa lavada', 'Agregados', 'Producto', 'Arena gruesa para concreto', 'm3'),
('003', 'Piedra chancada 3/4', 'Agregados', 'Producto', 'Piedra chancada para mezclas', 'm3'),
('004', 'Guantes industriales', 'Seguridad', 'Producto', 'Guantes de proteccion de uso industrial', 'Par'),
('005', 'Casco de seguridad', 'Seguridad', 'Producto', 'Casco de proteccion con suspension', 'Unidad'),
('006', 'Acero corrugado 1/2', 'Materiales', 'Producto', 'Varillas de acero corrugado para obra', 'Varilla'),
('007', 'Aditivo plastificante', 'Quimicos', 'Producto', 'Aditivo reductor de agua para concreto', 'Galon'),
('008', 'Lentes de seguridad', 'Seguridad', 'Producto', 'Lentes transparentes de proteccion', 'Unidad'),
('009', 'Mantenimiento de mezcladora', 'Mantenimiento', 'Servicio', 'Mantenimiento preventivo de mezcladora', 'Servicio'),
('010', 'Calibracion de balanza', 'Calidad', 'Servicio', 'Calibracion de balanza de dosificacion', 'Servicio'),
('011', 'Transporte de agregados', 'Transporte', 'Servicio', 'Traslado de agregados en camion', 'Viaje'),
('012', 'Inspeccion electrica', 'Mantenimiento', 'Servicio', 'Revision de tableros y conexiones', 'Servicio'),
('013', 'Limpieza industrial de silo', 'Mantenimiento', 'Servicio', 'Limpieza especializada de silo', 'Servicio'),
('014', 'Capacitacion de seguridad', 'Capacitacion', 'Servicio', 'Curso sobre riesgos en planta', 'Sesion'),
('015', 'Reparacion de faja', 'Mantenimiento', 'Servicio', 'Reparacion de faja transportadora', 'Servicio');


-- Datos de la tabla PROVEEDOR
-- Proposito: Registra empresas proveedoras de ejemplo.
INSERT INTO proveedor
(ruc, razon_social, direccion, ciudad, telefono, correo)
VALUES
('20900000001', 'Cementos y Agregados del Sur S.A.C.', 'Av. Industrial 121, Arequipa', 'Arequipa', '900000021', 'contacto01@proveedor-ejemplo.test'),
('20900000002', 'Proveedora Industrial AQP S.A.C.', 'Av. Industrial 122, Arequipa', 'Arequipa', '900000022', 'contacto02@proveedor-ejemplo.test'),
('20900000003', 'Canteras Alto Sur S.A.C.', 'Av. Industrial 123, Arequipa', 'Yura', '900000023', 'contacto03@proveedor-ejemplo.test'),
('20900000004', 'Equipos Seguros del Sur E.I.R.L.', 'Av. Industrial 124, Arequipa', 'Arequipa', '900000024', 'contacto04@proveedor-ejemplo.test'),
('20900000005', 'Ferreteria Pacifico Sur S.A.C.', 'Av. Industrial 125, Arequipa', 'Arequipa', '900000025', 'contacto05@proveedor-ejemplo.test'),
('20900000006', 'Quimicos para Concreto S.A.C.', 'Av. Industrial 126, Arequipa', 'Lima', '900000026', 'contacto06@proveedor-ejemplo.test'),
('20900000007', 'Soluciones Industriales Andinas S.A.C.', 'Av. Industrial 127, Arequipa', 'Arequipa', '900000027', 'contacto07@proveedor-ejemplo.test'),
('20900000008', 'Distribuidora Planta Sur S.A.C.', 'Av. Industrial 128, Arequipa', 'Cerro Colorado', '900000028', 'contacto08@proveedor-ejemplo.test'),
('20900000009', 'Mantenimiento Mecanico Arequipa S.A.C.', 'Av. Industrial 129, Arequipa', 'Arequipa', '900000029', 'contacto09@proveedor-ejemplo.test'),
('20900000010', 'Metrologia Industrial Andina S.A.C.', 'Av. Industrial 130, Arequipa', 'Arequipa', '900000030', 'contacto10@proveedor-ejemplo.test'),
('20900000011', 'Transportes del Altiplano Sur S.A.C.', 'Av. Industrial 131, Arequipa', 'Juliaca', '900000031', 'contacto11@proveedor-ejemplo.test'),
('20900000012', 'Electricidad y Control Industrial S.A.C.', 'Av. Industrial 132, Arequipa', 'Arequipa', '900000032', 'contacto12@proveedor-ejemplo.test'),
('20900000013', 'Limpieza Industrial Misti S.A.C.', 'Av. Industrial 133, Arequipa', 'Arequipa', '900000033', 'contacto13@proveedor-ejemplo.test'),
('20900000014', 'Formacion Segura del Sur S.A.C.', 'Av. Industrial 134, Arequipa', 'Arequipa', '900000034', 'contacto14@proveedor-ejemplo.test'),
('20900000015', 'Servicios Tecnicos de Fajas S.A.C.', 'Av. Industrial 135, Arequipa', 'Arequipa', '900000035', 'contacto15@proveedor-ejemplo.test');


-- Datos de la tabla EVALUACION_PROVEEDOR
-- Proposito: Asocia cada evaluacion a un proveedor y requerimiento.
INSERT INTO evaluacion_proveedor
(numero_evaluacion, fecha_evaluacion, num_requerimiento, ruc)
VALUES
('000001', '2026-08-16', '00000141', '20900000001'),
('000002', '2026-08-17', '00000141', '20900000007'),
('000003', '2026-08-18', '00000142', '20900000002'),
('000004', '2026-08-19', '00000143', '20900000003'),
('000005', '2026-08-20', '00000144', '20900000004'),
('000006', '2026-08-21', '00000145', '20900000004'),
('000007', '2026-08-22', '00000146', '20900000005'),
('000008', '2026-08-23', '00000147', '20900000006'),
('000009', '2026-08-24', '00000148', '20900000008'),
('000010', '2026-08-25', '00000149', '20900000009'),
('000011', '2026-08-26', '00000150', '20900000010'),
('000012', '2026-08-27', '00000151', '20900000011'),
('000013', '2026-08-28', '00000152', '20900000012'),
('000014', '2026-08-29', '00000153', '20900000013'),
('000015', '2026-08-30', '00000154', '20900000014');


-- Datos de la tabla EVALUACION_CRITERIO
-- Proposito: Almacena las notas por criterio para calcular las evaluaciones.
INSERT INTO evaluacion_criterio
(numero_evaluacion, criterio, calificacion)
VALUES
('000001', 'Certificaciones de calidad', 2),
('000001', 'Relacion calidad precio', 2),
('000001', 'Cotizacion', 2),
('000001', 'Cumplimiento de plazos', 2),
('000001', 'Aspectos administrativos', 1),
('000001', 'Referencia comercial', 2),
('000002', 'Certificaciones de calidad', 2),
('000002', 'Relacion calidad precio', 1),
('000002', 'Cotizacion', 1),
('000002', 'Cumplimiento de plazos', 1),
('000002', 'Aspectos administrativos', 1),
('000002', 'Referencia comercial', 1),
('000003', 'Certificaciones de calidad', 2),
('000003', 'Relacion calidad precio', 1),
('000003', 'Cotizacion', 2),
('000003', 'Cumplimiento de plazos', 2),
('000003', 'Aspectos administrativos', 1),
('000003', 'Referencia comercial', 2),
('000004', 'Certificaciones de calidad', 2),
('000004', 'Relacion calidad precio', 2),
('000004', 'Cotizacion', 1),
('000004', 'Cumplimiento de plazos', 2),
('000004', 'Aspectos administrativos', 1),
('000004', 'Referencia comercial', 2),
('000005', 'Certificaciones de calidad', 2),
('000005', 'Relacion calidad precio', 2),
('000005', 'Cotizacion', 2),
('000005', 'Cumplimiento de plazos', 1),
('000005', 'Aspectos administrativos', 2),
('000005', 'Referencia comercial', 1),
('000006', 'Certificaciones de calidad', 2),
('000006', 'Relacion calidad precio', 1),
('000006', 'Cotizacion', 2),
('000006', 'Cumplimiento de plazos', 2),
('000006', 'Aspectos administrativos', 1),
('000006', 'Referencia comercial', 2),
('000007', 'Certificaciones de calidad', 2),
('000007', 'Relacion calidad precio', 2),
('000007', 'Cotizacion', 1),
('000007', 'Cumplimiento de plazos', 1),
('000007', 'Aspectos administrativos', 2),
('000007', 'Referencia comercial', 2),
('000008', 'Certificaciones de calidad', 2),
('000008', 'Relacion calidad precio', 1),
('000008', 'Cotizacion', 2),
('000008', 'Cumplimiento de plazos', 1),
('000008', 'Aspectos administrativos', 2),
('000008', 'Referencia comercial', 2),
('000009', 'Certificaciones de calidad', 1),
('000009', 'Relacion calidad precio', 1),
('000009', 'Cotizacion', 0),
('000009', 'Cumplimiento de plazos', 1),
('000009', 'Aspectos administrativos', 1),
('000009', 'Referencia comercial', 1),
('000010', 'Certificaciones de calidad', 2),
('000010', 'Relacion calidad precio', 2),
('000010', 'Cotizacion', 2),
('000010', 'Cumplimiento de plazos', 2),
('000010', 'Aspectos administrativos', 1),
('000010', 'Referencia comercial', 2),
('000011', 'Certificaciones de calidad', 2),
('000011', 'Relacion calidad precio', 2),
('000011', 'Cotizacion', 1),
('000011', 'Cumplimiento de plazos', 2),
('000011', 'Aspectos administrativos', 2),
('000011', 'Referencia comercial', 2),
('000012', 'Certificaciones de calidad', 2),
('000012', 'Relacion calidad precio', 1),
('000012', 'Cotizacion', 2),
('000012', 'Cumplimiento de plazos', 2),
('000012', 'Aspectos administrativos', 2),
('000012', 'Referencia comercial', 1),
('000013', 'Certificaciones de calidad', 2),
('000013', 'Relacion calidad precio', 2),
('000013', 'Cotizacion', 2),
('000013', 'Cumplimiento de plazos', 1),
('000013', 'Aspectos administrativos', 1),
('000013', 'Referencia comercial', 2),
('000014', 'Certificaciones de calidad', 2),
('000014', 'Relacion calidad precio', 2),
('000014', 'Cotizacion', 1),
('000014', 'Cumplimiento de plazos', 2),
('000014', 'Aspectos administrativos', 2),
('000014', 'Referencia comercial', 1),
('000015', 'Certificaciones de calidad', 2),
('000015', 'Relacion calidad precio', 2),
('000015', 'Cotizacion', 2),
('000015', 'Cumplimiento de plazos', 1),
('000015', 'Aspectos administrativos', 2),
('000015', 'Referencia comercial', 2);


-- Datos de la tabla ORDEN_COMPRA
-- Proposito: Crea encabezados de ordenes de compra.
INSERT INTO orden_compra
(num_orden_compra, fecha, moneda, condicion_pago, descuento, punto_entrega, justificacion, numero_empleado_genera, numero_empleado_aprueba, num_requerimiento, ruc)
VALUES
('000001', '2026-09-01', 'Soles', 'Contado', 45, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000141', '20900000001'),
('000002', '2026-09-02', 'Soles', 'Contado', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000142', '20900000002'),
('000003', '2026-09-03', 'Soles', 'Credito 30 dias', NULL, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000143', '20900000003'),
('000004', '2026-09-04', 'Soles', 'Contado', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000144', '20900000004'),
('000005', '2026-09-05', 'Soles', 'Contado', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000145', '20900000004'),
('000006', '2026-09-06', 'Soles', 'Credito 30 dias', 35, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000146', '20900000005'),
('000007', '2026-09-07', 'Soles', 'Contado', NULL, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000147', '20900000006'),
('000008', '2026-09-08', 'Soles', 'Contado', 20, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000141', '20900000007'),
('000009', '2026-09-09', 'Soles', 'Credito 30 dias', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000142', '20900000002'),
('000010', '2026-09-10', 'Soles', 'Contado', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000143', '20900000003'),
('000011', '2026-09-11', 'Soles', 'Contado', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000144', '20900000004'),
('000012', '2026-09-12', 'Soles', 'Credito 30 dias', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000145', '20900000004'),
('000013', '2026-09-13', 'Soles', 'Contado', 25, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000146', '20900000005'),
('000014', '2026-09-14', 'Soles', 'Contado', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000147', '20900000006'),
('000015', '2026-09-15', 'Soles', 'Credito 30 dias', 0, 'Almacen central Supermix', 'Abastecimiento de requerimiento', '011', '004', '00000141', '20900000001');


-- Datos de la tabla ORDEN_SERVICIO
-- Proposito: Crea encabezados de ordenes de servicio.
INSERT INTO orden_servicio
(num_orden_servicio, fecha, lugar_servicio, condicion_pago, numero_empleado_genera, numero_empleado_aprueba, num_requerimiento, ruc)
VALUES
('000001', '2026-09-01', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000149', '20900000009'),
('000002', '2026-09-02', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000150', '20900000010'),
('000003', '2026-09-03', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000151', '20900000011'),
('000004', '2026-09-04', 'Planta Supermix - Arequipa', NULL, '003', '002', '00000152', '20900000012'),
('000005', '2026-09-05', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000153', '20900000013'),
('000006', '2026-09-06', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000154', '20900000014'),
('000007', '2026-09-07', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000149', '20900000009'),
('000008', '2026-09-08', 'Planta Supermix - Arequipa', NULL, '003', '002', '00000150', '20900000010'),
('000009', '2026-09-09', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000151', '20900000011'),
('000010', '2026-09-10', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000152', '20900000012'),
('000011', '2026-09-11', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000153', '20900000013'),
('000012', '2026-09-12', 'Planta Supermix - Arequipa', NULL, '003', '002', '00000154', '20900000014'),
('000013', '2026-09-13', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000149', '20900000009'),
('000014', '2026-09-14', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000150', '20900000010'),
('000015', '2026-09-15', 'Planta Supermix - Arequipa', 'Transferencia', '003', '002', '00000151', '20900000011');


-- Datos de la tabla REQUERIMIENTO_PRODUCTO_SERVICIO
-- Proposito: Agrega los elementos y cantidades solicitadas.
INSERT INTO requerimiento_producto_servicio
(num_requerimiento, numero_producto_servicio, cantidad, especificaciones_tecnicas)
VALUES
('00000141', '001', 140, 'Bolsa de 42.5 kg'),
('00000142', '002', 40, 'Arena limpia sin impurezas'),
('00000143', '003', 35, 'Granulometria 3/4'),
('00000144', '004', 65, 'Talla M y L'),
('00000145', '005', 28, 'Con barbuquejo'),
('00000146', '006', 90, 'Varilla de 12 m'),
('00000147', '007', 20, 'Uso para concreto premezclado'),
('00000148', '008', 45, 'Resistencia al impacto'),
('00000149', '009', 3, 'Revision de componentes'),
('00000150', '010', 4, 'Con certificado de calibracion'),
('00000151', '011', 7, 'Camion de carga autorizado'),
('00000152', '012', 2, 'Evaluacion de seguridad electrica'),
('00000153', '013', 2, 'Trabajo con permisos vigentes'),
('00000154', '014', 3, 'Sesion para trabajadores'),
('00000155', '015', 1, 'Reparacion de elementos de traccion');


-- Datos de la tabla ORDEN_COMPRA_PRODUCTO_SERVICIO
-- Proposito: Agrega los productos, cantidades y precios de las compras.
INSERT INTO orden_compra_producto_servicio
(num_orden_compra, numero_producto_servicio, cantidad, precio_unitario)
VALUES
('000001', '001', 90, 39.50),
('000002', '002', 25, 55.00),
('000003', '003', 20, 67.00),
('000004', '004', 40, 18.90),
('000005', '005', 16, 32.00),
('000006', '006', 50, 42.50),
('000007', '007', 12, 135.00),
('000008', '001', 30, 38.00),
('000009', '002', 15, 54.00),
('000010', '003', 15, 68.00),
('000011', '004', 25, 19.00),
('000012', '005', 12, 33.00),
('000013', '006', 40, 41.00),
('000014', '007', 8, 130.00),
('000015', '001', 20, 40.00);


-- Datos de la tabla ORDEN_SERVICIO_PRODUCTO_SERVICIO
-- Proposito: Agrega los servicios, cantidades y precios de las ordenes.
INSERT INTO orden_servicio_producto_servicio
(num_orden_servicio, numero_producto_servicio, cantidad, precio_unitario)
VALUES
('000001', '009', 1, 2500.00),
('000002', '010', 1, 1200.00),
('000003', '011', 3, 850.00),
('000004', '012', 1, 1500.00),
('000005', '013', 1, 3100.00),
('000006', '014', 2, 650.00),
('000007', '009', 1, 2450.00),
('000008', '010', 1, 1180.00),
('000009', '011', 2, 900.00),
('000010', '012', 1, 1450.00),
('000011', '013', 1, 3000.00),
('000012', '014', 1, 630.00),
('000013', '009', 1, 2600.00),
('000014', '010', 2, 1220.00),
('000015', '011', 2, 880.00);


-- 4. CONSULTAS DE LA FUNCIONALIDAD
-- Estas 10 consultas generan resultados para las figuras del informe.
-- Se pueden ejecutar individualmente en pgAdmin seleccionando cada SELECT.
