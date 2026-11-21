-- ============================================================================
-- LECTURA DEL SCRIPT:
--   CREATE TABLE define entidades; PRIMARY KEY impide identificadores duplicados.
--   REFERENCES materializa las relaciones; CHECK evita valores fuera de dominio.
--   Los indices facilitan búsquedas; no sustituyen las reglas de negocio.
-- SUPERMIX GDI | 01 - CREACION DE LA BASE DE DATOS (MODELO FISICO)
-- Motor: PostgreSQL. Ejecutar sobre una base de datos nueva, por ejemplo supermix_gdi.
-- Objetivo: crear las 12 tablas, relaciones, restricciones y los indices de acceso.
-- IMPORTANTE: este script no hace CREATE DATABASE. Primero crear la BD en pgAdmin.
-- Recomendacion: no ejecutarlo dos veces sobre las mismas tablas sin restablecer la BD.
-- ============================================================================
-- 1. CREACION DE LAS TABLAS
-- Se crean primero las tablas principales y despues las que las referencian.

-- Tabla 1: AREA
-- Finalidad: Unidades organizacionales a las que pertenecen empleados y requerimientos.
CREATE TABLE area (
    numero_area CHAR(3) PRIMARY KEY CHECK (numero_area ~ '^[0-9]{3}$'),
    nombre_area VARCHAR(50) NOT NULL CHECK (BTRIM(nombre_area) <> '')
);

-- Tabla 2: EMPLEADO
-- Finalidad: Personal asociado a un area; puede solicitar, generar o aprobar ordenes.
CREATE TABLE empleado (
    numero_empleado CHAR(3) PRIMARY KEY CHECK (numero_empleado ~ '^[0-9]{3}$'),
    nombre VARCHAR(50) NOT NULL CHECK (BTRIM(nombre) <> ''),
    apellido VARCHAR(50) NOT NULL CHECK (BTRIM(apellido) <> ''),
    cargo VARCHAR(60) NOT NULL CHECK (BTRIM(cargo) <> ''),
    correo VARCHAR(100) CHECK (correo ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    telefono CHAR(9) CHECK (telefono ~ '^[0-9]{9}$'),
    numero_area CHAR(3) NOT NULL CHECK (numero_area ~ '^[0-9]{3}$'),
    FOREIGN KEY (numero_area) REFERENCES area(numero_area)
);

-- Tabla 3: REQUERIMIENTO_COMPRA
-- Finalidad: Solicitud de adquisicion con fecha, area y empleado responsable.
CREATE TABLE requerimiento_compra (
    num_requerimiento VARCHAR(8) PRIMARY KEY CHECK (num_requerimiento ~ '^[0-9]{1,8}$'),
    fecha_requerimiento DATE NOT NULL,
    observaciones VARCHAR(200),
    numero_area CHAR(3) NOT NULL CHECK (numero_area ~ '^[0-9]{3}$'),
    numero_empleado_solicita CHAR(3) NOT NULL CHECK (numero_empleado_solicita ~ '^[0-9]{3}$'),
    FOREIGN KEY (numero_area) REFERENCES area(numero_area),
    FOREIGN KEY (numero_empleado_solicita) REFERENCES empleado(numero_empleado)
);

-- Tabla 4: PRODUCTO_SERVICIO
-- Finalidad: Catalogo unificado; tipo distingue productos de servicios.
CREATE TABLE producto_servicio (
    numero_producto_servicio CHAR(3) PRIMARY KEY CHECK (numero_producto_servicio ~ '^[0-9]{3}$'),
    nombre_producto_servicio VARCHAR(100) NOT NULL CHECK (BTRIM(nombre_producto_servicio) <> ''),
    categoria VARCHAR(50) NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('Producto', 'Servicio')),
    descripcion VARCHAR(200) NOT NULL CHECK (BTRIM(descripcion) <> ''),
    unidad_medida VARCHAR(30) NOT NULL CHECK (BTRIM(unidad_medida) <> '')
);

-- Tabla 5: PROVEEDOR
-- Finalidad: Personas juridicas proveedoras identificadas por RUC.
CREATE TABLE proveedor (
    ruc CHAR(11) PRIMARY KEY CHECK (ruc ~ '^[0-9]{11}$'),
    razon_social VARCHAR(100) NOT NULL CHECK (BTRIM(razon_social) <> ''),
    direccion VARCHAR(150),
    ciudad VARCHAR(50) NOT NULL,
    telefono CHAR(9) CHECK (telefono ~ '^[0-9]{9}$'),
    correo VARCHAR(100) CHECK (correo ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Tabla 6: EVALUACION_PROVEEDOR
-- Finalidad: Encabezado de una evaluacion asociada a solicitud y proveedor.
CREATE TABLE evaluacion_proveedor (
    numero_evaluacion VARCHAR(6) PRIMARY KEY CHECK (numero_evaluacion ~ '^[0-9]{1,6}$'),
    fecha_evaluacion DATE NOT NULL,
    num_requerimiento VARCHAR(8) NOT NULL CHECK (num_requerimiento ~ '^[0-9]{1,8}$'),
    ruc CHAR(11) NOT NULL CHECK (ruc ~ '^[0-9]{11}$'),
    FOREIGN KEY (num_requerimiento) REFERENCES requerimiento_compra(num_requerimiento),
    FOREIGN KEY (ruc) REFERENCES proveedor(ruc)
);

-- Tabla 7: EVALUACION_CRITERIO
-- Finalidad: Seis criterios puntuados de 0 a 2; PK compuesta evaluacion-criterio.
CREATE TABLE evaluacion_criterio (
    numero_evaluacion VARCHAR(6) NOT NULL CHECK (numero_evaluacion ~ '^[0-9]{1,6}$'),
    criterio VARCHAR(100) NOT NULL CHECK (criterio IN ('Certificaciones de calidad', 'Relacion calidad precio', 'Cotizacion', 'Cumplimiento de plazos', 'Aspectos administrativos', 'Referencia comercial')),
    calificacion INTEGER NOT NULL CHECK (calificacion BETWEEN 0 AND 2),
    PRIMARY KEY (numero_evaluacion, criterio),
    FOREIGN KEY (numero_evaluacion) REFERENCES evaluacion_proveedor(numero_evaluacion)
);

-- Tabla 8: ORDEN_COMPRA
-- Finalidad: Encabezado de compra con moneda, descuento y responsables.
CREATE TABLE orden_compra (
    num_orden_compra VARCHAR(6) PRIMARY KEY CHECK (num_orden_compra ~ '^[0-9]{1,6}$'),
    fecha DATE NOT NULL,
    moneda VARCHAR(10) NOT NULL CHECK (moneda IN ('Soles', 'Dolares')),
    condicion_pago VARCHAR(50) NOT NULL,
    descuento NUMERIC(10,2) CHECK (descuento >= 0),
    punto_entrega VARCHAR(100) NOT NULL,
    justificacion VARCHAR(200),
    numero_empleado_genera CHAR(3) NOT NULL CHECK (numero_empleado_genera ~ '^[0-9]{3}$'),
    numero_empleado_aprueba CHAR(3) NOT NULL CHECK (numero_empleado_aprueba ~ '^[0-9]{3}$'),
    num_requerimiento VARCHAR(8) NOT NULL CHECK (num_requerimiento ~ '^[0-9]{1,8}$'),
    ruc CHAR(11) NOT NULL CHECK (ruc ~ '^[0-9]{11}$'),
    FOREIGN KEY (numero_empleado_genera) REFERENCES empleado(numero_empleado),
    FOREIGN KEY (numero_empleado_aprueba) REFERENCES empleado(numero_empleado),
    FOREIGN KEY (num_requerimiento) REFERENCES requerimiento_compra(num_requerimiento),
    FOREIGN KEY (ruc) REFERENCES proveedor(ruc)
);

-- Tabla 9: ORDEN_SERVICIO
-- Finalidad: Encabezado de servicios con lugar de realizacion y responsables.
CREATE TABLE orden_servicio (
    num_orden_servicio VARCHAR(6) PRIMARY KEY CHECK (num_orden_servicio ~ '^[0-9]{1,6}$'),
    fecha DATE NOT NULL,
    lugar_servicio VARCHAR(100) NOT NULL,
    condicion_pago VARCHAR(50),
    numero_empleado_genera CHAR(3) NOT NULL CHECK (numero_empleado_genera ~ '^[0-9]{3}$'),
    numero_empleado_aprueba CHAR(3) NOT NULL CHECK (numero_empleado_aprueba ~ '^[0-9]{3}$'),
    num_requerimiento VARCHAR(8) NOT NULL CHECK (num_requerimiento ~ '^[0-9]{1,8}$'),
    ruc CHAR(11) NOT NULL CHECK (ruc ~ '^[0-9]{11}$'),
    FOREIGN KEY (numero_empleado_genera) REFERENCES empleado(numero_empleado),
    FOREIGN KEY (numero_empleado_aprueba) REFERENCES empleado(numero_empleado),
    FOREIGN KEY (num_requerimiento) REFERENCES requerimiento_compra(num_requerimiento),
    FOREIGN KEY (ruc) REFERENCES proveedor(ruc)
);

-- Tabla 10: REQUERIMIENTO_PRODUCTO_SERVICIO
-- Finalidad: Detalle y cantidad solicitada por producto/servicio en requerimiento.
CREATE TABLE requerimiento_producto_servicio (
    num_requerimiento VARCHAR(8) NOT NULL CHECK (num_requerimiento ~ '^[0-9]{1,8}$'),
    numero_producto_servicio CHAR(3) NOT NULL CHECK (numero_producto_servicio ~ '^[0-9]{3}$'),
    cantidad INTEGER NOT NULL CHECK (cantidad BETWEEN 1 AND 999999),
    especificaciones_tecnicas VARCHAR(200),
    PRIMARY KEY (num_requerimiento, numero_producto_servicio),
    FOREIGN KEY (num_requerimiento) REFERENCES requerimiento_compra(num_requerimiento),
    FOREIGN KEY (numero_producto_servicio) REFERENCES producto_servicio(numero_producto_servicio)
);

-- Tabla 11: ORDEN_COMPRA_PRODUCTO_SERVICIO
-- Finalidad: Detalle de articulos comprados con cantidad y precio unitario.
CREATE TABLE orden_compra_producto_servicio (
    num_orden_compra VARCHAR(6) NOT NULL CHECK (num_orden_compra ~ '^[0-9]{1,6}$'),
    numero_producto_servicio CHAR(3) NOT NULL CHECK (numero_producto_servicio ~ '^[0-9]{3}$'),
    cantidad INTEGER NOT NULL CHECK (cantidad BETWEEN 1 AND 999999),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    PRIMARY KEY (num_orden_compra, numero_producto_servicio),
    FOREIGN KEY (num_orden_compra) REFERENCES orden_compra(num_orden_compra),
    FOREIGN KEY (numero_producto_servicio) REFERENCES producto_servicio(numero_producto_servicio)
);

-- Tabla 12: ORDEN_SERVICIO_PRODUCTO_SERVICIO
-- Finalidad: Detalle de servicios contratados con cantidad y precio unitario.
CREATE TABLE orden_servicio_producto_servicio (
    num_orden_servicio VARCHAR(6) NOT NULL CHECK (num_orden_servicio ~ '^[0-9]{1,6}$'),
    numero_producto_servicio CHAR(3) NOT NULL CHECK (numero_producto_servicio ~ '^[0-9]{3}$'),
    cantidad INTEGER NOT NULL CHECK (cantidad BETWEEN 1 AND 999999),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    PRIMARY KEY (num_orden_servicio, numero_producto_servicio),
    FOREIGN KEY (num_orden_servicio) REFERENCES orden_servicio(num_orden_servicio),
    FOREIGN KEY (numero_producto_servicio) REFERENCES producto_servicio(numero_producto_servicio)
);

-- 2. INDICES SECUNDARIOS
-- Ayudan en las consultas por area, fecha, proveedor y referencias.
-- Las claves primarias generan sus propios indices automaticamente.

-- Indice idx_empleado_area: apoya busquedas o joins por numero_area en empleado.
CREATE INDEX idx_empleado_area
ON empleado(numero_area);

-- Indice idx_requerimiento_area: apoya busquedas o joins por numero_area en requerimiento_compra.
CREATE INDEX idx_requerimiento_area
ON requerimiento_compra(numero_area);

-- Indice idx_requerimiento_empleado: apoya busquedas o joins por numero_empleado_solicita en requerimiento_compra.
CREATE INDEX idx_requerimiento_empleado
ON requerimiento_compra(numero_empleado_solicita);

-- Indice idx_requerimiento_fecha: apoya busquedas o joins por fecha_requerimiento en requerimiento_compra.
CREATE INDEX idx_requerimiento_fecha
ON requerimiento_compra(fecha_requerimiento);

-- Indice idx_evaluacion_requerimiento: apoya busquedas o joins por num_requerimiento en evaluacion_proveedor.
CREATE INDEX idx_evaluacion_requerimiento
ON evaluacion_proveedor(num_requerimiento);

-- Indice idx_evaluacion_proveedor: apoya busquedas o joins por ruc en evaluacion_proveedor.
CREATE INDEX idx_evaluacion_proveedor
ON evaluacion_proveedor(ruc);

-- Indice idx_compra_empleado_genera: apoya busquedas o joins por numero_empleado_genera en orden_compra.
CREATE INDEX idx_compra_empleado_genera
ON orden_compra(numero_empleado_genera);

-- Indice idx_compra_empleado_aprueba: apoya busquedas o joins por numero_empleado_aprueba en orden_compra.
CREATE INDEX idx_compra_empleado_aprueba
ON orden_compra(numero_empleado_aprueba);

-- Indice idx_compra_requerimiento: apoya busquedas o joins por num_requerimiento en orden_compra.
CREATE INDEX idx_compra_requerimiento
ON orden_compra(num_requerimiento);

-- Indice idx_compra_proveedor: apoya busquedas o joins por ruc en orden_compra.
CREATE INDEX idx_compra_proveedor
ON orden_compra(ruc);

-- Indice idx_compra_fecha: apoya busquedas o joins por fecha en orden_compra.
CREATE INDEX idx_compra_fecha
ON orden_compra(fecha);

-- Indice idx_servicio_empleado_genera: apoya busquedas o joins por numero_empleado_genera en orden_servicio.
CREATE INDEX idx_servicio_empleado_genera
ON orden_servicio(numero_empleado_genera);

-- Indice idx_servicio_empleado_aprueba: apoya busquedas o joins por numero_empleado_aprueba en orden_servicio.
CREATE INDEX idx_servicio_empleado_aprueba
ON orden_servicio(numero_empleado_aprueba);

-- Indice idx_servicio_requerimiento: apoya busquedas o joins por num_requerimiento en orden_servicio.
CREATE INDEX idx_servicio_requerimiento
ON orden_servicio(num_requerimiento);

-- Indice idx_servicio_proveedor: apoya busquedas o joins por ruc en orden_servicio.
CREATE INDEX idx_servicio_proveedor
ON orden_servicio(ruc);

-- Indice idx_servicio_fecha: apoya busquedas o joins por fecha en orden_servicio.
CREATE INDEX idx_servicio_fecha
ON orden_servicio(fecha);

-- Indice idx_req_producto: apoya busquedas o joins por numero_producto_servicio en requerimiento_producto_servicio.
CREATE INDEX idx_req_producto
ON requerimiento_producto_servicio(numero_producto_servicio);

-- Indice idx_compra_producto: apoya busquedas o joins por numero_producto_servicio en orden_compra_producto_servicio.
CREATE INDEX idx_compra_producto
ON orden_compra_producto_servicio(numero_producto_servicio);

-- Indice idx_servicio_producto: apoya busquedas o joins por numero_producto_servicio en orden_servicio_producto_servicio.
CREATE INDEX idx_servicio_producto
ON orden_servicio_producto_servicio(numero_producto_servicio);
