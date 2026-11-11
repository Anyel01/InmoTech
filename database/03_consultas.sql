

USE `inmotech_db`;

SELECT 
    i.id_inmueble,
    i.titulo,
    i.descripcion,
    i.direccion,
    i.precio,
    i.area,
    i.habitaciones,
    i.banos,
    i.operacion,
    i.estado,
    c.nombre AS categoria,
    ci.nombre AS ciudad,
    d.nombre AS departamento,
    CONCAT(u.nombre, ' ', u.apellido) AS vendedor,
    u.telefono AS telefono_vendedor,
    u.correo AS correo_vendedor
FROM `inmueble` i
INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
INNER JOIN `usuario` u ON i.id_vendedor = u.id_usuario
WHERE i.estado = 'DISPONIBLE'
ORDER BY i.id_inmueble DESC;

SELECT 
    i.id_inmueble,
    i.titulo,
    i.precio,
    i.area,
    i.habitaciones,
    i.banos,
    i.operacion,
    c.nombre AS categoria,
    ci.nombre AS ciudad
FROM `inmueble` i
INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
WHERE i.estado = 'DISPONIBLE'
  AND (i.id_ciudad = 1 OR 1 IS NULL)
  AND (i.id_categoria = 2 OR 2 IS NULL)
  AND (i.operacion = 'VENTA' OR 'VENTA' IS NULL)
  AND (i.precio >= 200000000 OR 200000000 IS NULL)
  AND (i.precio <= 600000000 OR 600000000 IS NULL)
  AND (i.habitaciones >= 2 OR 2 IS NULL)
ORDER BY i.precio ASC;


SELECT 
    i.id_inmueble,
    i.titulo,
    i.descripcion,
    i.direccion,
    i.precio,
    i.area,
    i.habitaciones,
    i.banos,
    i.operacion,
    i.estado,
    i.id_categoria,
    i.id_ciudad,
    i.id_vendedor,
    c.nombre AS categoria,
    ci.nombre AS ciudad,
    d.nombre AS departamento,
    CONCAT(u.nombre, ' ', u.apellido) AS vendedor_nombre,
    u.telefono AS vendedor_telefono,
    u.correo AS vendedor_correo
FROM `inmueble` i
INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
INNER JOIN `usuario` u ON i.id_vendedor = u.id_usuario
WHERE i.id_inmueble = 1;


SELECT 
    i.id_inmueble,
    i.titulo,
    i.precio,
    i.area,
    i.habitaciones,
    i.banos,
    i.operacion,
    i.estado,
    c.nombre AS categoria,
    ci.nombre AS ciudad,
    d.nombre AS departamento,
    COUNT(v.id_visita) AS total_visitas
FROM `inmueble` i
INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
LEFT JOIN `visita` v ON i.id_inmueble = v.id_inmueble
WHERE i.id_vendedor = 2
GROUP BY i.id_inmueble, i.titulo, i.precio, i.area, i.habitaciones, i.banos, i.operacion, i.estado, c.nombre, ci.nombre, d.nombre
ORDER BY i.id_inmueble DESC;


SELECT 
    v.id_visita,
    v.fecha_visita,
    v.mensaje,
    v.estado,
    i.id_inmueble,
    i.titulo AS inmueble_titulo,
    i.direccion AS inmueble_direccion,
    i.precio AS inmueble_precio,
    i.operacion AS inmueble_operacion,
    ci.nombre AS inmueble_ciudad,
    CONCAT(vend.nombre, ' ', vend.apellido) AS vendedor_nombre,
    vend.telefono AS vendedor_telefono,
    vend.correo AS vendedor_correo
FROM `visita` v
INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
INNER JOIN `usuario` vend ON i.id_vendedor = vend.id_usuario
WHERE v.id_comprador = 4
ORDER BY v.fecha_visita DESC;


SELECT 
    v.id_visita,
    v.fecha_visita,
    v.mensaje,
    v.estado,
    i.id_inmueble,
    i.titulo AS inmueble_titulo,
    i.direccion AS inmueble_direccion,
    CONCAT(comp.nombre, ' ', comp.apellido) AS comprador_nombre,
    comp.correo AS comprador_correo,
    comp.telefono AS comprador_telefono
FROM `visita` v
INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
INNER JOIN `usuario` comp ON v.id_comprador = comp.id_usuario
WHERE i.id_vendedor = 2
ORDER BY v.fecha_visita ASC;


SELECT 
    c.nombre AS categoria, 
    COUNT(i.id_inmueble) AS total_disponibles,
    AVG(i.precio) AS precio_promedio
FROM `categoria` c
LEFT JOIN `inmueble` i ON c.id_categoria = i.id_categoria AND i.estado = 'DISPONIBLE'
GROUP BY c.id_categoria, c.nombre;

SELECT 
    i.id_inmueble,
    i.titulo,
    ci.nombre AS ciudad,
    COUNT(v.id_visita) AS total_visitas
FROM `inmueble` i
INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
LEFT JOIN `visita` v ON i.id_inmueble = v.id_inmueble
GROUP BY i.id_inmueble, i.titulo, ci.nombre
ORDER BY total_visitas DESC;
