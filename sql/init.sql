-- 1. Crea il Database (se non esiste)
CREATE DATABASE IF NOT EXISTS dbUsers;
CREATE DATABASE IF NOT EXISTS data_db; -- Manteniamo anche il secondo DB per il progetto

-- 2. Seleziona il database dbUsers per lavorarci dentro
USE dbUsers;

-- 3. Crea la tabella 'user' con la struttura richiesta
CREATE TABLE IF NOT EXISTS user (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(100),
    surname VARCHAR(100),
    age INT
);

-- (Opzionale) Inserisci un utente di prova
INSERT INTO user (email, name, surname, age) VALUES ('test@example.com', 'Mario', 'Rossi', 30);