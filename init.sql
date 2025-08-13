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
    description TEXT,
    barcode_image_path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    location_barcode_path VARCHAR(255)
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

CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    shipment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE IF NOT EXISTS shipment_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id INT NOT NULL,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS receives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    receives_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE IF NOT EXISTS receives_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receive_id INT NOT NULL,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (receive_id) REFERENCES receives(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

INSERT INTO users (username, password_hash, email, is_admin) VALUES
('tomek', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'tomek@example.com', FALSE),
('janek', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'janek@example.com', FALSE),
('ania',  'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'ania@example.com', FALSE),
('piotr', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'piotr@example.com', FALSE),
('zofia', 'pbkdf2:sha256:260000$rXm0pQ5sT2u1vW3x$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c', 'zofia@example.com', FALSE);

INSERT INTO products (name, sku, description, barcode_image_path) VALUES
('Wkretarka Bosch', 'WRK-BOSCH-01', 'Wkretarka akumulatorowa 18V', 'static/barcodes/WRK-BOSCH-01.png'),
('Puszka 500ml', 'PUSZKA-500', 'Metalowa puszka 500 ml na plyny', 'static/barcodes/PUSZKA-500.png'),
('Folia stretch', 'FOLIA-STRETCH', 'Folia stretch 23um, 2kg, przezroczysta', 'static/barcodes/FOLIA-STRETCH.png'),
('Kartony 30x30x30', 'KARTON-30', 'Kartony tekturowe, zestaw 10 sztuk', 'static/barcodes/KARTON-30.png'),
('Tasma pakowa', 'TASMA-PAK', 'Tasma do pakowania, brazowa, 48mm x 50m', 'static/barcodes/TASMA-PAK.png'),
('Karton A4', 'KARTON-A4', 'Karton formatu A4, bialy, 250g/m2', 'static/barcodes/KARTON-A4.png'),
('Pojemnik plastikowy', 'POJ-PLAST', 'Pojemnik z uchwytem, 10L, przezroczysty', 'static/barcodes/POJ-PLAST.png'),
('Marker permanentny', 'MARKER-01', 'Czarny marker, wodoodporny', 'static/barcodes/MARKER-01.png'),
('Naklejki ostrzegawcze', 'NAKLEJKA-OSTR', 'Zestaw etykiet "Uwaga szklo"', 'static/barcodes/NAKLEJKA-OSTR.png'),
('Etykiety termiczne', 'ETYK-TERM', 'Etykiety 1000 szt. rolka, 100x150mm', 'static/barcodes/ETYK-TERM.png'),
('Srubokret krzyzakowy', 'SRB-KRZYZ-01', 'Srubokret PH2 x 100mm', 'static/barcodes/SRB-KRZYZ-01.png'),
('Klucz nastawny', 'KLUCZ-NAST-01', 'Klucz nastawny 250mm', 'static/barcodes/KLUCZ-NAST-01.png'),
('Zestaw opasek kablowych', 'OPASKI-KAB--SET', 'Opaski kablowe, mix rozmiarow, 100 szt.', 'static/barcodes/OPASKI-KAB--SET.png'),
('Rekawice ochronne', 'REK-OCHR-M', 'Rekawice ochronne, rozmiar M', 'static/barcodes/REK-OCHR-M.png'),
('Mlotek stolarski', 'MLT-STOL-01', 'Mlotek stolarski 500g', 'static/barcodes/MLT-STOL-01.png'),
('Tasma miernicza', 'TASMA-MIERZ-5M', 'Tasma miernicza 5m', 'static/barcodes/TASMA-MIERZ-5M.png'),
('Latarka LED', 'LATARKA-LED-MINI', 'Mini latarka LED, aluminiowa', 'static/barcodes/LATARKA-LED-MINI.png'),
('Opakowania babelkowe', 'OPAK-BABEL-10M', 'Folia babelkowa, rolka 10m', 'static/barcodes/OPAK-BABEL-10M.png'),
('Wypelniacz do paczek', 'WYPELNIACZ-50L', 'Wypelniacz do paczek, 50L worek', 'static/barcodes/WYPELNIACZ-50L.png'),
('Drukarka etykiet', 'DRUK-ETYK-BT', 'Drukarka etykiet termicznych Bluetooth', 'static/barcodes/DRUK-ETYK-BT.png'),
('Skaner kodow kreskowych', 'SKANER-USB-01', 'Skaner kodow kreskowych USB', 'static/barcodes/SKANER-USB-01.png'),
('Paleta drewniana', 'PALETA-EUR-01', 'Standardowa paleta EUR', 'static/barcodes/PALETA-EUR-01.png'),
('Wozek transportowy', 'WOZEK-SKLAD-01', 'Wozek transportowy skladany', 'static/barcodes/WOZEK-SKLAD-01.png'),
('Kask ochronny', 'KASK-OCHR-BIAL', 'Kask ochronny, bialy', 'static/barcodes/KASK-OCHR-BIAL.png'),
('Okulary ochronne', 'OKULARY-OCHR-PRZ', 'Okulary ochronne, przezroczyste', 'static/barcodes/OKULARY-OCHR-PRZ.png');

INSERT INTO locations (code, location_barcode_path) VALUES
('A1-01', 'static/barcodes/A1-01.png'), ('A1-02', 'static/barcodes/A1-02.png'), ('A1-03', 'static/barcodes/A1-03.png'), ('A1-04', 'static/barcodes/A1-04.png'), ('A1-05', 'static/barcodes/A1-05.png'), ('A1-06', 'static/barcodes/A1-06.png'),
('A2-01', 'static/barcodes/A2-01.png'), ('A2-02', 'static/barcodes/A2-02.png'), ('A2-03', 'static/barcodes/A2-03.png'), ('A2-04', 'static/barcodes/A2-04.png'), ('A2-05', 'static/barcodes/A2-05.png'), ('A2-06', 'static/barcodes/A2-06.png'),
('B1-01', 'static/barcodes/B1-01.png'), ('B1-02', 'static/barcodes/B1-02.png'), ('B1-03', 'static/barcodes/B1-03.png'), ('B1-04', 'static/barcodes/B1-04.png'), ('B1-05', 'static/barcodes/B1-05.png'), ('B1-06', 'static/barcodes/B1-06.png'),
('B2-01', 'static/barcodes/B2-01.png'), ('B2-02', 'static/barcodes/B2-02.png'), ('B2-03', 'static/barcodes/B2-03.png'), ('B2-04', 'static/barcodes/B2-04.png'), ('B2-05', 'static/barcodes/B2-05.png'), ('B2-06', 'static/barcodes/B2-06.png'),
('C1-01', 'static/barcodes/C1-01.png'), ('C1-02', 'static/barcodes/C1-02.png'), ('C1-03', 'static/barcodes/C1-03.png'), ('C1-04', 'static/barcodes/C1-04.png'), ('C1-05', 'static/barcodes/C1-05.png'), ('C1-06', 'static/barcodes/C1-06.png'),
('C2-01', 'static/barcodes/C2-01.png'), ('C2-02', 'static/barcodes/C2-02.png'), ('C2-03', 'static/barcodes/C2-03.png'), ('C2-04', 'static/barcodes/C2-04.png'), ('C2-05', 'static/barcodes/C2-05.png'), ('C2-06', 'static/barcodes/C2-06.png');

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

INSERT INTO receives (username, receives_date) VALUES
('zofia', '2025-01-01 10:00:00'),
('tomek', '2025-01-01 10:00:01'),
('piotr', '2025-01-01 10:00:02');

INSERT INTO receives_products (receive_id, product_id, location_id, quantity) VALUES
((SELECT id FROM receives WHERE username = 'zofia' ORDER BY receives_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'PUSZKA-500'), (SELECT id FROM locations WHERE code = 'A1-01'), 50),
((SELECT id FROM receives WHERE username = 'zofia' ORDER BY receives_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'MARKER-01'), (SELECT id FROM locations WHERE code = 'A1-02'), 20),
((SELECT id FROM receives WHERE username = 'tomek' ORDER BY receives_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'WRK-BOSCH-01'), (SELECT id FROM locations WHERE code = 'B1-01'), 1),
((SELECT id FROM receives WHERE username = 'tomek' ORDER BY receives_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'FOLIA-STRETCH'), (SELECT id FROM locations WHERE code = 'C1-01'), 5),
((SELECT id FROM receives WHERE username = 'piotr' ORDER BY receives_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'SRB-KRZYZ-01'), (SELECT id FROM locations WHERE code = 'A1-01'), 10),
((SELECT id FROM receives WHERE username = 'piotr' ORDER BY receives_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'MLT-STOL-01'), (SELECT id FROM locations WHERE code = 'A1-02'), 3);

INSERT INTO shipments (username, shipment_date) VALUES
('tomek', '2025-01-01 10:01:00'),
('janek', '2025-01-01 10:01:01'),
('ania', '2025-01-01 10:01:02');

INSERT INTO shipment_products (shipment_id, product_id, location_id, quantity) VALUES
((SELECT id FROM shipments WHERE username = 'tomek' ORDER BY shipment_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'WRK-BOSCH-01'), (SELECT id FROM locations WHERE code = 'B1-01'), 1),
((SELECT id FROM shipments WHERE username = 'tomek' ORDER BY shipment_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'FOLIA-STRETCH'), (SELECT id FROM locations WHERE code = 'C1-01'), 5),
((SELECT id FROM shipments WHERE username = 'janek' ORDER BY shipment_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'PUSZKA-500'), (SELECT id FROM locations WHERE code = 'A1-01'), 50),
((SELECT id FROM shipments WHERE username = 'janek' ORDER BY shipment_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'MARKER-01'), (SELECT id FROM locations WHERE code = 'A1-02'), 20),
((SELECT id FROM shipments WHERE username = 'ania' ORDER BY shipment_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'SRB-KRZYZ-01'), (SELECT id FROM locations WHERE code = 'A1-01'), 10),
((SELECT id FROM shipments WHERE username = 'ania' ORDER BY shipment_date DESC LIMIT 1), (SELECT id FROM products WHERE sku = 'MLT-STOL-01'), (SELECT id FROM locations WHERE code = 'A1-02'), 3);