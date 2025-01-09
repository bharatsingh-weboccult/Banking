from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import time
import ast
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SUPERKEY')


# Database file
DB_FILE = os.environ.get('DB_NAME')


# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Create Account Page
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_number = int(time.time())
        username = request.form['username']
        customer_name = request.form['customer_name']
        mobile_number = request.form['mobile_no']
        balance = float(request.form['balance'])
        password = request.form['password']
        last_Login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # lastLogin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO accounts (account_number, username, customer_name, mobile_number, balance, password, last_Login, transaction_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (account_number, username, customer_name, mobile_number, balance, password, last_Login, transaction_history)
            )
            conn.commit()
            conn.close()
            flash('Account created successfully! Your account number is ' + account_number, 'success')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Failed !')
            return redirect(url_for('create_account'))

    return render_template('create_account.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_number = request.form['account_number']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        customer = conn.execute(
            "SELECT account_number, username, customer_name, mobile_number, balance, last_login FROM accounts WHERE (account_number = ? OR username = ?) AND password = ?", 
            (account_number, username, password)
        ).fetchone()
        last_Login = datetime.now().replace(microsecond=0)
        conn.execute(
            "UPDATE accounts SET last_Login = ? WHERE account_number = ?",
            (last_Login, customer['account_number'])
        )
        conn.commit()
        conn.close()

        if customer:
            # Store account_number and set 'logged_in' in session
            session['account_number'] = customer['account_number']
            session['logged_in'] = True  # Add this line
            flash('Login successful!', 'success')
            return redirect(url_for('account_details', account_number=session['account_number']))

        else:
            flash('Invalid credentials!', 'Failed!')
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/account_details/<account_number>')
def account_details(account_number):
    # Check if user is logged in
    if 'account_number' not in session:
        flash('You must log in first!', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Fetch account details
    customer = conn.execute(
        "SELECT account_number, username, customer_name, mobile_number, balance, last_login FROM accounts WHERE account_number = ?", 
        (account_number,)
    ).fetchone()
    # Fetch transaction history
    transactions = conn.execute(
        "SELECT type, amount, timestamp FROM transactions WHERE account_number = ? ORDER BY timestamp DESC", 
        (account_number,)
    ).fetchall()
    conn.close()

    if customer:
        return render_template('account_details.html', customer=customer, transactions=transactions)
    else:
        flash('Account not found!', 'danger')
        return redirect(url_for('home'))



@app.route('/deposit/<account_number>', methods=['GET', 'POST'])
def deposit(account_number):
    # Ensure user is logged in and authorized
    if not session.get('logged_in') or session.get('account_number') != int(account_number):
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            
            conn = get_db_connection()
            # Insert transaction into the transactions table
            conn.execute(
                "INSERT INTO transactions (account_number, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                (account_number, 'Deposit', amount, datetime.now())
            )
            # Update account balance
            conn.execute(
                "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
                (amount, account_number)
            )
            conn.commit()
            flash('Deposit successful!', 'success')
        except Exception as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            conn.close()

        return redirect(url_for('account_details', account_number=account_number))

    return render_template('deposit.html')


@app.route('/withdraw/<account_number>', methods=['GET', 'POST'])
def withdraw(account_number):
    # Ensure user is logged in and authorized
    if not session.get('logged_in') or session.get('account_number') != int(account_number):
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])

            conn = get_db_connection()
            # Get current balance
            customer = conn.execute(
                "SELECT balance FROM accounts WHERE account_number = ?", 
                (account_number,)
            ).fetchone()

            if customer and customer['balance'] >= amount:
                # Insert transaction into the transactions table
                conn.execute(
                    "INSERT INTO transactions (account_number, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                    (account_number, 'Withdraw', amount, datetime.now())
                )
                # Update account balance
                conn.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
                    (amount, account_number)
                )
                conn.commit()
                flash('Withdrawal successful!', 'success')
            else:
                flash('Insufficient balance!', 'danger')
        except Exception as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            conn.close()

        return redirect(url_for('account_details', account_number=account_number))

    return render_template('withdraw.html')

@app.route('/transaction_history/<account_number>')
def transaction_history(account_number):
    # Check if user is logged in
    if 'account_number' not in session or session['account_number'] != int(account_number):
        flash('You must log in to access this page!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Fetch transaction history
    transactions = conn.execute(
        "SELECT type, amount, timestamp FROM transactions WHERE account_number = ? ORDER BY timestamp DESC", 
        (account_number,)
    ).fetchall()
    conn.close()

    return render_template('transaction_history.html', transactions=transactions, account_number=account_number)



# Reset Password Page
@app.route('/reset_password/<account_number>', methods=['GET', 'POST'])
def reset_password(account_number):
    if request.method == 'POST':
        new_password = request.form['new_password']

        conn = get_db_connection()
        conn.execute(
            "UPDATE accounts SET password = ? WHERE account_number = ?", 
            (new_password, account_number)
        )
        conn.commit()
        conn.close()

        flash('Password reset successful!', 'success')
        return redirect(url_for('account_details', account_number=account_number))

    return render_template('reset_password.html')


# Logout Page
@app.route('/logout')
def logout():
    # Remove account_number from session
    session.pop('account_number', None)
    flash('You have logged out successfully!', 'info')
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
