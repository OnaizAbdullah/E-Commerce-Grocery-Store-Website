DROP TABLE IF EXISTS items;

CREATE TABLE items
(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    type TEXT NOT NULL
);

INSERT INTO items (name, price, type)
VALUES
('Milk', 3.00, 'Dairy'),
('Bread', 2.50, 'Carbohydrates'),
('Rice', 1.33, 'Carbohydrates'),
('Chocolate', 4.00, 'Sweets' ),
('Runners', 8.99, 'Footwear'),
('Oil', 4.50, 'Cooking'),
('Lollipops',2.00,'Sweets'),
('Slippers',4.00, 'Footwear'),
('Socks',5.00,'Clothing'),
('Vest',6.00,'Clothing');

DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS admins;
CREATE TABLE admins
(
    admin_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS feedback;
CREATE TABLE feedback
(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_text TEXT
);
SELECT *
FROM users;