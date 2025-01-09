from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
import sqlite3
from datetime import datetime
import time
import sys

# Database file
DB_FILE = "banking.db"

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

class BankingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Banking Application")
        self.setGeometry(100, 100, 800, 600)

        self.current_account = None
        self.init_ui()

    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.home_screen()

    def home_screen(self):
        self.clear_layout()

        title = QLabel("Welcome to the Banking Application")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        create_account_btn = QPushButton("Create Account")
        create_account_btn.clicked.connect(self.create_account_screen)
        self.layout.addWidget(create_account_btn)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login_screen)
        self.layout.addWidget(login_btn)

    def create_account_screen(self):
        self.clear_layout()

        layout = QVBoxLayout()
        self.layout.addLayout(layout)

        layout.addWidget(QLabel("Create Account"))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Customer Name")
        layout.addWidget(self.customer_name_input)

        self.mobile_number_input = QLineEdit()
        self.mobile_number_input.setPlaceholderText("Mobile Number")
        layout.addWidget(self.mobile_number_input)

        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("Initial Balance")
        layout.addWidget(self.balance_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_account)
        layout.addWidget(create_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.home_screen)
        layout.addWidget(back_btn)

    def create_account(self):
        account_number = int(time.time())
        username = self.username_input.text()
        customer_name = self.customer_name_input.text()
        mobile_number = self.mobile_number_input.text()
        try:
            balance = float(self.balance_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid balance amount.")
            return
        password = self.password_input.text()
        last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO accounts (account_number, username, customer_name, mobile_number, balance, password, last_Login, transaction_history) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (account_number, username, customer_name, mobile_number, balance, password, last_login, "[]")
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"Account created successfully! Your account number is {account_number}.")
            self.home_screen()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Failed to create account. Please try again.")

    def login_screen(self):
        self.clear_layout()

        layout = QVBoxLayout()
        self.layout.addLayout(layout)

        layout.addWidget(QLabel("Login"))

        self.login_account_number_input = QLineEdit()
        self.login_account_number_input.setPlaceholderText("Account Number")
        layout.addWidget(self.login_account_number_input)

        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Username")
        layout.addWidget(self.login_username_input)

        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("Password")
        self.login_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.home_screen)
        layout.addWidget(back_btn)

    def login(self):
        account_number = self.login_account_number_input.text()
        username = self.login_username_input.text()
        password = self.login_password_input.text()

        conn = get_db_connection()
        customer = conn.execute(
            "SELECT * FROM accounts WHERE (account_number = ? OR username = ?) AND password = ?",
            (account_number, username, password)
        ).fetchone()

        if customer:
            self.current_account = customer
            conn.execute(
                "UPDATE accounts SET last_Login = ? WHERE account_number = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), customer["account_number"])
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Login successful!")
            self.account_details_screen()
        else:
            conn.close()
            QMessageBox.warning(self, "Error", "Invalid credentials!")

    def account_details_screen(self):
        self.clear_layout()

        layout = QVBoxLayout()
        self.layout.addLayout(layout)

        layout.addWidget(QLabel(f"Account Details for {self.current_account['customer_name']}"))

        details = QLabel(
            f"Account Number: {self.current_account['account_number']}\n"
            f"Username: {self.current_account['username']}\n"
            f"Mobile Number: {self.current_account['mobile_number']}\n"
            f"Balance: {self.current_account['balance']}\n"
            f"Last Login: {self.current_account['last_Login']}"
        )
        layout.addWidget(details)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

    def logout(self):
        self.current_account = None
        QMessageBox.information(self, "Logout", "You have logged out successfully!")
        self.home_screen()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize database
    conn = get_db_connection()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS accounts ("
        "account_number INTEGER PRIMARY KEY,"
        "username TEXT UNIQUE,"
        "customer_name TEXT,"
        "mobile_number TEXT,"
        "balance REAL,"
        "password TEXT,"
        "last_Login TEXT,"
        "transaction_history TEXT"
        ")"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS transactions ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "account_number INTEGER,"
        "type TEXT,"
        "amount REAL,"
        "timestamp TEXT"
        ")"
    )
    conn.close()

    window = BankingApp()
    window.show()

    sys.exit(app.exec())
