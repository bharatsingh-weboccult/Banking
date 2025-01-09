from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QFormLayout
)
from PySide6.QtCore import Qt
import sqlite3
from datetime import datetime
import sys
import time

DB_FILE = "banking.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

class BankingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Banking App")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.home_label = QLabel("Welcome to the Banking App")
        self.home_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.home_label)

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.clicked.connect(self.create_account)
        layout.addWidget(self.create_account_button)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_account(self):
        dialog = AccountCreationDialog(self)
        dialog

    def login(self):
        dialog = LoginDialog(self)
        dialog.exec_()

class AccountCreationDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.customer_name_input = QLineEdit()
        self.mobile_no_input = QLineEdit()
        self.balance_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Customer Name:", self.customer_name_input)
        form_layout.addRow("Mobile Number:", self.mobile_no_input)
        form_layout.addRow("Initial Balance:", self.balance_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit(self):
        account_number = int(time.time())
        username = self.username_input.text()
        customer_name = self.customer_name_input.text()
        mobile_number = self.mobile_no_input.text()
        try:
            balance = float(self.balance_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Balance must be a number!")
            return
        password = self.password_input.text()
        last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO accounts (account_number, username, customer_name, mobile_number, balance, password, last_Login) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (account_number, username, customer_name, mobile_number, balance, password, last_login)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"Account created successfully! Your account number is {account_number}")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "Failed to create account. Please try again.")

class LoginDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setGeometry(150, 150, 400, 200)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.account_number_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Account Number:", self.account_number_input)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        account_number = self.account_number_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        conn = get_db_connection()
        customer = conn.execute(
            "SELECT * FROM accounts WHERE (account_number = ? OR username = ?) AND password = ?", 
            (account_number, username, password)
        ).fetchone()
        conn.close()

        if customer:
            QMessageBox.information(self, "Success", f"Welcome back, {customer['customer_name']}!")
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials! Please try again.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = BankingApp()
    main_window.show()
    sys.exit(app.exec())
