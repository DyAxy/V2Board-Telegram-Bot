SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;
CREATE TABLE IF NOT EXISTS `bot_modules_notify` (`id` int(11) NOT NULL AUTO_INCREMENT,`order_id` int(11) NOT NULL,`type` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1订单 99定制',`state` tinyint(1) NOT NULL DEFAULT '0' COMMENT '-2旧数据 -1无需推送消息 0未推送消息 1已推送消息',PRIMARY KEY (`id`)) ENGINE = InnoDB DEFAULT CHARSET = utf8;