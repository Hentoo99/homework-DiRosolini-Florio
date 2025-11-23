CREATE DATABASE IF NOT EXISTS user_db;
CREATE DATABASE IF NOT EXISTS data_db;


USE user_db;

CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255)
);

INSERT INTO users (email, name, surname) VALUES ('mario@example.com', 'Mario', "Guerrera");