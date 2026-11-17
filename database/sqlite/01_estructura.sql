

CREATE TABLE IF NOT EXISTS rol (
    id_rol INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    telefono TEXT NOT NULL,
    id_rol INTEGER NOT NULL REFERENCES rol(id_rol)
);
CREATE TABLE IF NOT EXISTS departamento (
    id_departamento INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS ciudad (
    id_ciudad INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    id_departamento INTEGER NOT NULL REFERENCES departamento(id_departamento)
);
CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS inmueble (
    id_inmueble INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    direccion TEXT NOT NULL,
    precio NUMERIC NOT NULL CHECK (precio > 0),
    area NUMERIC NOT NULL CHECK (area > 0),
    habitaciones INTEGER NOT NULL DEFAULT 0 CHECK (habitaciones >= 0),
    banos INTEGER NOT NULL DEFAULT 0 CHECK (banos >= 0),
    operacion TEXT NOT NULL CHECK (operacion IN ('VENTA', 'ARRIENDO')),
    estado TEXT NOT NULL DEFAULT 'DISPONIBLE'
        CHECK (estado IN ('DISPONIBLE', 'NO_DISPONIBLE')),
    id_categoria INTEGER NOT NULL REFERENCES categoria(id_categoria),
    id_ciudad INTEGER NOT NULL REFERENCES ciudad(id_ciudad),
    id_vendedor INTEGER NOT NULL REFERENCES usuario(id_usuario)
);
CREATE TABLE IF NOT EXISTS visita (
    id_visita INTEGER PRIMARY KEY,
    fecha_visita TEXT NOT NULL,
    mensaje TEXT,
    estado TEXT NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'REALIZADA')),
    id_inmueble INTEGER NOT NULL REFERENCES inmueble(id_inmueble),
    id_comprador INTEGER NOT NULL REFERENCES usuario(id_usuario)
);

-- Indices (mismos que en la version MySQL)
CREATE INDEX IF NOT EXISTS idx_usuario_rol        ON usuario(id_rol);
CREATE INDEX IF NOT EXISTS idx_ciudad_departamento ON ciudad(id_departamento);
CREATE INDEX IF NOT EXISTS idx_inmueble_estado    ON inmueble(estado);
CREATE INDEX IF NOT EXISTS idx_inmueble_ciudad    ON inmueble(id_ciudad);
CREATE INDEX IF NOT EXISTS idx_inmueble_categoria ON inmueble(id_categoria);
CREATE INDEX IF NOT EXISTS idx_inmueble_operacion ON inmueble(operacion);
CREATE INDEX IF NOT EXISTS idx_inmueble_precio    ON inmueble(precio);
CREATE INDEX IF NOT EXISTS idx_inmueble_vendedor  ON inmueble(id_vendedor);
CREATE INDEX IF NOT EXISTS idx_visita_inmueble    ON visita(id_inmueble);
CREATE INDEX IF NOT EXISTS idx_visita_comprador   ON visita(id_comprador);
CREATE INDEX IF NOT EXISTS idx_visita_estado      ON visita(estado);
CREATE INDEX IF NOT EXISTS idx_visita_fecha       ON visita(fecha_visita);
