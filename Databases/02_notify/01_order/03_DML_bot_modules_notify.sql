SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;
INSERT INTO bot_modules_notify (`order_id`,`type`,`state`) SELECT `id`,1,-2 FROM v2_order WHERE NOT EXISTS(SELECT order_id from bot_modules_notify where bot_modules_notify.order_id=v2_order.id AND bot_modules_notify.type=1) ORDER BY `id` ASC