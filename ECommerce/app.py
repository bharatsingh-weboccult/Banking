from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import requests
import threading
import banking_api
import multiprocessing
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SUPERKEY')

# Databases
DB_ECOMMERCE = os.environ.get('DB_NAME')
DB_BANKING = '/home/wot-bharat/Web task/task1/BankingApp/banking.db'

# API URL for Banking System
BANK_API_URL = 'http://127.0.0.1:5001/process_payment'


# Helper function to connect to the e-commerce database
def get_ecommerce_connection():
    conn = sqlite3.connect(DB_ECOMMERCE)
    conn.row_factory = sqlite3.Row
    return conn


# Helper function to connect to the banking database
def get_banking_connection():
    conn = sqlite3.connect(DB_BANKING)
    conn.row_factory = sqlite3.Row
    return conn


# E-commerce Homepage
@app.route('/')
def index():
    conn = get_ecommerce_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('index.html', products=products)

#####################################################
# Start banking API in a separate thread
def start_banking_api():
    banking_api.run_banking_api()
#####################################################
@app.route('/products')
def product_list():
    # Example data
    products = [
        {'id': 1, 'name': 'Laptop', 'price': 45000, 'stock': 10, 'image_url': 'https://tinyurl.com/dsrgujyfgjig'},
        {'id': 2, 'name': 'Smartphone', 'price': 20000, 'stock': 25, 'image_url': 'https://via.placeholder.com/200'},
        {'id': 3, 'name': 'Headphones', 'price': 1500, 'stock': 50, 'image_url': 'https://via.placeholder.com/200'},
    ]
    return render_template('product_list.html', products=products)


# Add Product to Cart
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form['quantity'])
    conn = get_ecommerce_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if product:
        if 'cart' not in session:
            session['cart'] = []
        cart_item = {
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'total': product['price'] * quantity
        }
        session['cart'].append(cart_item)
        flash('Item added to cart!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Product not found!', 'danger')
        return redirect(url_for('index'))


# View Cart
@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))


# Checkout Page
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Total price of the cart
        total_amount = sum(item['total'] for item in session.get('cart', []))
        # Make payment through banking API
        upi_id = request.form['upi_id']
        pin = request.form['pin']

        # Request to Bank API to process payment
        response = requests.post(BANK_API_URL, json={
            'upi_id': upi_id,
            'pin': pin,
            'amount': total_amount
        })

        if response.status_code == 200 and response.json().get('status') == 'success':
            flash('Payment Successful! Order placed.', 'success')
            # Save the order to the e-commerce database
            conn = get_ecommerce_connection()
            for item in session.get('cart', []):
                conn.execute("INSERT INTO orders (product_id, quantity, total_price, status) VALUES (?, ?, ?, ?)",
                             (item['product_id'], item['quantity'], item['total'], 'completed'))
            conn.commit()
            conn.close()

            session.pop('cart', None)
            return redirect(url_for('payment_success'))

        else:
            flash('Payment failed! Please try again.', 'danger')
            return redirect(url_for('checkout'))

    return render_template('checkout.html')


# Payment Success Page
@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')


# Start the E-commerce app
if __name__ == '__main__':
    # app.run(debug=True, port=5000)

    # Start the banking API in a separate process
    banking_process = multiprocessing.Process(target=start_banking_api)
    banking_process.start()
    
    # Run the e-commerce app
    try:
        app.run(port=5000, debug=True, threaded=True)
    finally:
        # Terminate the banking API process when the main app stops
        banking_process.terminate()