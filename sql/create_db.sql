-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema social
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `social` ;

-- -----------------------------------------------------
-- Schema social
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `social` DEFAULT CHARACTER SET utf8 ;
USE `social` ;

-- -----------------------------------------------------
-- Table `social`.`accounts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `social`.`accounts` ;

CREATE TABLE IF NOT EXISTS `social`.`accounts` (
  `id_account` CHAR(16) NOT NULL,
  `salt` CHAR(16) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `username` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`id_account`),
  UNIQUE INDEX `login_UNIQUE` (`username` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `social`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `social`.`users` ;

CREATE TABLE IF NOT EXISTS `social`.`users` (
  `id_account` CHAR(16) NOT NULL,
  `name` VARCHAR(64) NULL,
  `surname` VARCHAR(64) NULL,
  `patronymic` VARCHAR(64) NULL,
  `birthday` DATE NULL,
  `sex` CHAR(1) NULL,
  `interests` TEXT NULL,
  `city` VARCHAR(128) NULL,
  CONSTRAINT `account`
    FOREIGN KEY (`id_account`)
    REFERENCES `social`.`accounts` (`id_account`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
