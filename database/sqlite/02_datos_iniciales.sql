-- InmoTech - datos iniciales para SQLite (equivalente a ../02_datos_iniciales.sql).
-- Solo se cargan cuando la tabla rol esta vacia. Clave de los usuarios de prueba: 123456

INSERT INTO rol (id_rol, nombre) VALUES
    (1, 'ADMINISTRADOR'), (2, 'VENDEDOR'), (3, 'COMPRADOR');
INSERT INTO departamento (id_departamento, nombre) VALUES
    (1, 'Cundinamarca'), (2, 'Antioquia'), (3, 'Valle del Cauca'),
    (4, 'Atlántico'), (5, 'Santander'), (6, 'Bolívar');
INSERT INTO ciudad (id_ciudad, nombre, id_departamento) VALUES
    (1, 'Bogotá D.C.', 1), (2, 'Chía', 1), (3, 'Soacha', 1),
    (4, 'Medellín', 2), (5, 'Envigado', 2), (6, 'Rionegro', 2),
    (7, 'Cali', 3), (8, 'Palmira', 3), (9, 'Barranquilla', 4),
    (10, 'Bucaramanga', 5), (11, 'Floridablanca', 5), (12, 'Cartagena', 6);
INSERT INTO categoria (id_categoria, nombre) VALUES
    (1, 'Casa'), (2, 'Apartamento'), (3, 'Lote'), (4, 'Local');
INSERT INTO usuario
    (id_usuario, nombre, apellido, correo, password_hash, telefono, id_rol)
VALUES
    (1, 'Andrés', 'Morales', 'admin@inmotech.com',
     'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736',
     '3001234567', 1),
    (2, 'Carlos', 'Mendoza', 'carlos.vendedor@inmotech.com',
     'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736',
     '3109876543', 2),
    (3, 'María', 'Gómez', 'maria.vendedora@inmotech.com',
     'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736',
     '3154567890', 2),
    (4, 'Juan', 'Pérez', 'juan.comprador@gmail.com',
     'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736',
     '3201122334', 3),
    (5, 'Laura', 'Rodríguez', 'laura.compradora@gmail.com',
     'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736',
     '3187766554', 3);
INSERT INTO inmueble
    (id_inmueble, titulo, descripcion, direccion, precio, area,
     habitaciones, banos, operacion, estado, id_categoria, id_ciudad, id_vendedor)
VALUES
    (1, 'Apartamento Moderno en Chapinero Alto',
     'Apartamento iluminado con vista a los cerros, cocina abierta y parqueadero privado.',
     'Carrera 4 # 68-45, Chapinero', 485000000, 78.5, 2, 2, 'VENTA', 'DISPONIBLE', 2, 1, 2),
    (2, 'Casa Campestre Exclusiva en Chía',
     'Casa campestre con jardines, zona BBQ, chimenea y parqueadero para cuatro vehículos.',
     'Vereda Bojacá, Conjunto El Trébol Casa 12', 890000000, 260, 4, 4, 'VENTA', 'DISPONIBLE', 1, 2, 2),
    (3, 'Apartamento Amoblado en El Poblado',
     'Apartamento amoblado con balcón, piscina y gimnasio en unidad cerrada.',
     'Calle 10A # 28-30, El Poblado', 3800000, 65, 1, 1, 'ARRIENDO', 'DISPONIBLE', 2, 4, 3),
    (4, 'Local Comercial en Centro Financiero',
     'Local a pie de calle con vitrina, mezzanine y baños para clientes.',
     'Calle 72 # 11-20', 7500000, 110, 0, 2, 'ARRIENDO', 'DISPONIBLE', 4, 1, 2),
    (5, 'Lote Urbanizado en Rionegro',
     'Lote campestre con servicios, ideal para vivienda unifamiliar.',
     'Sector Llanogrande, Parcelación Los Sauces Lote 8', 340000000, 1200, 0, 0, 'VENTA', 'DISPONIBLE', 3, 6, 3),
    (6, 'Casa Familiar en Ciudad Jardín Cali',
     'Casa de dos plantas con piscina, patio interior y estudio.',
     'Avenida San Joaquín # 14-55, Ciudad Jardín', 720000000, 220, 4, 3, 'VENTA', 'DISPONIBLE', 1, 7, 3),
    (7, 'Apartamento Dúplex con Terraza',
     'Dúplex con terraza BBQ, vestier y doble garaje.',
     'Carrera 35 # 48-12, Cabecera del Llano', 620000000, 145, 3, 3, 'VENTA', 'DISPONIBLE', 2, 10, 2),
    (8, 'Apartamento Frente a la Bahía',
     'Apartamento remodelado con vista al mar, muelle y piscina.',
     'Carrera 1 # 12-80, Bocagrande', 5500000, 92, 2, 2, 'ARRIENDO', 'NO_DISPONIBLE', 2, 12, 3);
INSERT INTO visita
    (id_visita, fecha_visita, mensaje, estado, id_inmueble, id_comprador)
VALUES
    (1, '2026-11-25 10:00:00', 'Me interesa conocer la propiedad.', 'PENDIENTE', 1, 4),
    (2, '2026-11-20 15:30:00', 'Visitaré la casa con mi familia.', 'CONFIRMADA', 2, 4),
    (3, '2026-10-15 11:00:00', 'Visita realizada.', 'REALIZADA', 3, 5),
    (4, '2026-11-12 09:00:00', 'Solicitud cancelada.', 'CANCELADA', 4, 5);
