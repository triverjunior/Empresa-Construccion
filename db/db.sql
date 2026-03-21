-- Crear base de datos
CREATE DATABASE IF NOT EXISTS construction_company;
USE construction_company;

-- Crear tabla de obras
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL
);

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'worker') NOT NULL,
    disponibility BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_project_id INT,
    FOREIGN KEY (assigned_project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Crear tabla de registros 
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    type ENUM('progress', 'problem') NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);