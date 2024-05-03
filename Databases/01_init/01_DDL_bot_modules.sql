SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;
CREATE TABLE IF NOT EXISTS `bot_modules` (`module` varchar(255) NOT NULL,`state` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,PRIMARY KEY (`module`)) CHARSET = utf8;