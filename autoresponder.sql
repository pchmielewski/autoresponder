CREATE TABLE IF NOT EXISTS `postfix_autoresponder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(512) CHARACTER SET utf8 NOT NULL,
  `from` datetime NOT NULL,
  `to` datetime NOT NULL,
  `message` text COLLATE utf8_polish_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

INSERT INTO  `postfix`.`postfix_transport` (
`id` ,
`domain` ,
`destination`
)
VALUES (
NULL ,  'autoresponder.yourdomain.com',  'autoresponder'
)