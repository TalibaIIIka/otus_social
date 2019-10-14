CREATE TABLE IF NOT EXISTS `accounts` (
  `id_account` BIGINT(20) unsigned NOT NULL AUTO_INCREMENT,
  `salt` CHAR(32) NOT NULL,
  `password_hash` CHAR(128) NOT NULL,
  `username` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`id_account`),
  UNIQUE INDEX `login_UNIQUE` (`username` ASC))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `users` (
  `id_account` BIGINT(20) unsigned NOT NULL,
  `name` VARCHAR(64) NULL,
  `surname` VARCHAR(64) NULL,
  `patronymic` VARCHAR(64) NULL,
  `birthday` DATE NULL,
  `sex` CHAR(1) NULL,
  `interests` TEXT NULL,
  `city` VARCHAR(128) NULL,
  CONSTRAINT `account`
    FOREIGN KEY (`id_account`)
    REFERENCES `accounts` (`id_account`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
