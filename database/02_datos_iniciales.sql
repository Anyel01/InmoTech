

USE `inmotech_db`;


INSERT INTO `rol` (`id_rol`, `nombre`) VALUES
(1, 'ADMINISTRADOR'),
(2, 'VENDEDOR'),
(3, 'COMPRADOR');

INSERT INTO `departamento` (`id_departamento`, `nombre`) VALUES
(1, 'Cundinamarca'),
(2, 'Antioquia'),
(3, 'Valle del Cauca'),
(4, 'Atlántico'),
(5, 'Santander'),
(6, 'Bolívar');


INSERT INTO `ciudad` (`id_ciudad`, `nombre`, `id_departamento`) VALUES
(1, 'Bogotá D.C.', 1),
(2, 'Chía', 1),
(3, 'Soacha', 1),
(4, 'Medellín', 2),
(5, 'Envigado', 2),
(6, 'Rionegro', 2),
(7, 'Cali', 3),
(8, 'Palmira', 3),
(9, 'Barranquilla', 4),
(10, 'Bucaramanga', 5),
(11, 'Floridablanca', 5),
(12, 'Cartagena', 6);


INSERT INTO `categoria` (`id_categoria`, `nombre`) VALUES
(1, 'Casa'),
(2, 'Apartamento'),
(3, 'Lote'),
(4, 'Local');

INSERT INTO `usuario` (`id_usuario`, `nombre`, `apellido`, `correo`, `password_hash`, `telefono`, `id_rol`) VALUES
(1, 'Andrés', 'Morales', 'admin@inmotech.com', 'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736', '3001234567', 1),
(2, 'Carlos', 'Mendoza', 'carlos.vendedor@inmotech.com', 'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736', '3109876543', 2),
(3, 'María', 'Gómez', 'maria.vendedora@inmotech.com', 'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736', '3154567890', 2),
(4, 'Juan', 'Pérez', 'juan.comprador@gmail.com', 'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736', '3201122334', 3),
(5, 'Laura', 'Rodríguez', 'laura.compradora@gmail.com', 'pbkdf2:sha256:260000$4684a3f05b32a355$48edcb968ea656ac67011d62a103e41497497bac45acd4b732cbd70016037736', '3187766554', 3);


INSERT INTO `inmueble` (`id_inmueble`, `titulo`, `descripcion`, `direccion`, `precio`, `area`, `habitaciones`, `banos`, `operacion`, `estado`, `id_categoria`, `id_ciudad`, `id_vendedor`) VALUES
(1, 'Apartamento Moderno en Chapinero Alto', 'Hermoso apartamento iluminado con vista panorámica a los cerros orientales, acabados de lujo, cocina tipo americano y parqueadero cubierto privado.', 'Carrera 4 # 68-45, Chapinero', 485000000.00, 78.50, 2, 2, 'VENTA', 'DISPONIBLE', 2, 1, 2),
(2, 'Casa Campestre Exclusiva en Chía', 'Amplia casa campestre con jardines privados, zona BBQ, chimenea tradicional, 3 niveles, cuarto de servicio y parqueadero para 4 vehículos.', 'Vereda Bojacá, Conjunto El Trébol Casa 12', 890000000.00, 260.00, 4, 4, 'VENTA', 'DISPONIBLE', 1, 2, 2),
(3, 'Apartamento Amoblado en El Poblado', 'Acogedor apartamento completamente dotado en el sector más exclusivo de Medellín, balcón amplio, piscina y gimnasio en la unidad cerrada.', 'Calle 10A # 28-30, El Poblado', 3800000.00, 65.00, 1, 1, 'ARRIENDO', 'DISPONIBLE', 2, 4, 3),
(4, 'Local Comercial en Centro Financiero Calle 72', 'Excelente local a pie de calle con alto flujo peatonal y vehicular, vitrina en vidrio templado, mezzanine y batería de baños para clientes.', 'Calle 72 # 11-20', 7500000.00, 110.00, 0, 2, 'ARRIENDO', 'DISPONIBLE', 4, 1, 2),
(5, 'Lote Urbanizado en Rionegro Llanogrande', 'Lote plano campestre con punto de agua, gas y electricidad. Ideal para construcción de vivienda unifamiliar en parcelación con vigilancia 24h.', 'Sector Llanogrande, Parcelación Los Sauces Lote 8', 340000000.00, 1200.00, 0, 0, 'VENTA', 'DISPONIBLE', 3, 6, 3),
(6, 'Casa Familiar en Ciudad Jardín Cali', 'Casa tradicional de dos plantas con piscina privada, patio interior arborizado, estar de alcobas, sala comedor independiente y estudio.', 'Avenida San Joaquín # 14-55, Ciudad Jardín', 720000000.00, 220.00, 4, 3, 'VENTA', 'DISPONIBLE', 1, 7, 3),
(7, 'Apartamento Dúplex con Terraza en Cabecera', 'Espectacular dúplex con terraza BBQ privada de 35m2, alcoba principal con vestier y jacuzzi, cocina integral cerrada y doble garaje.', 'Carrera 35 # 48-12, Cabecera del Llano', 620000000.00, 145.00, 3, 3, 'VENTA', 'DISPONIBLE', 2, 10, 2),
(8, 'Apartamento en Bocagrande Frente a la Bahía', 'Apartamento remodelado con vista directa al mar y la bahía, aire central, edificio con muelle privado y piscina sin fin.', 'Carrera 1 # 12-80, Bocagrande', 5500000.00, 92.00, 2, 2, 'ARRIENDO', 'NO_DISPONIBLE', 2, 12, 3);


INSERT INTO `visita` (`id_visita`, `fecha_visita`, `mensaje`, `estado`, `id_inmueble`, `id_comprador`) VALUES
(1, '2026-11-25 10:00:00', 'Buenas tardes, estoy muy interesado en adquirir el apartamento. ¿Podemos revisar la documentación del inmueble durante la visita?', 'PENDIENTE', 1, 4),
(2, '2026-11-20 15:30:00', 'Quisiera visitar la casa campestre en Chía en compañía de mi familia y un arquitecto para evaluar reformas.', 'CONFIRMADA', 2, 4),
(3, '2026-10-15 11:00:00', 'Visita realizada satisfactoriamente con el cliente.', 'REALIZADA', 3, 5),
(4, '2026-11-12 09:00:00', 'El comprador canceló por motivo de viaje fuera de la ciudad.', 'CANCELADA', 4, 5);
