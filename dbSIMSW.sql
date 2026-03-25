-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         11.8.5-MariaDB - MariaDB Server
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.11.0.7065
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para simsw
CREATE DATABASE IF NOT EXISTS `simsw` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `simsw`;

-- Volcando estructura para tabla simsw.analisis
CREATE TABLE IF NOT EXISTS `analisis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `tipo` enum('Estatico','Dinamico','Alteracion') DEFAULT NULL,
  `metodo` enum('Manual','Automatico') DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `resultado_global` int(11) DEFAULT NULL,
  `sitio_web_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sitio_web_id` (`sitio_web_id`),
  CONSTRAINT `sitio_web_id` FOREIGN KEY (`sitio_web_id`) REFERENCES `sitio_web` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=423 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla simsw.detalle_oz
CREATE TABLE IF NOT EXISTS `detalle_oz` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `endpoint` text DEFAULT NULL,
  `metodo` varchar(10) DEFAULT NULL,
  `parametro` varchar(255) DEFAULT NULL,
  `payload` text DEFAULT NULL,
  `informe_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `informe_id_unique` (`informe_id`),
  KEY `informe_id` (`informe_id`),
  CONSTRAINT `informe_id` FOREIGN KEY (`informe_id`) REFERENCES `informe` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla simsw.informe
CREATE TABLE IF NOT EXISTS `informe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `descripcion_humana` text DEFAULT NULL,
  `impacto` text DEFAULT NULL,
  `recomendacion` text DEFAULT NULL,
  `evidencia` text DEFAULT NULL,
  `severidad` int(11) NOT NULL,
  `codigo` text DEFAULT NULL,
  `alteracion_hash` varchar(64) DEFAULT NULL,
  `analisis_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `analisis_id` (`analisis_id`),
  CONSTRAINT `analisis_id` FOREIGN KEY (`analisis_id`) REFERENCES `analisis` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=409 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla simsw.mail
CREATE TABLE IF NOT EXISTS `mail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla simsw.sitio_mail
CREATE TABLE IF NOT EXISTS `sitio_mail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sitio_web_id` int(11) NOT NULL,
  `mail_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sitio_web_id_unique` (`sitio_web_id`,`mail_id`),
  KEY `sitio_web_id` (`sitio_web_id`),
  KEY `mail_id` (`mail_id`),
  CONSTRAINT `mail_sitio_id` FOREIGN KEY (`mail_id`) REFERENCES `mail` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `sitio_web_mail_id` FOREIGN KEY (`sitio_web_id`) REFERENCES `sitio_web` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla simsw.sitio_web
CREATE TABLE IF NOT EXISTS `sitio_web` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `url` varchar(2048) NOT NULL,
  `propietario` varchar(50) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_ultimo_monitoreo` datetime DEFAULT NULL,
  `frecuencia_monitoreo_minutos` int(11) NOT NULL DEFAULT 120,
  `archivos_base` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_ultimo_automatico` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla simsw.usuario
CREATE TABLE IF NOT EXISTS `usuario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- La exportación de datos fue deseleccionada.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
