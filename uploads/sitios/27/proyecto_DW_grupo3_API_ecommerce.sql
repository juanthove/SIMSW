-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         11.8.3-MariaDB - mariadb.org binary distribution
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


-- Volcando estructura de base de datos para api_e_market
CREATE DATABASE IF NOT EXISTS `api_e_market` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `api_e_market`;

-- Volcando estructura para tabla api_e_market.card_payment
CREATE TABLE IF NOT EXISTS `card_payment` (
  `id` int(11) NOT NULL,
  `number` varchar(50) NOT NULL DEFAULT '',
  `name_lastname` varchar(200) NOT NULL DEFAULT '',
  `expiration` char(7) NOT NULL DEFAULT '',
  `cvv` varchar(4) NOT NULL DEFAULT '',
  `installments` tinyint(4) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  CONSTRAINT `paymentCard` FOREIGN KEY (`id`) REFERENCES `payment_method` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.card_payment: ~1 rows (aproximadamente)
DELETE FROM `card_payment`;
INSERT INTO `card_payment` (`id`, `number`, `name_lastname`, `expiration`, `cvv`, `installments`) VALUES
	(12, '123456', 'Juan', '11/2026', '777', 2),
	(14, '76579832', 'Jose', '6/2028', '653', 1);

-- Volcando estructura para tabla api_e_market.cart
CREATE TABLE IF NOT EXISTS `cart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fee` decimal(5,2) NOT NULL DEFAULT 5.00,
  `department` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `street` varchar(100) DEFAULT NULL,
  `street_number` varchar(10) DEFAULT NULL,
  `corner` varchar(100) DEFAULT NULL,
  `additional_comments` varchar(100) DEFAULT NULL,
  `total_price` decimal(20,6) DEFAULT 5.000000,
  `user_id` int(11) NOT NULL,
  `payment_method_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `userCart` (`user_id`) USING BTREE,
  KEY `paymentCart` (`payment_method_id`) USING BTREE,
  CONSTRAINT `paymentCart` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `userCart` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.cart: ~3 rows (aproximadamente)
DELETE FROM `cart`;
INSERT INTO `cart` (`id`, `fee`, `department`, `city`, `street`, `street_number`, `corner`, `additional_comments`, `total_price`, `user_id`, `payment_method_id`) VALUES
	(8, 0.15, 'Colonia', 'Colonia del Sacramento', 'FJC', '14', 'Rai', 'Auto y 2 Play', 153523.000000, 32, 12),
	(9, 0.07, 'Soriano', 'Mercedes', 'LPS', '143', 'Publica', '', 9416.000000, 32, 13),
	(10, 0.07, 'Montevideo', 'Pocitos', 'Benito Blanco', '154', 'No', '', 2781.000000, 32, 14);

-- Volcando estructura para tabla api_e_market.cart_products
CREATE TABLE IF NOT EXISTS `cart_products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cart_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cart_product_cart` (`cart_id`),
  KEY `cart_product_product` (`product_id`),
  CONSTRAINT `cart_product_cart` FOREIGN KEY (`cart_id`) REFERENCES `cart` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `cart_product_product` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.cart_products: ~5 rows (aproximadamente)
DELETE FROM `cart_products`;
INSERT INTO `cart_products` (`id`, `cart_id`, `product_id`, `quantity`) VALUES
	(2, 8, 50921, 1),
	(3, 8, 50743, 2),
	(4, 9, 50741, 2),
	(5, 9, 60801, 1),
	(6, 10, 40281, 1);

-- Volcando estructura para tabla api_e_market.category
CREATE TABLE IF NOT EXISTS `category` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(100) NOT NULL,
  `product_count` int(11) NOT NULL DEFAULT 0,
  `imgSrc` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.category: ~9 rows (aproximadamente)
DELETE FROM `category`;
INSERT INTO `category` (`id`, `name`, `description`, `product_count`, `imgSrc`) VALUES
	(101, 'Autos', 'Los mejores precios en autos 0 kilómetro, de alta y media gama.', 5, 'img/cat101_1.jpg'),
	(102, 'Juguetes', 'Encuentra aquí los mejores precios para niños/as de cualquier edad.', 4, 'img/cat102_1.jpg'),
	(103, 'Muebles', 'Muebles antiguos, nuevos y para ser armados por uno mismo.', 4, 'img/cat103_1.jpg'),
	(104, 'Herramientas', 'Herramientas para cualquier tipo de trabajo.', 0, 'img/cat104_1.jpg'),
	(105, 'Computadoras', 'Todo en cuanto a computadoras, para uso de oficina y/o juegos.', 1, 'img/cat105_1.jpg'),
	(106, 'Vestimenta', 'Gran variedad de ropa, nueva y de segunda mano.', 0, 'img/cat106_1.jpg'),
	(107, 'Electrodomésticos', 'Todos los electrodomésticos modernos y de bajo consumo.', 0, 'img/cat107_1.jpg'),
	(108, 'Deporte', 'Toda la variedad de indumentaria para todo tipo de deporte.', 0, 'img/cat108_1.jpg'),
	(109, 'Celulares', 'Celulares de todo tipo para cubrir todas las necesidades.', 0, 'img/cat109_1.jpg');

-- Volcando estructura para tabla api_e_market.comments
CREATE TABLE IF NOT EXISTS `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `score` int(11) NOT NULL DEFAULT 0,
  `description` varchar(200) NOT NULL DEFAULT '0',
  `dateTime` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `productComment` (`product_id`) USING BTREE,
  KEY `userComment` (`user_id`) USING BTREE,
  CONSTRAINT `productComment` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `userComment` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.comments: ~31 rows (aproximadamente)
DELETE FROM `comments`;
INSERT INTO `comments` (`id`, `score`, `description`, `dateTime`, `user_id`, `product_id`) VALUES
	(1, 5, 'Precioso, a mi nena le encantó', '2021-02-20 14:00:42', 1, 50741),
	(2, 4, 'Esperaba que fuera más grande, pero es muy lindo.', '2021-01-11 16:26:10', 2, 50741),
	(3, 5, 'Hermoso el oso. Quedamos encantados, lo recomiendo.', '2020-12-16 19:55:19', 3, 50741),
	(4, 1, 'Se lo regalé a mi novia para que me perdone, pero no funcionó', '2020-02-14 23:19:09', 4, 50741),
	(5, 5, 'Perfecta. La que me recomendó el entrenador', '2022-05-21 23:10:41', 5, 50742),
	(6, 4, 'Es lo que esperaba. Ahora a entrenar mucho!', '2021-10-30 06:33:53', 6, 50742),
	(7, 5, 'Muy buena calidad.', '2020-11-02 09:28:45', 7, 50742),
	(8, 5, 'Excelente. Para rememorar viejos tiempos y volver a sentirse un campeón.', '2019-11-09 21:15:29', 8, 50742),
	(9, 5, 'Un lujo. Se la compré a mis hijos, pero creo que me la quedo yo.', '2022-04-18 13:20:56', 9, 50743),
	(10, 5, 'Increibles los gráficos que tiene.', '2022-04-05 11:20:09', 10, 50743),
	(11, 5, 'IM PRE SIO NAN TE.', '2022-03-21 22:38:39', 11, 50743),
	(12, 5, 'Me cuesta creer lo que han avanzado las consolas', '2022-01-04 11:16:48', 12, 50743),
	(13, 5, 'Compra de último momento para la navidad. A mi nieto le gustó.', '2021-12-24 23:59:59', 13, 50744),
	(14, 2, 'Les pedí azul y me mandaron verde. La bicicleta es buena', '2021-09-15 01:27:19', 14, 50744),
	(15, 3, 'Es buena, pero le faltaron las rueditas.', '2021-03-24 20:11:19', 15, 50744),
	(16, 4, 'Perfecta para que mis hijos vayan empezando a practicar.', '2021-01-18 05:22:50', 16, 50744),
	(17, 3, 'Ya llevo un año con este auto y la verdad que tiene sus ventajas y desventajas', '2020-02-25 18:03:52', 17, 50921),
	(18, 5, 'Es un auto muy cómodo y en relación precio/calidad vale la pena!', '2020-01-17 13:42:18', 18, 50921),
	(19, 4, 'Casi todo bien!, excepto por algún detalle de gusto personal', '2020-03-14 09:05:13', 19, 50921),
	(20, 5, 'Un espectáculo el auto!', '2020-02-21 15:05:22', 20, 50921),
	(21, 3, 'Es un buen auto, pero el precio me pareció algo elevado', '2022-04-05 15:29:40', 21, 50922),
	(22, 5, 'Muy buen auto, vale cada centavo', '2021-11-15 19:32:10', 22, 50922),
	(23, 5, 'Me gusta como se comporta en tierra y pista', '2020-02-21 15:05:22', 23, 50922),
	(24, 5, 'Gran opción. Bueno, bonito y barato', '2022-02-15 20:19:20', 24, 50923),
	(25, 4, 'No había el color que yo quería, pero lo demás está perfecto.', '2021-05-24 19:25:43', 25, 50923),
	(26, 5, 'Lo que busco cuando no compito', '2020-12-03 14:15:33', 26, 50923),
	(27, 5, 'Espectacular. Sport con potencia y confort.', '2022-06-24 20:19:20', 27, 50924),
	(28, 3, 'Es algo chico, pero está bien para una familia pequeña.', '2021-12-02 11:23:32', 28, 60801),
	(29, 4, 'Muy cómodo. Ideal para las siestas', '2022-03-29 09:15:01', 29, 60802),
	(30, 5, 'Lo compré para ver los partidos con mis amigos. Valió la pena.', '2021-08-09 22:05:12', 30, 60802),
	(31, 5, 'Es grande. Entra más de lo que parece', '2022-11-21 03:33:41', 31, 60803);

-- Volcando estructura para tabla api_e_market.payment_method
CREATE TABLE IF NOT EXISTS `payment_method` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('Tarjeta','Transferencia') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.payment_method: ~2 rows (aproximadamente)
DELETE FROM `payment_method`;
INSERT INTO `payment_method` (`id`, `type`) VALUES
	(12, 'Tarjeta'),
	(13, 'Transferencia'),
	(14, 'Tarjeta');

-- Volcando estructura para tabla api_e_market.product
CREATE TABLE IF NOT EXISTS `product` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL DEFAULT '',
  `cost` int(11) NOT NULL DEFAULT 0,
  `currency` enum('USD','UYU') NOT NULL,
  `sold_count` int(11) NOT NULL DEFAULT 0,
  `category_id` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `categoryProduct` (`category_id`) USING BTREE,
  CONSTRAINT `categoryProduct` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.product: ~14 rows (aproximadamente)
DELETE FROM `product`;
INSERT INTO `product` (`id`, `name`, `description`, `cost`, `currency`, `sold_count`, `category_id`) VALUES
	(40281, 'Computadora de escritorio', 'Computadora de escritorio. Potencia y rendimiento, para juegos o trabajo', 2599, 'USD', 11, 105),
	(50741, 'Oso de peluche', 'Oso de peluche gigante, con el bebé. Resistente y lavable. Tus hijos los amarán', 2400, 'UYU', 97, 102),
	(50742, 'Pelota de básquetbol', 'Balón de baloncesto profesional, para interiores, tamaño 5, 27.5 pulgadas. Oficial de la NBA', 2999, 'UYU', 11, 102),
	(50743, 'PlayStation 5', 'Maravíllate con increíbles gráficos y disfruta de nuevas funciones de PS5. Con E/S integrada.', 59999, 'UYU', 16, 102),
	(50744, 'Bicicleta', '¡La mejor BMX pequeña del mercado! Frenos traseros y cuadro duradero de acero Hi-Ten.', 10999, 'UYU', 8, 102),
	(50921, 'Chevrolet Onix Joy', 'Generación 2019, variedad de colores. Motor 1.0, ideal para ciudad.', 13500, 'USD', 14, 101),
	(50922, 'Fiat Way', 'La versión de Fiat que brinda confort y a un precio accesible.', 14500, 'USD', 52, 101),
	(50923, 'Suzuki Celerio', 'Un auto que se ha ganado la buena fama por su economía con el combustible.', 12500, 'USD', 25, 101),
	(50924, 'Peugeot 208', 'El modelo de auto que se sigue renovando y manteniendo su prestigio en comodidad.', 15200, 'USD', 17, 101),
	(50925, 'Bugatti Chiron', 'El mejor hiperdeportivo de mundo. Producción limitada a 500 unidades.', 3500000, 'USD', 0, 101),
	(60801, 'Juego de comedor', 'Un conjunto sencillo y sólido, ideal para zonas de comedor pequeñas, hecho en madera maciza de pino', 4000, 'UYU', 88, 103),
	(60802, 'Sofá', 'Cómodo sofá de tres cuerpos, con chaiselongue intercambiable. Ideal para las siestas', 24000, 'UYU', 12, 103),
	(60803, 'Armario', 'Diseño clásico con puertas con forma de panel. Espejo de cuerpo entero para ver cómo te queda la ropa', 8000, 'UYU', 24, 103),
	(60804, 'Mesa de centro', 'Añade más funciones a tu sala de estar, ya que te permite cambiar fácilmente de actividad.', 10000, 'UYU', 37, 103);

-- Volcando estructura para tabla api_e_market.product_images
CREATE TABLE IF NOT EXISTS `product_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(50) NOT NULL,
  `product_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `product` (`product_id`) USING BTREE,
  CONSTRAINT `product` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.product_images: ~56 rows (aproximadamente)
DELETE FROM `product_images`;
INSERT INTO `product_images` (`id`, `url`, `product_id`) VALUES
	(1, 'img/prod40281_1.jpg', 40281),
	(2, 'img/prod40281_2.jpg', 40281),
	(3, 'img/prod40281_3.jpg', 40281),
	(4, 'img/prod40281_4.jpg', 40281),
	(5, 'img/prod50741_1.jpg', 50741),
	(6, 'img/prod50741_2.jpg', 50741),
	(7, 'img/prod50741_3.jpg', 50741),
	(8, 'img/prod50741_4.jpg', 50741),
	(9, 'img/prod50742_1.jpg', 50742),
	(10, 'img/prod50742_2.jpg', 50742),
	(11, 'img/prod50742_3.jpg', 50742),
	(12, 'img/prod50742_4.jpg', 50742),
	(13, 'img/prod50743_1.jpg', 50743),
	(14, 'img/prod50743_2.jpg', 50743),
	(15, 'img/prod50743_3.jpg', 50743),
	(16, 'img/prod50743_4.jpg', 50743),
	(17, 'img/prod50744_1.jpg', 50744),
	(18, 'img/prod50744_2.jpg', 50744),
	(19, 'img/prod50744_3.jpg', 50744),
	(20, 'img/prod50744_4.jpg', 50744),
	(21, 'img/prod50921_1.jpg', 50921),
	(22, 'img/prod50921_2.jpg', 50921),
	(23, 'img/prod50921_3.jpg', 50921),
	(24, 'img/prod50921_4.jpg', 50921),
	(25, 'img/prod50922_1.jpg', 50922),
	(26, 'img/prod50922_2.jpg', 50922),
	(27, 'img/prod50922_3.jpg', 50922),
	(28, 'img/prod50922_4.jpg', 50922),
	(29, 'img/prod50923_1.jpg', 50923),
	(30, 'img/prod50923_2.jpg', 50923),
	(31, 'img/prod50923_3.jpg', 50923),
	(32, 'img/prod50923_4.jpg', 50923),
	(33, 'img/prod50924_1.jpg', 50924),
	(34, 'img/prod50924_2.jpg', 50924),
	(35, 'img/prod50924_3.jpg', 50924),
	(36, 'img/prod50924_4.jpg', 50924),
	(37, 'img/prod50925_1.jpg', 50925),
	(38, 'img/prod50925_2.jpg', 50925),
	(39, 'img/prod50925_3.jpg', 50925),
	(40, 'img/prod50925_4.jpg', 50925),
	(41, 'img/prod60801_1.jpg', 60801),
	(42, 'img/prod60801_2.jpg', 60801),
	(43, 'img/prod60801_3.jpg', 60801),
	(44, 'img/prod60801_4.jpg', 60801),
	(45, 'img/prod60802_1.jpg', 60802),
	(46, 'img/prod60802_2.jpg', 60802),
	(47, 'img/prod60802_3.jpg', 60802),
	(48, 'img/prod60802_4.jpg', 60802),
	(49, 'img/prod60803_1.jpg', 60803),
	(50, 'img/prod60803_2.jpg', 60803),
	(51, 'img/prod60803_3.jpg', 60803),
	(52, 'img/prod60803_4.jpg', 60803),
	(53, 'img/prod60804_1.jpg', 60804),
	(54, 'img/prod60804_2.jpg', 60804),
	(55, 'img/prod60804_3.jpg', 60804),
	(56, 'img/prod60804_4.jpg', 60804);

-- Volcando estructura para tabla api_e_market.related_products
CREATE TABLE IF NOT EXISTS `related_products` (
  `product_id_base` int(11) NOT NULL,
  `product_id_related` int(11) NOT NULL,
  PRIMARY KEY (`product_id_base`,`product_id_related`) USING BTREE,
  KEY `productRelated` (`product_id_related`) USING BTREE,
  KEY `productBase` (`product_id_base`),
  CONSTRAINT `productBase` FOREIGN KEY (`product_id_base`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `productRelated` FOREIGN KEY (`product_id_related`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.related_products: ~28 rows (aproximadamente)
DELETE FROM `related_products`;
INSERT INTO `related_products` (`product_id_base`, `product_id_related`) VALUES
	(40281, 50743),
	(40281, 50744),
	(50741, 50742),
	(50741, 50744),
	(50742, 50741),
	(50742, 50743),
	(50743, 50742),
	(50743, 50744),
	(50744, 50741),
	(50744, 50743),
	(50921, 50922),
	(50921, 50924),
	(50922, 50921),
	(50922, 50923),
	(50923, 50922),
	(50923, 50924),
	(50924, 50921),
	(50924, 50923),
	(50925, 50921),
	(50925, 50924),
	(60801, 60802),
	(60801, 60804),
	(60802, 60801),
	(60802, 60803),
	(60803, 60802),
	(60803, 60804),
	(60804, 60801),
	(60804, 60803);

-- Volcando estructura para tabla api_e_market.transfer_payment
CREATE TABLE IF NOT EXISTS `transfer_payment` (
  `id` int(11) NOT NULL,
  `image` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `paymentTransfer` FOREIGN KEY (`id`) REFERENCES `payment_method` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.transfer_payment: ~1 rows (aproximadamente)
DELETE FROM `transfer_payment`;
INSERT INTO `transfer_payment` (`id`, `image`) VALUES
	(13, 'Calendario_Fase_2_-_DESARROLLO_WEB_2025_1.pdf');

-- Volcando estructura para tabla api_e_market.user
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL DEFAULT '0',
  `lastname` varchar(50) NOT NULL DEFAULT '0',
  `email` varchar(200) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `image` varchar(200) DEFAULT NULL,
  `user` varchar(200) NOT NULL,
  `password` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla api_e_market.user: ~33 rows (aproximadamente)
DELETE FROM `user`;
INSERT INTO `user` (`id`, `name`, `lastname`, `email`, `phone`, `image`, `user`, `password`) VALUES
	(1, 'Silvia', 'Fagundez', NULL, NULL, NULL, 'silvia_fagundez', NULL),
	(2, 'Majo', 'Sanchez', NULL, NULL, NULL, 'majo_sanchez', NULL),
	(3, 'Raul', 'Añez', NULL, NULL, NULL, 'raul_añez', NULL),
	(4, 'Flynn', 'Rider', NULL, NULL, NULL, 'flynn_rider', NULL),
	(5, 'Karen', 'Gonzalez', NULL, NULL, NULL, 'karen_gonzalez', NULL),
	(6, 'Luis', 'Salgueiro', NULL, NULL, NULL, 'luis_salgueiro', NULL),
	(7, 'Carlos', 'Diaz', NULL, NULL, NULL, 'carlos_diaz', NULL),
	(8, 'Scottie', 'Pippen', NULL, NULL, NULL, 'scottie_pippen', NULL),
	(9, 'Saul', 'Dominguez', NULL, NULL, NULL, 'saul_dominguez', NULL),
	(10, 'Lucia', 'Ralek', NULL, NULL, NULL, 'lucia_ralek', NULL),
	(11, 'Mateo', 'Diestre', NULL, NULL, NULL, 'mateo_diestre', NULL),
	(12, 'Ralph', 'Baer', NULL, NULL, NULL, 'ralph_baer', NULL),
	(13, 'Ignacio', 'Paremon', NULL, NULL, NULL, 'ignacio_paremon', NULL),
	(14, 'Mia', 'Barboza', NULL, NULL, NULL, 'mia_barboza', NULL),
	(15, 'Julian', 'Surech', NULL, NULL, NULL, 'julian_surech', NULL),
	(16, 'Mariana', 'Pajon', NULL, NULL, NULL, 'mariana_pajon', NULL),
	(17, 'Juan', 'Pedro', NULL, NULL, NULL, 'juan_pedro', NULL),
	(18, 'Maria', 'Sanchez', NULL, NULL, NULL, 'maria_sanchez', NULL),
	(19, 'Paola', 'Perez', NULL, NULL, NULL, 'paola_perez', NULL),
	(20, 'Gustavo', 'Trelles', NULL, NULL, NULL, 'gustavo_trelles', NULL),
	(21, 'Ema', 'Perez', NULL, NULL, NULL, 'ema_perez', NULL),
	(22, 'Javier', 'Santoalla', NULL, NULL, NULL, 'javier_santoalla', NULL),
	(23, 'Gonza', 'Rodriguez', NULL, NULL, NULL, 'gonza_rodriguez', NULL),
	(24, 'Alfredo', 'Bioy', NULL, NULL, NULL, 'alfredo_bioy', NULL),
	(25, 'Pablo', 'Cibeles', NULL, NULL, NULL, 'pablo_cibeles', NULL),
	(26, 'Santiago', 'Urrutia', NULL, NULL, NULL, 'santiago_urrutia', NULL),
	(27, 'Maite', 'Caceres', NULL, NULL, NULL, 'maite_caceres', NULL),
	(28, 'Jaime', 'Gil', NULL, NULL, NULL, 'jaime_gil', NULL),
	(29, 'Ximena', 'Fagundez', NULL, NULL, NULL, 'ximena_fagundez', NULL),
	(30, 'Marcelo', 'Sosa', NULL, NULL, NULL, 'marcelo_sosa', NULL),
	(31, 'Bruno', 'Diaz', NULL, NULL, NULL, 'bruno_diaz', NULL),
	(32, 'usuario', 'ejemplo', NULL, NULL, NULL, 'usuario@ejemplo.com', 'password'),
	(33, 'admin', 'ecommerce', NULL, NULL, NULL, 'admin@ecommerce.com', 'password');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
