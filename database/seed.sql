-- Datos de ejemplo para probar el sistema

INSERT INTO marcas (nombre, pais) VALUES
    ('Yamaha',      'Japón'),
    ('Selmer',      'Francia'),
    ('Yanagisawa',  'Japón'),
    ('Jupiter',     'Taiwán'),
    ('Keilwerth',   'Alemania');

INSERT INTO saxofones (marca_id, modelo, tipo, numero_serie, acabado, anio, precio, estado) VALUES
    (1, 'YAS-280',          'Alto',     'YA-100231', 'Laca dorada',  2022,  950.00, 'Disponible'),
    (1, 'YTS-62',           'Tenor',    'YT-554120', 'Laca dorada',  2019, 2800.00, 'En mantenimiento'),
    (2, 'Supreme',          'Alto',     'SE-889012', 'Laca oscura',  2023, 7200.00, 'Disponible'),
    (2, 'Mark VI',          'Tenor',    'SE-112345', 'Laca original',1965, 15000.00,'Reservado'),
    (3, 'S-WO10',           'Soprano',  'YN-334455', 'Laca dorada',  2021, 3900.00, 'Disponible'),
    (4, 'JAS-500',          'Alto',     'JP-778899', 'Laca dorada',  2020,  650.00, 'Vendido'),
    (5, 'SX90R Shadow',     'Tenor',    'KW-445566', 'Negro níquel', 2018, 6100.00, 'Disponible'),
    (1, 'YBS-480',          'Barítono', 'YB-221100', 'Laca dorada',  2021, 5400.00, 'Disponible');

INSERT INTO clientes (nombre, telefono, correo) VALUES
    ('María Fernández', '8888-1234', 'maria.f@correo.com'),
    ('José Ramírez',    '8777-4321', 'jramirez@correo.com'),
    ('Escuela de Música Municipal', '2222-5555', 'info@musicamunicipal.cr');

INSERT INTO mantenimientos (saxofon_id, cliente_id, fecha, descripcion, costo, estado) VALUES
    (2, 1, '2026-10-20', 'Cambio de zapatillas y ajuste de mecanismo', 120.00, 'En proceso'),
    (5, 2, '2026-09-15', 'Limpieza general y lubricación',              45.00, 'Terminado'),
    (1, 3, '2026-10-27', 'Revisión de fugas en la campana',             30.00, 'Pendiente');
