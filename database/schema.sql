-- =========================================================
-- SaxManager - Esquema de la base de datos (SQLite)
-- Tienda y taller de saxofones
-- =========================================================

PRAGMA foreign_keys = ON;

-- Marcas de saxofones (Yamaha, Selmer, Yanagisawa...)
CREATE TABLE IF NOT EXISTS marcas (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT    NOT NULL UNIQUE,
    pais    TEXT
);

-- Inventario de saxofones. Cada saxofón pertenece a UNA marca (1:N)
CREATE TABLE IF NOT EXISTS saxofones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    marca_id      INTEGER NOT NULL,
    modelo        TEXT    NOT NULL,
    tipo          TEXT    NOT NULL CHECK (tipo IN ('Soprano', 'Alto', 'Tenor', 'Barítono')),
    numero_serie  TEXT    NOT NULL UNIQUE,
    acabado       TEXT,
    anio          INTEGER,
    precio        REAL    NOT NULL CHECK (precio >= 0),
    estado        TEXT    NOT NULL DEFAULT 'Disponible'
                  CHECK (estado IN ('Disponible', 'Reservado', 'En mantenimiento', 'Vendido')),
    FOREIGN KEY (marca_id) REFERENCES marcas(id) ON DELETE RESTRICT
);

-- Clientes de la tienda / dueños de instrumentos que llegan al taller
CREATE TABLE IF NOT EXISTS clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL,
    telefono  TEXT,
    correo    TEXT
);

-- Servicios de taller. Relaciona un saxofón con un cliente (N:1 con cada uno)
CREATE TABLE IF NOT EXISTS mantenimientos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    saxofon_id   INTEGER NOT NULL,
    cliente_id   INTEGER NOT NULL,
    fecha        TEXT    NOT NULL,          -- formato AAAA-MM-DD
    descripcion  TEXT    NOT NULL,
    costo        REAL    NOT NULL DEFAULT 0 CHECK (costo >= 0),
    estado       TEXT    NOT NULL DEFAULT 'Pendiente'
                 CHECK (estado IN ('Pendiente', 'En proceso', 'Terminado')),
    FOREIGN KEY (saxofon_id) REFERENCES saxofones(id) ON DELETE CASCADE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)  ON DELETE RESTRICT
);
