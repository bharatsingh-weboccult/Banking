import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QWidget, QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
import sqlite3
from datetime import datetime

# Database File
DB_FILE = "banking.db"

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Account Creation Dialog
class AccountCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")

        # Layout
        layout = QVBoxLayout()

        # Fields
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Enter username")
        self.customer_name_field = QLineEdit()
        self.customer_name_field.setPlaceholderText("Enter customer name")
        self.mobile_number_field = QLineEdit()
        self.mobile_number_field.setPlaceholderText("Enter mobile number")
        self.balance_field = QLineEdit()
        self.balance_field.setPlaceholderText("Enter initial balance")
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter password")
        self.password_field.setEchoMode(QLineEdit.Password)

        # Buttons
        self.create_button = QPushButton("Create Account")
        self.create_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        # Add widgets to layout
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_field)
        layout.addWidget(QLabel("Customer Name:"))
        layout.addWidget(self.customer_name_field)
        layout.addWidget(QLabel("Mobile Number:"))
        layout.addWidget(self.mobile_number_field)
        layout.addWidget(QLabel("Initial Balance:"))
        layout.addWidget(self.balance_field)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_field)
        layout.addWidget(self.create_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

# Account Login Dialog
class AccountLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login Account")

        # Layout
        layout = QVBoxLayout()

        # Fields
        self.account_number_field = QLineEdit()
        self.account_number_field.setPlaceholderText("Enter Account Number")
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Enter username")
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter password")
        self.password_field.setEchoMode(QLineEdit.Password)

        # Buttons
        self.login_button = QPushButton("Login Account")
        self.login_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        # Add widgets to layout
        layout.addWidget(QLabel("Account Number:"))
        layout.addWidget(self.account_number_field)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_field)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_field)
        layout.addWidget(self.login_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

# Main Window
class BankingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Banking Application")

        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        # Buttons
        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.clicked.connect(self.create_account)
        self.login_button = QPushButton("Log In")
        self.login_button.clicked.connect(self.login)

        # Add buttons to layout
        layout.addWidget(self.create_account_button)
        layout.addWidget(self.login_button)

        self.central_widget.setLayout(layout)

    def create_account(self):
        dialog = AccountCreationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username = dialog.username_field.text().lower()
            customer_name = dialog.customer_name_field.text()
            mobile_number = dialog.mobile_number_field.text()
            balance = dialog.balance_field.text()
            password = dialog.password_field.text()
            account_number = int(datetime.now().timestamp())  # Unique account number
            last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO accounts (account_number, username, customer_name, mobile_number, balance, password, last_login) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (account_number, username, customer_name, mobile_number, balance, password, last_login)
                )
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"Account created! Account number: {account_number}")
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "Failed to create account. Please try again.")

    def login(self):
        dialog = AccountLoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            account_number = dialog.account_number_field.text()
            username = dialog.username_field.text().lower()
            password = dialog.password_field.text()

            try:
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
                QMessageBox.information(self, f"Successfully Login in Account number: {account_number}")
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "Failed to login account. Please try again.")
        # QMessageBox.information(self, "Login", "Login functionality is not yet implemented.")

# Application Entry Point
def main():
    app = QApplication(sys.argv)
    window = BankingApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
