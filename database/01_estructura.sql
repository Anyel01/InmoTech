
CREATE DATABASE IF NOT EXISTS `inmotech_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `inmotech_db`;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `imagen_inmueble`;
DROP TABLE IF EXISTS `visita`;
DROP TABLE IF EXISTS `inmueble`;
DROP TABLE IF EXISTS `categoria`;
DROP TABLE IF EXISTS `ciudad`;
DROP TABLE IF EXISTS `departamento`;
DROP TABLE IF EXISTS `usuario`;
DROP TABLE IF EXISTS `rol`;

SET FOREIGN_KEY_CHECKS = 1;


CREATE TABLE `rol` (
    `id_rol` INT AUTO_INCREMENT PRIMARY KEY,
    `nombre` VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `usuario` (
    `id_usuario` INT AUTO_INCREMENT PRIMARY KEY,
    `nombre` VARCHAR(100) NOT NULL,
    `apellido` VARCHAR(100) NOT NULL,
    `correo` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `telefono` VARCHAR(20) NOT NULL,
    `id_rol` INT NOT NULL,
    `activo` TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT `chk_usuario_activo` CHECK (`activo` IN (0, 1)),
    CONSTRAINT `fk_usuario_rol`
        FOREIGN KEY (`id_rol`) REFERENCES `rol`(`id_rol`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE INDEX `idx_usuario_rol` ON `usuario`(`id_rol`);


CREATE TABLE `departamento` (
    `id_departamento` INT AUTO_INCREMENT PRIMARY KEY,
    `nombre` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `ciudad` (
    `id_ciudad` INT AUTO_INCREMENT PRIMARY KEY,
    `nombre` VARCHAR(100) NOT NULL,
    `id_departamento` INT NOT NULL,
    CONSTRAINT `fk_ciudad_departamento`
        FOREIGN KEY (`id_departamento`) REFERENCES `departamento`(`id_departamento`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_ciudad_departamento` ON `ciudad`(`id_departamento`);


CREATE TABLE `categoria` (
    `id_categoria` INT AUTO_INCREMENT PRIMARY KEY,
    `nombre` VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `inmueble` (
    `id_inmueble` INT AUTO_INCREMENT PRIMARY KEY,
    `titulo` VARCHAR(200) NOT NULL,
    `descripcion` TEXT NOT NULL,
    `direccion` VARCHAR(200) NOT NULL,
    `precio` DECIMAL(14, 2) NOT NULL,
    `area` DECIMAL(8, 2) NOT NULL,
    `habitaciones` INT NOT NULL DEFAULT 0,
    `banos` INT NOT NULL DEFAULT 0,
    `operacion` ENUM('VENTA', 'ARRIENDO') NOT NULL,
    `estado` ENUM('DISPONIBLE', 'NO_DISPONIBLE') NOT NULL DEFAULT 'DISPONIBLE',
    `id_categoria` INT NOT NULL,
    `id_ciudad` INT NOT NULL,
    `id_vendedor` INT NOT NULL,
    CONSTRAINT `chk_inmueble_precio` CHECK (`precio` > 0),
    CONSTRAINT `chk_inmueble_area` CHECK (`area` > 0),
    CONSTRAINT `chk_inmueble_habitaciones` CHECK (`habitaciones` >= 0),
    CONSTRAINT `chk_inmueble_banos` CHECK (`banos` >= 0),
    CONSTRAINT `fk_inmueble_categoria`
        FOREIGN KEY (`id_categoria`) REFERENCES `categoria`(`id_categoria`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT `fk_inmueble_ciudad`
        FOREIGN KEY (`id_ciudad`) REFERENCES `ciudad`(`id_ciudad`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT `fk_inmueble_vendedor`
        FOREIGN KEY (`id_vendedor`) REFERENCES `usuario`(`id_usuario`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_inmueble_estado` ON `inmueble`(`estado`);
CREATE INDEX `idx_inmueble_ciudad` ON `inmueble`(`id_ciudad`);
CREATE INDEX `idx_inmueble_categoria` ON `inmueble`(`id_categoria`);
CREATE INDEX `idx_inmueble_operacion` ON `inmueble`(`operacion`);
CREATE INDEX `idx_inmueble_precio` ON `inmueble`(`precio`);
CREATE INDEX `idx_inmueble_vendedor` ON `inmueble`(`id_vendedor`);


CREATE TABLE `visita` (
    `id_visita` INT AUTO_INCREMENT PRIMARY KEY,
    `fecha_visita` DATETIME NOT NULL,
    `mensaje` TEXT NULL,
    `estado` ENUM('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'REALIZADA') NOT NULL DEFAULT 'PENDIENTE',
    `id_inmueble` INT NOT NULL,
    `id_comprador` INT NOT NULL,
    CONSTRAINT `fk_visita_inmueble`
        FOREIGN KEY (`id_inmueble`) REFERENCES `inmueble`(`id_inmueble`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT `fk_visita_comprador`
        FOREIGN KEY (`id_comprador`) REFERENCES `usuario`(`id_usuario`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_visita_inmueble` ON `visita`(`id_inmueble`);
CREATE INDEX `idx_visita_comprador` ON `visita`(`id_comprador`);
CREATE INDEX `idx_visita_estado` ON `visita`(`estado`);
CREATE INDEX `idx_visita_fecha` ON `visita`(`fecha_visita`);

-- ------------------------------------------------------------------------------
-- 8. Tabla: imagen_inmueble
-- Fotos de cada inmueble. "ruta" es relativa a la carpeta static/ y "orden"
-- define la secuencia del carrusel (la primera, orden 1, es la portada).
-- Si se borra un inmueble sus fotos se borran con él (CASCADE).
-- ------------------------------------------------------------------------------
CREATE TABLE `imagen_inmueble` (
    `id_imagen` INT AUTO_INCREMENT PRIMARY KEY,
    `ruta` VARCHAR(255) NOT NULL,
    `descripcion` VARCHAR(200) NOT NULL DEFAULT '',
    `orden` INT NOT NULL DEFAULT 1,
    `id_inmueble` INT NOT NULL,
    CONSTRAINT `chk_imagen_orden` CHECK (`orden` >= 1),
    CONSTRAINT `fk_imagen_inmueble`
        FOREIGN KEY (`id_inmueble`) REFERENCES `inmueble`(`id_inmueble`)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_imagen_inmueble_orden` ON `imagen_inmueble`(`id_inmueble`, `orden`);
