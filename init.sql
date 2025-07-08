-- Użytkownicy
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE, 
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE, -- kod produktu
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

-- Produkty
INSERT INTO products (name, sku, description) VALUES
  ('Wkrętarka Bosch', 'WRK-BOSCH-01', 'Wkrętarka akumulatorowa'),
  ('Puszka 500ml', 'PUSZKA-500', 'Metalowa puszka 500 ml'),
  ('Folia stretch', 'FOLIA-STRETCH', 'Folia stretch 23µm, 2kg'),
  ('Kartony 30x30x30', 'KARTON-30', 'Kartony tekturowe'),
  ('Taśma pakowa', 'TASMA-PAK', 'Taśma do pakowania'),
  ('Karton A4', 'KARTON-A4', 'Karton formatu A4'),
  ('Pojemnik plastikowy', 'POJ-PLAST', 'Pojemnik z uchwytem'),
  ('Marker permanentny', 'MARKER-01', 'Czarny marker'),
  ('Naklejki ostrzegawcze', 'NAKLEJKA-OSTR', 'Zestaw etykiet'),
  ('Etykiety termiczne', 'ETYK-TERM', 'Etykiety 1000 szt. rolka');

-- Lokacje A1 do C5
INSERT INTO locations (code) VALUES
  ('A1'), ('A2'), ('A3'), ('A4'), ('A5'),
  ('B1'), ('B2'), ('B3'), ('B4'), ('B5'),
  ('C1'), ('C2'), ('C3'), ('C4'), ('C5');

-- Stan magazynowy (product_id od 1 do 10, location_id od 1 do 15)
INSERT INTO inventory (product_id, location_id, quantity) VALUES
  (1, 1, 30),
  (2, 2, 100),
  (3, 3, 60),
  (4, 4, 45),
  (5, 5, 75),
  (6, 6, 40),
  (7, 7, 20),
  (8, 8, 50),
  (9, 9, 90),
  (10, 10, 70),
  (1, 11, 10),
  (2, 12, 25),
  (3, 13, 35),
  (4, 14, 15),
  (5, 15, 5);