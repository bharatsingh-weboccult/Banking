from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

####################################################
@app.route('/api/check_balance', methods=['GET'])
def check_balance():
    return jsonify({"message": "Balance API is working"})

# Add a function to run this API
def run_banking_api():
    app.run(port=5001, debug=True)
#####################################################
# Database file for Banking System
DB_FILE = '/home/wot-bharat/Web task/task1/BankingApp/banking.db'


# Helper function to connect to the banking database
def get_banking_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Process Payment API
@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    upi_id = data['upi_id']
    pin = data['pin']
    amount = data['amount']

    # Verify account details
    conn = get_banking_connection()
    customer = conn.execute(
        "SELECT account_number, balance  FROM accounts WHERE upi_id = ? AND pin = ?",
        (upi_id, pin)
    ).fetchone()

    if customer:
        # Check if the user has enough balance
        if customer['balance'] >= amount:
            # Deduct the amount from the account balance
            conn.execute(
                "UPDATE accounts SET balance = balance - ? WHERE upi_id = ?",
                (amount, upi_id)
            )
            conn.execute(
                    "INSERT INTO transactions (account_number, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                    (customer['account_number'], 'Paid', amount, datetime.now())
                )
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": "Payment successful!"})

        else:
            conn.close()
            return jsonify({"status": "failure", "message": "Insufficient balance!"})

    else:
        conn.close()
        return jsonify({"status": "failure", "message": "Invalid account or password!"})


# Start the Banking API
if __name__ == '__main__':
    run_banking_api()
    # app.run(debug=True, port=5001)
