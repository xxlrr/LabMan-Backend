CREATE DATABASE labman;
USE labman;

CREATE TABLE users (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       username VARCHAR(255) NOT NULL UNIQUE,
                       email VARCHAR(255) UNIQUE,
                       password_hash VARCHAR(255) NOT NULL,
                       role ENUM('User', 'Manager') NOT NULL,
                       firstname VARCHAR(255),
                       lastname VARCHAR(255)
);