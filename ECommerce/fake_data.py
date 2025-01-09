import sqlite3

# Connect to the e-commerce database
db_path = "ecommerce.db"  # Change this to the path of your database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define fake data
fake_products = [
    {"name": "Laptop", "price": 45000.0, "stock": 10, "image_url": "https://via.placeholder.com/200"},
    {"name": "Smartphone", "price": 20000.0, "stock": 25, "image_url": "https://via.placeholder.com/200"},
    {"name": "Headphones", "price": 1500.0, "stock": 50, "image_url": "https://via.placeholder.com/200"},
    {"name": "Smartwatch", "price": 5000.0, "stock": 30, "image_url": "https://via.placeholder.com/200"},
    {"name": "Bluetooth Speaker", "price": 3000.0, "stock": 20, "image_url": "https://via.placeholder.com/200"},
    {"name": "Tablet", "price": 25000.0, "stock": 15, "image_url": "https://via.placeholder.com/200"},
    {"name": "Gaming Console", "price": 40000.0, "stock": 5, "image_url": "https://via.placeholder.com/200"},
    {"name": "External Hard Drive", "price": 5000.0, "stock": 40, "image_url": "https://via.placeholder.com/200"},
    {"name": "Monitor", "price": 12000.0, "stock": 10, "image_url": "https://via.placeholder.com/200"},
    {"name": "Keyboard", "price": 1500.0, "stock": 50, "image_url": "https://via.placeholder.com/200"},
]

# Insert data into the products table
try:
    for product in fake_products:
        cursor.execute(
            """
            INSERT INTO products (name, price, stock, image_url)
            VALUES (?, ?, ?, ?)
            """,
            (product["name"], product["price"], product["stock"], product["image_url"]),
        )
    conn.commit()
    print("Fake data inserted successfully into the 'products' table.")
except sqlite3.Error as e:
    print("Error occurred:", e)
finally:
    conn.close()
