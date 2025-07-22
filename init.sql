
-- Definicje tabel
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

-- Zmiana w tabeli inventory: dodano location_id dla śledzenia produktu w wielu miejscach
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location_id INT NOT NULL, -- Dodana kolumna location_id
    quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id), -- Klucz obcy do locations
    UNIQUE (product_id, location_id) -- Unikalność na parze (produkt, lokalizacja)
);

CREATE TABLE IF NOT EXISTS lists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    list_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS list_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    list_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE (list_id, product_id)
);

-- Zmiana w tabeli shipments: usunięto location_id
CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    shipment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    barcode VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (username) REFERENCES users(username)
    -- FOREIGN KEY (location_id) i kolumna location_id ZOSTAŁY USUNIĘTE
);

CREATE TABLE IF NOT EXISTS shipment_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE (shipment_id, product_id)
);

-- Zmiana w tabeli receives: usunięto location_id
CREATE TABLE IF NOT EXISTS receives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    receives_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    barcode VARCHAR(255) NOT NULL UNIQUE,
    FOREIGN KEY (username) REFERENCES users(username)
    -- FOREIGN KEY (location_id) i kolumna location_id ZOSTAŁY USUNIĘTE
);

CREATE TABLE IF NOT EXISTS receives_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receives_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (receives_id) REFERENCES receives(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE (receives_id, product_id)
);

-- Dane początkowe (zaktualizowane o brak location_id w shipments i receives)

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

-- Dane dla inventory, teraz z location_id, co zgadza się z danymi, które podałeś
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

INSERT INTO lists (list_name, description) VALUES
('Standardowa Wysylka A', 'Lista produktów do standardowej wysyłki A'),
('Materiały Biurowe', 'Lista materiałów biurowych do przyjęcia'),
('Narzędzia Elektryczne', 'Lista narzędzi do wysyłki');

INSERT INTO list_items (list_id, product_id, quantity) VALUES
((SELECT id FROM lists WHERE list_name = 'Standardowa Wysylka A'), (SELECT id FROM products WHERE sku = 'WRK-BOSCH-01'), 1),
((SELECT id FROM lists WHERE list_name = 'Standardowa Wysylka A'), (SELECT id FROM products WHERE sku = 'FOLIA-STRETCH'), 5),
((SELECT id FROM lists WHERE list_name = 'Materiały Biurowe'), (SELECT id FROM products WHERE sku = 'PUSZKA-500'), 50),
((SELECT id FROM lists WHERE list_name = 'Materiały Biurowe'), (SELECT id FROM products WHERE sku = 'MARKER-01'), 20),
((SELECT id FROM lists WHERE list_name = 'Narzędzia Elektryczne'), (SELECT id FROM products WHERE sku = 'SRB-KRZYZ-01'), 10),
((SELECT id FROM lists WHERE list_name = 'Narzędzia Elektryczne'), (SELECT id FROM products WHERE sku = 'MLT-STOL-01'), 3);

-- Zmiana w INSERTach dla shipments: usunięto location_id
INSERT INTO shipments (username, barcode) VALUES
('tomek', 'SHIP-001-ABC'),
('janek', 'SHIP-002-DEF'),
('ania', 'SHIP-003-GHI');

INSERT INTO shipment_products (shipment_id, product_id, quantity) VALUES
((SELECT id FROM shipments WHERE barcode = 'SHIP-001-ABC'), (SELECT id FROM products WHERE sku = 'WRK-BOSCH-01'), 1),
((SELECT id FROM shipments WHERE barcode = 'SHIP-001-ABC'), (SELECT id FROM products WHERE sku = 'FOLIA-STRETCH'), 5),
((SELECT id FROM shipments WHERE barcode = 'SHIP-002-DEF'), (SELECT id FROM products WHERE sku = 'PUSZKA-500'), 50),
((SELECT id FROM shipments WHERE barcode = 'SHIP-002-DEF'), (SELECT id FROM products WHERE sku = 'MARKER-01'), 20),
((SELECT id FROM shipments WHERE barcode = 'SHIP-003-GHI'), (SELECT id FROM products WHERE sku = 'SRB-KRZYZ-01'), 10),
((SELECT id FROM shipments WHERE barcode = 'SHIP-003-GHI'), (SELECT id FROM products WHERE sku = 'MLT-STOL-01'), 3);

-- Zmiana w INSERTach dla receives: usunięto location_id
INSERT INTO receives (username, barcode) VALUES
('zofia', 'REC-001-PQR'),
('tomek', 'REC-002-STU'),
('piotr', 'REC-003-VWX');

INSERT INTO receives_products (receives_id, product_id, quantity) VALUES
((SELECT id FROM receives WHERE barcode = 'REC-001-PQR'), (SELECT id FROM products WHERE sku = 'PUSZKA-500'), 50),
((SELECT id FROM receives WHERE barcode = 'REC-001-PQR'), (SELECT id FROM products WHERE sku = 'MARKER-01'), 20),
((SELECT id FROM receives WHERE barcode = 'REC-002-STU'), (SELECT id FROM products WHERE sku = 'WRK-BOSCH-01'), 1),
((SELECT id FROM receives WHERE barcode = 'REC-002-STU'), (SELECT id FROM products WHERE sku = 'FOLIA-STRETCH'), 5),
((SELECT id FROM receives WHERE barcode = 'REC-003-VWX'), (SELECT id FROM products WHERE sku = 'SRB-KRZYZ-01'), 10),
((SELECT id FROM receives WHERE barcode = 'REC-003-VWX'), (SELECT id FROM products WHERE sku = 'MLT-STOL-01'), 3);