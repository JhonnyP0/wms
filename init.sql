CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    UNIQUE (product_id, location_id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'shipped', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO users (username, password_hash, email, is_admin) VALUES
('tomek', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'tomek@example.com', FALSE),
('janek', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'janek@example.com', FALSE),
('ania',  'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'ania@example.com', FALSE),
('piotr', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'piotr@example.com', FALSE),
('zofia', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'zofia@example.com', FALSE);

INSERT INTO products (name, sku, description) VALUES
('Wkretarka Bosch', 'WRK-BOSCH-01', 'Wkretarka akumulatorowa 18V'),
('Puszka 500ml', 'PUSZKA-500', 'Metalowa puszka 500 ml na plyny'),
('Folia stretch', 'FOLIA-STRETCH', 'Folia stretch 23um, 2kg, przezroczysta'),
('Kartony 30x30x30', 'KARTON-30', 'Kartony tekturowe, zestaw 10 sztuk'),
('Tasma pakowa', 'TASMA-PAK', 'Tasma do pakowania, brazowa, 48mm x 50m'),
('Karton A4', 'KARTON-A4', 'Karton formatu A4, bialy, 250g/m2'),
('Pojemnik plastikowy', 'POJ-PLAST', 'Pojemnik z uchwytem, 10L, przezroczysty'),
('Marker permanentny', 'MARKER-01', 'Czarny marker, wodoodporny'),
('Naklejki ostrzegawcze', 'NAKLEJKA-OSTR', 'Zestaw etykiet "Uwaga szklo"'),
('Etykiety termiczne', 'ETYK-TERM', 'Etykiety 1000 szt. rolka, 100x150mm'),
('Srubokret krzyzakowy', 'SRB-KRZYZ-01', 'Srubokret PH2 x 100mm'),
('Klucz nastawny', 'KLUCZ-NAST-01', 'Klucz nastawny 250mm'),
('Zestaw opasek kablowych', 'OPASKI-KAB--SET', 'Opaski kablowe, mix rozmiarow, 100 szt.'),
('Rekawice ochronne', 'REK-OCHR-M', 'Rekawice ochronne, rozmiar M'),
('Mlotek stolarski', 'MLT-STOL-01', 'Mlotek stolarski 500g'),
('Tasma miernicza', 'TASMA-MIERZ-5M', 'Tasma miernicza 5m'),
('Latarka LED', 'LATARKA-LED-MINI', 'Mini latarka LED, aluminiowa'),
('Opakowania babelkowe', 'OPAK-BABEL-10M', 'Folia babelkowa, rolka 10m'),
('Wypelniacz do paczek', 'WYPELNIACZ-50L', 'Wypelniacz do paczek, 50L worek'),
('Drukarka etykiet', 'DRUK-ETYK-BT', 'Drukarka etykiet termicznych Bluetooth'),
('Skaner kodow kreskowych', 'SKANER-USB-01', 'Skaner kodow kreskowych USB'),
('Paleta drewniana', 'PALETA-EUR-01', 'Standardowa paleta EUR'),
('Wozek transportowy', 'WOZEK-SKLAD-01', 'Wozek transportowy skladany'),
('Kask ochronny', 'KASK-OCHR-BIAL', 'Kask ochronny, bialy'),
('Okulary ochronne', 'OKULARY-OCHR-PRZ', 'Okulary ochronne, przezroczyste');

INSERT INTO locations (code) VALUES
('A1-01'), ('A1-02'), ('A1-03'), ('A1-04'), ('A1-05'), ('A1-06'),
('A2-01'), ('A2-02'), ('A2-03'), ('A2-04'), ('A2-05'), ('A2-06'),
('B1-01'), ('B1-02'), ('B1-03'), ('B1-04'), ('B1-05'), ('B1-06'),
('B2-01'), ('B2-02'), ('B2-03'), ('B2-04'), ('B2-05'), ('B2-06'),
('C1-01'), ('C1-02'), ('C1-03'), ('C1-04'), ('C1-05'), ('C1-06'),
('C2-01'), ('C2-02'), ('C2-03'), ('C2-04'), ('C2-05'), ('C2-06');

INSERT INTO inventory (product_id, location_id, quantity) VALUES
(1, (SELECT id FROM locations WHERE code = 'A1-01'), 30),
(11, (SELECT id FROM locations WHERE code = 'A1-01'), 15),
(2, (SELECT id FROM locations WHERE code = 'A1-02'), 100),
(12, (SELECT id FROM locations WHERE code = 'A1-02'), 10),
(3, (SELECT id FROM locations WHERE code = 'A1-03'), 60),
(18, (SELECT id FROM locations WHERE code = 'A1-03'), 5),
(4, (SELECT id FROM locations WHERE code = 'A1-04'), 45),
(19, (SELECT id FROM locations WHERE code = 'A1-04'), 2),
(5, (SELECT id FROM locations WHERE code = 'A1-05'), 75),
(13, (SELECT id FROM locations WHERE code = 'A1-05'), 200),
(6, (SELECT id FROM locations WHERE code = 'A1-06'), 40),
(8, (SELECT id FROM locations WHERE code = 'A1-06'), 100),

(7, (SELECT id FROM locations WHERE code = 'A2-01'), 20),
(15, (SELECT id FROM locations WHERE code = 'A2-01'), 8),
(9, (SELECT id FROM locations WHERE code = 'A2-02'), 90),
(10, (SELECT id FROM locations WHERE code = 'A2-02'), 70),
(1, (SELECT id FROM locations WHERE code = 'A2-03'), 10),
(4, (SELECT id FROM locations WHERE code = 'A2-03'), 20),
(2, (SELECT id FROM locations WHERE code = 'A2-04'), 25),
(5, (SELECT id FROM locations WHERE code = 'A2-04'), 15),
(3, (SELECT id FROM locations WHERE code = 'A2-05'), 35),
(7, (SELECT id FROM locations WHERE code = 'A2-05'), 10),
(6, (SELECT id FROM locations WHERE code = 'A2-06'), 50),
(9, (SELECT id FROM locations WHERE code = 'A2-06'), 40),

(14, (SELECT id FROM locations WHERE code = 'B1-01'), 50),
(17, (SELECT id FROM locations WHERE code = 'B1-01'), 25),
(20, (SELECT id FROM locations WHERE code = 'B1-02'), 1),
(21, (SELECT id FROM locations WHERE code = 'B1-02'), 1),
(22, (SELECT id FROM locations WHERE code = 'B1-03'), 10),
(23, (SELECT id FROM locations WHERE code = 'B1-03'), 3),
(24, (SELECT id FROM locations WHERE code = 'B1-04'), 5),
(25, (SELECT id FROM locations WHERE code = 'B1-04'), 30),
(11, (SELECT id FROM locations WHERE code = 'B1-05'), 20),
(12, (SELECT id FROM locations WHERE code = 'B1-05'), 5),
(13, (SELECT id FROM locations WHERE code = 'B1-06'), 100),
(16, (SELECT id FROM locations WHERE code = 'B1-06'), 30),

(14, (SELECT id FROM locations WHERE code = 'B2-01'), 25),
(15, (SELECT id FROM locations WHERE code = 'B2-01'), 3),
(17, (SELECT id FROM locations WHERE code = 'B2-02'), 15),
(18, (SELECT id FROM locations WHERE code = 'B2-02'), 2),
(19, (SELECT id FROM locations WHERE code = 'B2-03'), 1),
(20, (SELECT id FROM locations WHERE code = 'B2-03'), 1),
(21, (SELECT id FROM locations WHERE code = 'B2-04'), 1),
(22, (SELECT id FROM locations WHERE code = 'B2-04'), 5),
(23, (SELECT id FROM locations WHERE code = 'B2-05'), 1),
(24, (SELECT id FROM locations WHERE code = 'B2-05'), 2),
(25, (SELECT id FROM locations WHERE code = 'B2-06'), 10),
(1, (SELECT id FROM locations WHERE code = 'B2-06'), 5),

(2, (SELECT id FROM locations WHERE code = 'C1-01'), 50),
(3, (SELECT id FROM locations WHERE code = 'C1-01'), 20),
(4, (SELECT id FROM locations WHERE code = 'C1-02'), 30),
(5, (SELECT id FROM locations WHERE code = 'C1-02'), 40),
(6, (SELECT id FROM locations WHERE code = 'C1-03'), 25),
(7, (SELECT id FROM locations WHERE code = 'C1-03'), 15),
(8, (SELECT id FROM locations WHERE code = 'C1-04'), 60),
(9, (SELECT id FROM locations WHERE code = 'C1-04'), 30),
(10, (SELECT id FROM locations WHERE code = 'C1-05'), 45),
(11, (SELECT id FROM locations WHERE code = 'C1-05'), 10),
(12, (SELECT id FROM locations WHERE code = 'C1-06'), 8),
(13, (SELECT id FROM locations WHERE code = 'C1-06'), 70),

(14, (SELECT id FROM locations WHERE code = 'C2-01'), 15),
(15, (SELECT id FROM locations WHERE code = 'C2-01'), 2),
(16, (SELECT id FROM locations WHERE code = 'C2-02'), 20),
(17, (SELECT id FROM locations WHERE code = 'C2-02'), 10),
(18, (SELECT id FROM locations WHERE code = 'C2-03'), 3),
(19, (SELECT id FROM locations WHERE code = 'C2-03'), 1),
(20, (SELECT id FROM locations WHERE code = 'C2-04'), 1),
(21, (SELECT id FROM locations WHERE code = 'C2-04'), 1),
(22, (SELECT id FROM locations WHERE code = 'C2-05'), 8),
(23, (SELECT id FROM locations WHERE code = 'C2-05'), 2),
(24, (SELECT id FROM locations WHERE code = 'C2-06'), 3),
(25, (SELECT id FROM locations WHERE code = 'C2-06'), 20);

-- Wstawianie danych do tabeli orders
INSERT INTO orders (user_id, status) VALUES
(1, 'pending'),
(2, 'shipped'),
(3, 'cancelled'),
(1, 'shipped'),
(4, 'pending'),
(5, 'pending'),
(2, 'cancelled'),
(3, 'shipped'),
(4, 'shipped'),
(5, 'pending');

-- Wstawianie danych do tabeli order_items
INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 2), (1, 3, 5), (1, 5, 1);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(2, 2, 10), (2, 4, 3);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(3, 6, 7), (3, 7, 2), (3, 10, 4);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(4, 11, 1), (4, 12, 1), (4, 14, 10);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(5, 18, 1), (5, 19, 1), (5, 20, 1);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(6, 21, 1), (6, 22, 5), (6, 23, 1);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(7, 1, 5), (7, 8, 20);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(8, 10, 50), (8, 13, 100);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(9, 2, 5), (9, 15, 2);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(10, 16, 10), (10, 24, 1);
