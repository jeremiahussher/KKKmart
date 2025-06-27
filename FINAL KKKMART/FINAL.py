import sys
import re
import os
import json
from PyQt5.QtWidgets import (
    QFileDialog,
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, 
    QMainWindow,
    QSizePolicy, QGridLayout, QFrame, QComboBox, QRadioButton, QListWidget,
    QListWidgetItem, QTextEdit, QCheckBox, QInputDialog, QScrollArea
)
from PyQt5.QtGui import QFont, QCursor, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
import datetime
import database as db



CURRENT_USER = "guest"

def cart_file():
    return f"cart_{CURRENT_USER}.json"
# --------------------

db.ensure_tables()


COUPONS = {
    "10OFF": {"discount": 0.10, "desc": "10% OFF", "min_spend": 0},
    "FREESHIP": {"discount": 0.00, "desc": "Free Shipping", "min_spend": 0},
    "50OFF": {"discount": 0.50, "desc": "50% OFF (max $50)", "min_spend": 0, "max_discount": 50},
    "15OFF": {"discount": 0.15, "desc": "15% OFF (max $150)", "min_spend": 200, "max_discount": 150},
    "20OFF": {"discount": 0.20, "desc": "20% OFF (max $100)", "min_spend": 300, "max_discount": 100},
}

# --------------------
# Simple persistent notifications helper
NOTIFICATION_FILE = "notifications.json"

def load_notifications():
    """Return list of saved notifications (most recent first)."""
    if os.path.exists(NOTIFICATION_FILE):
        try:
            with open(NOTIFICATION_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_notification(text: str):
    """Append a notification entry to the notifications file."""
    data = load_notifications()
    data.insert(0, text)  # newest first
    try:
        with open(NOTIFICATION_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def clear_notifications():
    try:
        with open(NOTIFICATION_FILE, "w") as f:
            json.dump([], f)
    except Exception:
        pass
#Proceed to Login Interface
class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KKKMART - Login")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f5f7fa;
            }
        """)
        self.setup_ui()

        # Initialize database and ensure default users exist
        db.create_users_table()
        # Add admin as seller
        db.add_user("admin", "admin123", "admin@example.com", "00000000000", "seller")
        # Add user as buyer (default type)
        db.add_user("user", "user123", "user@example.com", "00000000001", "buyer")

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        # App title
        title = QLabel("KKKMART")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }
        """)

        # Subtitle
        subtitle = QLabel("Welcome back! Please sign in to continue.")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-top: -10px;")

        self.username_input = self.create_input("Username")
        self.password_input = self.create_input("Password", is_password=True)

        # Show/Hide password button
        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.setFixedHeight(40)
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.clicked.connect(self.show_hide_password)
        self.toggle_password_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: white;
                padding: 5px;
            }
        """)

        password_row = QHBoxLayout()
        password_row.setAlignment(Qt.AlignCenter)
        password_row.setSpacing(0)
        password_row.addWidget(self.password_input)
        password_row.addWidget(self.toggle_password_btn)

        self.remember_checkbox = QCheckBox("Remember Me")

        if os.path.exists("remember_me.json"):
            with open("remember_me.json", "r") as f:
                data = json.load(f)
                self.username_input.setText(data.get("username", ""))
                self.password_input.setText(data.get("password", ""))
                self.remember_checkbox.setChecked(True)

        # Login Button
        login_btn = QPushButton("LOG IN")
        login_btn.setFixedHeight(48)
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
                padding-top: 3px;
            }
        """)
        login_btn.clicked.connect(self.login_validation)

        # Register prompt
        text_label = QLabel("Don't have an account?")
        text_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")

        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #e74c3c;
                border: none;
                font-size: 13px;
                font-weight: 600;
                padding: 0 0 0 5px;
            }
            QPushButton:hover {
                color: #c0392b;
                text-decoration: underline;
            }
        """)
        register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        register_btn.clicked.connect(self.open_register)

        register_row = QHBoxLayout()
        register_row.setAlignment(Qt.AlignCenter)
        register_row.setSpacing(2)
        register_row.addWidget(text_label)
        register_row.addWidget(register_btn)

        # Social login buttons removed as per user request

        # Form container
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Add form elements with labels
        form_layout.addWidget(QLabel("Username"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addLayout(password_row)
        
        # Remember me row
        remember_row = QHBoxLayout()
        remember_row.addWidget(self.remember_checkbox)
        remember_row.addStretch()
        
        # Forgot password link
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #3498db;
                border: none;
                font-size: 12px;
                padding: 0;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        forgot_btn.setCursor(Qt.PointingHandCursor)
        remember_row.addWidget(forgot_btn)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addLayout(form_layout)
        layout.addLayout(remember_row)
        layout.addSpacing(5)
        layout.addWidget(login_btn)
        layout.addSpacing(15)
        layout.addLayout(register_row)
        layout.addStretch()
        
        # Set main layout
        self.setLayout(layout)

    def create_input(self, placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(48)
        input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: white;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        return input_field

    def login_validation(self):
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            print(f"Attempting login for user: {username}")

            if not username or not password:
                QMessageBox.warning(self, "Error", "Please fill in all fields!")
                return

            # First verify the user exists and password is correct
            user_data = db.validate_user(username, password)
            print(f"User data from DB: {user_data}")
            
            if not user_data:
                QMessageBox.warning(self, "Error", "Invalid username or password!")
                return
                
            # Get the user type directly from the validated user data
            user_type = user_data.get('user_type', 'buyer')
            print(f"User type for {username}: {user_type}")
            
            # Save login if "Remember Me" is checked
            if self.remember_checkbox.isChecked():
                with open("remember_me.json", "w") as f:
                    json.dump({"username": username, "password": password}, f)
            else:
                # Remove the file if it exists and "Remember Me" is unchecked
                if os.path.exists("remember_me.json"):
                    os.remove("remember_me.json")
            
            # Create the appropriate page based on user type
            try:
                if user_type == 'seller':
                    print(f"Creating SellerDashboardUI for {user_type}...")
                    self.homepage = SellerDashboardUI(username, self)
                else:
                    print(f"Creating HomePageUI for {user_type}...")
                    self.homepage = HomePageUI(username, self, user_type=user_type)
                
                print("Showing dashboard...")
                self.homepage.show()
                self.hide()
                print("Login successful")
                return  # Successfully logged in
                
            except Exception as e:
                print(f"Error creating home page: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to initialize user interface: {str(e)}")
                return
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            QMessageBox.critical(self, "Error", "An unexpected error occurred during login.")

    def open_register(self):
        self.register_window = RegisterUI(self)
        self.register_window.show()
        self.hide()

    def show_hide_password(self):
        if self.toggle_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Show")

    def add_new_user(self, username, password):
        db.add_user(username, password)

#This is Register Window
class RegisterUI(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Create New Account - KKKMART")
        self.setGeometry(100, 100, 400, 650)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: white;
            }
        """)
        self.register_setup_ui()

    # Register Setup with modern design
    def register_setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # App title
        title = QLabel("Create Account")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                margin-bottom: 5px;
                letter-spacing: 0.5px;
            }
        """)

        # Subtitle
        subtext = QLabel("Join KKKMART today")
        subtext.setFont(QFont("Segoe UI", 10))
        subtext.setAlignment(Qt.AlignCenter)
        subtext.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")

        # Form container
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.setup_input(self.name_input)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.setup_input(self.email_input)
        
        # Phone input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        self.setup_input(self.phone_input)
        
        # Password input with toggle
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
                padding: 0 15px;
                font-size: 14px;
                background: #f8f9fa;
                color: #2c3e50;
                height: 48px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: white;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        
        self.toggle_register_password = QPushButton("Show")
        self.toggle_register_password.setFixedSize(80, 48)
        self.toggle_register_password.setCheckable(True)
        self.toggle_register_password.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_register_password.setStyleSheet("""
            QPushButton {
                border: 2px solid #e0e0e0;
                border-left: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f1f1f1;
            }
            QPushButton:checked {
                color: #e74c3c;
            }
        """)
        self.toggle_register_password.clicked.connect(self.password_visibility)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_register_password)
        
        # Account Type Selection
        account_type_container = QWidget()
        account_type_layout = QVBoxLayout(account_type_container)
        account_type_layout.setContentsMargins(0, 10, 0, 0)
        
        account_type_label = QLabel("Account Type")
        account_type_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 8px;
            }
        """)
        
        radio_container = QWidget()
        radio_layout = QHBoxLayout(radio_container)
        radio_layout.setContentsMargins(0, 0, 0, 0)
        radio_layout.setSpacing(20)
        
        self.buyer_radio = QRadioButton("Buyer")
        self.seller_radio = QRadioButton("Seller")
        self.buyer_radio.setChecked(True)
        
        # Style radio buttons
        radio_style = """
            QRadioButton {
                color: #2c3e50;
                font-size: 14px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #e74c3c;
                border: 2px solid #e74c3c;
            }
            QRadioButton::indicator:hover {
                border-color: #95a5a6;
            }
        """
        self.buyer_radio.setStyleSheet(radio_style)
        self.seller_radio.setStyleSheet(radio_style)
        
        radio_layout.addWidget(self.buyer_radio)
        radio_layout.addWidget(self.seller_radio)
        radio_layout.addStretch()
        
        account_type_layout.addWidget(account_type_label)
        account_type_layout.addWidget(radio_container)

        # Add all form elements to form layout
        form_layout.addWidget(QLabel("Full Name"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Email Address"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(QLabel("Phone Number"))
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(password_container)
        form_layout.addWidget(account_type_container)
        
        # Sign Up Button
        self.sign_up_btn = QPushButton("CREATE ACCOUNT")
        self.sign_up_btn.setFixedHeight(50)
        self.sign_up_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.sign_up_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                margin: 5px 0 15px 0;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.sign_up_btn.clicked.connect(self.register_validation)
        
        # Login prompt
        login_prompt = QHBoxLayout()
        login_prompt.setAlignment(Qt.AlignCenter)
        login_prompt.setSpacing(5)
        
        login_prompt.addWidget(QLabel("Already have an account?"))
        login_btn = QPushButton("Sign in")
        login_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #e74c3c;
                border: none;
                font-weight: 600;
                padding: 0;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #c0392b;
                text-decoration: underline;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.back_to_login)
        login_prompt.addWidget(login_btn)
        
        # Add all widgets to main layout
        layout.addWidget(title)
        layout.addWidget(subtext)
        layout.addLayout(form_layout)
        layout.addWidget(self.sign_up_btn)
        layout.addLayout(login_prompt)
        
        # Set the main layout
        self.setLayout(layout)

    # Input field setup
    def setup_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background: #f8f9fa;
                color: #2c3e50;
                height: 48px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: white;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        widget.setFixedHeight(48)

    #Validation of Creating Account
    def register_validation(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not email or not password or not phone:
            QMessageBox.warning(self, "Input Error", "Please fill all of this!!!!")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Failed to Create Account", "Enter a valid email address.")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Failed to Create Account", "Password must be at least 6 characters long.")
            return

        if not phone.isdigit() or len(phone) < 11:
            QMessageBox.warning(self, "Failed to Create Account", "Enter a valid phone number.")
            return

        # Determine account type
        user_type = 'seller' if self.seller_radio.isChecked() else 'buyer'
        
        if db.add_user(name, password, email, phone, user_type):
            QMessageBox.information(self, "Registration Successful", f"Welcome, {name}!")
            self.login_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Registration Failed", "Username already exists.")

    #Must be password visible if are showed
    def password_visibility(self):
        if self.toggle_register_password.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_register_password.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_register_password.setText("Show")

    #Going back to Login Interface
    def back_to_login(self):
        self.login_window.show()
        self.close()
    
#HomePage Window
class HomePageUI(QMainWindow):
    def __init__(self, username, login_window, user_type='buyer'):
        super().__init__()
        self.setWindowTitle("KKKMART - Home")
        self.setGeometry(100, 100, 360, 640)
        self.username = username
        self.login_window = login_window
        self.user_type = user_type  # Store user type
        self.setStyleSheet("background-color: white;")
        self.settings_window = None
        self.homepage_setup_ui()

    def setup_seller_ui(self, main_layout):
        """Setup the UI for seller dashboard"""
        # Add seller-specific widgets here
        welcome_label = QLabel(f"Welcome, Seller: {self.username}")
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        welcome_label.setStyleSheet("color: red;")
        main_layout.addWidget(welcome_label)
        
        # Add Product Button
        add_product_btn = QPushButton("Add New Product")
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 15px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        add_product_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_product_btn.clicked.connect(self.open_add_product)
        main_layout.addWidget(add_product_btn)
        
        # Product Management Section
        manage_label = QLabel("Your Products")
        manage_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(manage_label)
        
        # Add the product grid
        grid_widget = self.create_product_grid()
        if grid_widget:
            main_layout.addWidget(grid_widget)
        
        main_layout.addStretch()
        return main_layout
    
    def create_product_grid(self):
        """Create and return a grid layout with products"""
        # Create a grid layout
        grid = QGridLayout()
        grid.setSpacing(15)  # Add some spacing between items
        
        # Load products
        default_products = [
            {"image": "sneakers.png", "name": "Shoes", "price": "$70", "stocks": "20", "rating": "⭐⭐⭐⭐⭐", 
             "description": "Comfortable sneakers for everyday wear.", "seller": "Shoe Marketplace"},
            {"image": "laptop.png", "name": "Laptop", "price": "$600", "stocks": "50", "rating": "⭐⭐⭐⭐⭐",
              "description": "High-performance laptop for work and play.", "seller": "Laptop Marketplace"},
            {"image": "phone.png", "name": "NOKIA PHONE", "price": "$300", "stocks": "50", "rating": "⭐⭐⭐⭐⭐",
                "description": "Latest smartphone with advanced features.", "seller": "Phone Marketplace"},
            {"image": "clothes.png", "name": "Tupad Clothes", "price": "$150", "stocks": "30", "rating": "⭐⭐⭐",
                "description": "Bibile ka neto? Matuto kang TUMUPAD sa usapan!", "seller": "Tupad Clothing System"}
        ]
        products_grid = default_products
        
        if os.path.exists("products.json"):
            try:
                with open("products.json", "r") as f:
                    user_products = json.load(f)
                    # create mapping for quick lookup and update stocks/prices
                    name_map = {p['name'].strip().lower(): p for p in products_grid}
                    for prod in user_products:
                        name_key = prod.get('name', '').strip().lower()
                        if not name_key:
                            continue
                        if name_key in name_map:
                            # Update existing default product with latest details (e.g., stocks)
                            name_map[name_key].update(prod)
                        else:
                            products_grid.append(prod)
                            name_map[name_key] = prod
            except Exception as e:
                print(f"Error loading products: {e}")
        
        # ensure uniqueness (remove any duplicates that slipped through)
        unique_products = []
        seen_names = set()
        for prod in products_grid:
            n = prod.get('name', '').strip().lower()
            if n and n not in seen_names:
                unique_products.append(prod)
                seen_names.add(n)
        products_grid = unique_products
        
        # Create product buttons in a 2-column grid
        row, col = 0, 0
        for product in products_grid:
            # Create a container widget for each product
            product_widget = QWidget()
            product_widget.setStyleSheet("""
                QWidget {
                    background: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #f0f0f0;
                    padding: 0;
                    margin: 5px;
                    transition: all 0.3s ease;
                }
                QWidget:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
                }
                QLabel {
                    color: #2c3e50;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """)
            
            # Create layout for the product widget
            layout = QVBoxLayout(product_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Product image container with fixed aspect ratio
            image_container = QWidget()
            image_container.setFixedHeight(140)
            image_container.setStyleSheet("background: #f8f9fa; border-top-left-radius: 12px; border-top-right-radius: 12px;")
            image_layout = QVBoxLayout(image_container)
            image_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add product image
            image_label = QLabel()
            if os.path.exists(product.get('image', '')):
                pixmap = QPixmap(product['image']).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("No Image")
                image_label.setStyleSheet("color: #95a5a6; font-style: italic;")
            image_label.setAlignment(Qt.AlignCenter)
            image_layout.addWidget(image_label, 0, Qt.AlignCenter)
            layout.addWidget(image_container)
            
            # Product details container
            details_container = QWidget()
            details_container.setStyleSheet("background: white; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; padding: 12px;")
            details_layout = QVBoxLayout(details_container)
            details_layout.setContentsMargins(8, 12, 8, 12)
            details_layout.setSpacing(6)
            
            # Add product name
            name_label = QLabel(product.get('name', 'Unnamed Product'))
            name_label.setStyleSheet("""
                font-weight: 600;
                font-size: 14px;
                color: #2c3e50;
                margin-bottom: 4px;
            """)
            name_label.setWordWrap(True)
            details_layout.addWidget(name_label)
            
            # Add product price
            price_label = QLabel(f"${float(product.get('price', '0').replace('$', '')):.2f}")
            price_label.setStyleSheet("""
                color: #e74c3c;
                font-weight: 700;
                font-size: 16px;
                margin: 4px 0;
            """)
            details_layout.addWidget(price_label)
            
            # Rating and stock row
            rating_stock_container = QWidget()
            rating_stock_layout = QHBoxLayout(rating_stock_container)
            rating_stock_layout.setContentsMargins(0, 0, 0, 0)
            rating_stock_layout.setSpacing(10)
            
            # Add rating
            rating_label = QLabel(product.get('rating', '⭐⭐⭐⭐⭐'))
            rating_label.setStyleSheet("color: #f1c40f; font-size: 14px;")
            rating_stock_layout.addWidget(rating_label)
            
            # Add stock indicator
            stock = int(product.get('stocks', product.get('stock', '0')))
            stock_label = QLabel(f"{stock} in stock")
            stock_label.setStyleSheet("""
                color: #27ae60;
                font-size: 12px;
                font-weight: 500;
                padding: 2px 6px;
                background: rgba(39, 174, 96, 0.1);
                border-radius: 4px;
            """)
            if stock < 5:
                stock_label.setStyleSheet("""
                    color: #e74c3c;
                    font-size: 12px;
                    font-weight: 500;
                    padding: 2px 6px;
                    background: rgba(231, 76, 60, 0.1);
                    border-radius: 4px;
                """)
            rating_stock_layout.addWidget(stock_label)
            rating_stock_layout.addStretch()
            
            details_layout.addWidget(rating_stock_container)
            layout.addWidget(details_container)
            
            # Add click handler
            product_widget.mousePressEvent = lambda e, p=product: self.open_item_details(
                p.get('image', ''), 
                p.get('name', ''), 
                p.get('price', '0'), 
                p.get('stocks', p.get('stock', '0')), 
                p.get('rating', ''), 
                p.get('description', ''), 
                p.get('seller', ''), 
                p.get('sizes', [])
            )
            product_widget.setCursor(Qt.PointingHandCursor)
            
            # Add to grid
            grid.addWidget(product_widget, row, col)
            
            # Update grid position
            col += 1
            if col >= 2:  # 2 columns
                col = 0
                row += 1
        
        # Add stretch to push everything to the top
        grid.setRowStretch(row + 1, 1)
        grid.setColumnStretch(2, 1)
        
        return grid
    
    def setup_buyer_ui(self, main_layout):
        # Clear existing widgets
        for i in reversed(range(main_layout.count())):
            main_layout.itemAt(i).widget().setParent(None)
        
        # Add sale banner
        banner = QLabel("SALE: Up to 50% OFF!")
        banner.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                margin: 10px 0;
            }
        """)
        banner.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(banner)
        
        # Add product grid
        main_layout.addWidget(QLabel("Trending Products"))
        
        # Create and add the product grid
        grid_layout = self.create_product_grid()
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

    def homepage_setup_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Add header with welcome message and profile button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        welcome_label = QLabel(f"Welcome, {self.username}")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        profile_btn = QPushButton()
        profile_btn.setIcon(QIcon("profile.png"))
        profile_btn.setIconSize(QSize(30, 30))
        profile_btn.setFixedSize(40, 40)
        profile_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #e74c3c;
                border-radius: 20px;
                background: white;
            }
            QPushButton:hover {
                background: #f5f5f5;
            }
        """)
        profile_btn.clicked.connect(self.open_profile)
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(profile_btn)
        
        main_layout.addWidget(header)
        
        # Add search bar and button
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 10)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search products...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 1px solid #e74c3c;
            }
        """)
        
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        search_btn.clicked.connect(self.search_product)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_btn)
        main_layout.addWidget(search_container)
        
        # Add scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)
        
        # Add content based on user type
        if self.user_type == 'seller':
            self.setup_seller_ui(scroll_layout)
        else:
            self.setup_buyer_ui(scroll_layout)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Add navigation bar
        self.setup_navigation_bar(main_layout)

    def setup_navigation_bar(self, main_layout):
        # Create navigation bar container
        nav_bar = QWidget()
        nav_bar.setFixedHeight(60)
        nav_bar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #e0e0e0;
            }
        """)
        
        # Create layout for navigation buttons
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(10, 5, 10, 5)
        nav_layout.setSpacing(10)
        
        # Define navigation items
        nav_items = [
            ("home", "Home", self.go_home),
            ("cart", "Inventory", self.open_inventory),
            ("orders", "Orders", self.open_orders),
            ("coupons", "Coupons", self.open_coupons),
            ("bell", "Notification", self.open_notification),
            ("settings", "Setting", self.open_settings),
            ("profile", "Profile", self.open_profile)
        ]
        
        # Add navigation buttons
        for icon_name, tooltip, callback in nav_items:
            btn = QPushButton()
            btn.setIcon(QIcon(f"{icon_name}.png"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setFixedSize(40, 40)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background: #f5f5f5;
                }
            """)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        # Add navigation bar to main layout
        main_layout.addWidget(nav_bar)

    def search_product(self):
        self.product_window = ProductWindow(self)
        self.product_window.show()
        self.close()

    def go_home(self):
        # Already on home page, do nothing
        pass
        
    def open_inventory(self):
        self.inventory_window = InventoryCartUI(self)
        self.inventory_window.show()
        self.close()

    def open_settings(self):
        self.settings_window = AccountSettingsUI(self.login_window, self)
        self.settings_window.show()
        self.hide()
    
    def open_orders(self):
        self.orders_window = OrderHistoryUI(self)
        self.orders_window.show()
        self.close()

    def open_summary(self):
        self.summary_window = SummaryUI(self)
        self.summary_window.show()
        self.close()

    def open_product_listing(self):
        self.product_window = ProductWindow(self)
        self.product_window.show()
        self.close()

    def open_coupons(self):
        self.coupons_window = CouponsUI(self)
        self.coupons_window.show()
        self.close()

    def open_item_details(self, image_path, name, price, stocks, rating, description, seller, sizes):
        # fetch up-to-date stock from products.json
        latest_stocks = stocks
        if os.path.exists("products.json"):
            try:
                with open("products.json", "r") as f:
                    prods = json.load(f)
                for p in prods:
                    if p.get("name", "").strip().lower() == name.strip().lower():
                        latest_stocks = p.get("stocks", p.get("stock", stocks))
                        break
            except Exception:
                pass
        self.item_details_window = ItemDetailsUI(self, image_path, name, price, latest_stocks, rating, description, seller, sizes)
        self.item_details_window.show()
        self.close()
    
    def open_notification(self):
        self.notification_window = NotificationUI(self)
        self.notification_window.show()
        self.close()

    def open_profile(self):
        self.profile_window = ProfileUI(self)
        self.profile_window.show()
        self.hide()

    def open_account_settings(self):
        if not self.settings_window:
            self.settings_window = AccountSettingsUI(self.login_window, self)
        self.settings_window.show()
        self.hide()

    def open_add_product(self):
        self.add_product_window = AddProductUI(self)
        self.add_product_window.show()
        self.close()

class SellerDashboardUI(QWidget):
    def __init__(self, username, login_window):
        super().__init__()
        self.username = username
        self.login_window = login_window
        self.setWindowTitle("KKKMART - Seller Dashboard")
        self.setGeometry(100, 100, 360, 640)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: bold;
                color: #ff4444;
                margin: 10px 0;
            }
            QLabel#stats {
                font-size: 14px;
                padding: 8px;
                border-radius: 8px;
                margin: 5px 0;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel(f"Welcome, {self.username}")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Stats Overview
        stats_layout = QVBoxLayout()
        
        # Total Products
        total_products = QLabel("Total Products: 0")
        total_products.setObjectName("stats")
        total_products.setStyleSheet("background-color: #e3f2fd; color: #0d47a1;")
        
        # Total Orders
        total_orders = QLabel("Total Orders: 0")
        total_orders.setObjectName("stats")
        total_orders.setStyleSheet("background-color: #e8f5e9; color: #2e7d32;")
        
        # Revenue
        revenue = QLabel("Total Revenue: ₱0.00")
        revenue.setObjectName("stats")
        revenue.setStyleSheet("background-color: #fff3e0; color: #e65100;")
        
        stats_layout.addWidget(total_products)
        stats_layout.addWidget(total_orders)
        stats_layout.addWidget(revenue)
        layout.addLayout(stats_layout)

        # Buttons
        buttons = [
            ("➕ Add Product", self.add_product),
            ("📦 My Products", self.view_products),
            ("📋 Orders", self.view_orders),
            ("📊 Analytics", self.view_analytics),
            ("⚙️ Settings", self.open_settings),
            ("👋 Logout", self.logout)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)

    def view_products(self):
        # Show the product list for this seller
        QMessageBox.information(self, "My Products", "Product management will open here.")
        # You can integrate the ProductListUI from seller_home.py here

    def view_orders(self):
        # Show orders for this seller's products
        QMessageBox.information(self, "Orders", "Order management will open here.")

    def view_analytics(self):
        # Show sales analytics
        QMessageBox.information(self, "Analytics", "Sales analytics will be shown here.")

    def open_settings(self):
        # Open seller settings
        QMessageBox.information(self, "Settings", "Seller settings will open here.")

    def logout(self):
        # Show confirmation dialog before logging out
        reply = QMessageBox.question(
            self, 'Logout', 'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Return to login window if user confirms
            self.login_window.show()
            self.close()
        
    def add_product(self):
        # Open the Add Product window
        self.add_product_ui = AddProductUI(self)
        self.add_product_ui.show()
        self.hide()

class AddProductUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("Add New Product")
        self.setGeometry(100, 100, 360, 500)
        self.homepage_window = homepage_window
        self.setStyleSheet("background-color: white;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product Name")
        layout.addWidget(self.name_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        layout.addWidget(self.price_input)

        self.stocks_input = QLineEdit()
        self.stocks_input.setPlaceholderText("Stocks")
        layout.addWidget(self.stocks_input)

        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("Rating (e.g. 4.5)")
        layout.addWidget(self.rating_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description")
        layout.addWidget(self.desc_input)

        # Image selection
        image_layout = QHBoxLayout()
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Click 'Browse' to select an image")
        self.image_input.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet("background-color: #ff4444; color: white; border-radius: 5px; padding: 5px;")
        browse_btn.clicked.connect(self.browse_image)
        
        image_layout.addWidget(self.image_input)
        image_layout.addWidget(browse_btn)
        layout.addLayout(image_layout)

        add_btn = QPushButton("Add Product")
        add_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        add_btn.clicked.connect(self.save_product)
        layout.addWidget(add_btn)

        back_btn = QPushButton("<- Back")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def browse_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Product Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
            options=options
        )
        if file_name:
            # Store just the filename, not the full path
            self.image_input.setText(os.path.basename(file_name))
            # You might want to copy the image to your application's image directory here
            # For example:
            # import shutil
            # shutil.copy2(file_name, os.path.join("images", os.path.basename(file_name)))

    def save_product(self):
        product = {
            "image": self.image_input.text().strip(),
            "name": self.name_input.text().strip(),
            "price": self.price_input.text().strip(),
            "stocks": self.stocks_input.text().strip(),
            "rating": self.rating_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "seller": self.current_user 
        }
        if not all(product.values()):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        products = []
        if os.path.exists("products.json"):
            with open("products.json", "r") as f:
                try:
                    products = json.load(f)
                except Exception:
                    products = []
        products.append(product)
        with open("products.json", "w") as f:
            json.dump(products, f, indent=4)
        QMessageBox.information(self, "Success", "Product added!")
        self.go_back()

    def go_back(self):
        self.homepage_window.show()
        self.close()


class ItemDetailsUI(QWidget):
    def __init__(self, homepage_window, image_path, name, price, stocks, rating, description, seller, sizes):
        super().__init__()
        self.setWindowTitle("KKKMART - Item Details")
        self.setGeometry(100, 100, 360, 640)
        self.homepage_window = homepage_window
        self.seller = seller
        self.setStyleSheet("background-color: white;")
        
        # Store values
        self.image_path = image_path
        self.name = name
        self.price = price
        self.stocks = stocks
        self.rating = rating
        self.description = description
        self.seller = seller
        self.sizes = sizes
        self.item_details_setup_ui()

    #Setup ng Item Details
    def item_details_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Top Bar
        top_bar = QHBoxLayout()
        back_btn = QPushButton("<-")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("color: white; font-size: 18px; background: red; border: none;")
        back_btn.clicked.connect(self.go_back)

        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        product_image = QLabel()
        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        product_image.setPixmap(pixmap)
        product_image.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(product_image)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: red; background-color: red; height: 2px;")
        line.setFixedHeight(2)
        main_layout.addWidget(line)

        name_price_layout = QHBoxLayout()
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        price_label = QLabel(self.price)
        price_label.setFont(QFont("Arial", 14))
        price_label.setStyleSheet("color: red;")
        name_price_layout.addWidget(name_label)
        name_price_layout.addStretch()
        name_price_layout.addWidget(price_label)
        main_layout.addLayout(name_price_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: red; background-color: red; height: 2px;")
        line.setFixedHeight(2)
        main_layout.addWidget(line)

        stock_rating_layout = QHBoxLayout()
        stocks_label = QLabel(f"Stocks: {self.stocks}")
        stocks_label.setFont(QFont("Arial", 12))
        rating_label = QLabel(f"Rating: {self.rating}")
        rating_label.setFont(QFont("Arial", 12))
        stock_rating_layout.addWidget(stocks_label)
        stock_rating_layout.addStretch()
        stock_rating_layout.addWidget(rating_label)
        main_layout.addLayout(stock_rating_layout)
        
        # Add seller name (clickable)
        seller_layout = QHBoxLayout()
        seller_label = QLabel("Seller:")
        seller_label.setFont(QFont("Arial", 12))
        
        seller_name = QLabel(self.seller if self.seller else "Shoe Marketplace")
        seller_name.setFont(QFont("Arial", 12, QFont.Bold))
        seller_name.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #e74c3c;
                text-decoration: none;
                padding: 4px 12px;
                border-radius: 15px;
                font-weight: 500;
                border: 1px solid #d62c1a;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            QLabel:hover {
                background-color: #d62c1a;
                cursor: pointer;
                text-decoration: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            }
        """)
        seller_name.mousePressEvent = lambda e: self.view_seller_profile()
        
        seller_layout.addWidget(seller_label)
        seller_layout.addWidget(seller_name)
        seller_layout.addStretch()
        main_layout.addLayout(seller_layout)

        # Size selection
        if getattr(self, 'sizes', []):
            size_label = QLabel("Select Size:")
            self.size_combo = QComboBox()
            self.size_combo.addItems([str(s) for s in self.sizes])
            size_layout = QHBoxLayout()
            size_layout.addWidget(size_label)
            size_layout.addStretch()
            size_layout.addWidget(self.size_combo)
            main_layout.addLayout(size_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: red; background-color: red; height: 2px;")
        line.setFixedHeight(2)
        main_layout.addWidget(line)

        main_layout.addLayout(name_price_layout)
        main_layout.addLayout(stock_rating_layout)

        
        # Product Description
        description_title = QLabel("Item Description")
        description_title.setFont(QFont("Arial", 14, QFont.Bold))
        description_box = QTextEdit()
        description_box.setText(self.description)
        description_box.setReadOnly(True)
        description_box.setFixedHeight(120)
        main_layout.addWidget(description_title)
        main_layout.addWidget(description_box)

        # Chat to Seller Button
        button_layout = QHBoxLayout()
        chat_btn = QPushButton("Chat to Seller")
        chat_btn.setCursor(QCursor(Qt.PointingHandCursor))
        chat_btn.setStyleSheet("background-color: orange; color: white; border-radius: 8px; font-size: 14px;")
        chat_btn.setFixedHeight(40)
        chat_btn.setFixedWidth(120)
        chat_btn.clicked.connect(self.chat_to_seller)  


        # Action Buttons
        add_to_cart_btn = QPushButton("Add to Cart")
        add_to_cart_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_to_cart_btn.setStyleSheet("background-color: red; color: white; border-radius: 8px; font-size: 14px;")
        add_to_cart_btn.setFixedHeight(40)
        add_to_cart_btn.setFixedWidth(120)
        add_to_cart_btn.clicked.connect(self.add_to_cart)


        buy_now_btn = QPushButton("Buy Now")
        buy_now_btn.setCursor(QCursor(Qt.PointingHandCursor))
        buy_now_btn.setStyleSheet("background-color: green; color: white; border-radius: 8px; font-size: 14px;")
        buy_now_btn.setFixedHeight(40)
        buy_now_btn.setFixedWidth(120)
        buy_now_btn.clicked.connect(self.buy_item)
        button_layout.addWidget(chat_btn)
        button_layout.addWidget(add_to_cart_btn)
        button_layout.addWidget(buy_now_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def chat_to_seller(self):
        QMessageBox.information(self, "Chat", f"Starting chat with seller: {self.seller}")

    def add_to_cart(self):
        item = {
            "image": self.image_path,
            "name": self.name,
            "price": self.price,
            "stocks": self.stocks,
            "rating": self.rating,
            "description": self.description,
            "sizes": getattr(self, "sizes", []),
            "size": self.size_combo.currentText() if hasattr(self, "size_combo") else ""
    }

        cart = []
        if os.path.exists(cart_file()):
            with open(cart_file(), "r") as f:
                try:
                    cart = json.load(f)
                except Exception:
                    cart = []
        cart.append(item)
        with open(cart_file(), "w") as f:
            json.dump(cart, f, indent=4)
        QMessageBox.information(self, "Added to Cart", f"{self.name} has been added to your cart!")

    def buy_item(self):
        """Proceed directly to checkout with the selected item."""
        try:
            price_val = float(str(self.price).replace('$', '').strip())
        except Exception:
            price_val = float(self.price) if str(self.price).replace('.','',1).isdigit() else 0.0
        item = {
            "name": self.name,
            "price": price_val,
            "sizes": getattr(self, "sizes", []),
            "size": self.size_combo.currentText() if hasattr(self, "size_combo") else ""
        }
        self.checkout_window = CheckoutUI(self, item)
        self.checkout_window.show()
        self.hide()
        
    def view_seller_profile(self):
        """Open the seller's profile page"""
        seller_name = self.seller if self.seller else "Shoe Marketplace"
        self.seller_profile = SellerProfileUI(seller_name, self.homepage_window)
        self.seller_profile.show()
        self.close()

    def go_back(self):
        self.homepage_window.show()
        self.close()


class SellerProfileUI(QWidget):
    def __init__(self, seller_name, homepage_window):
        super().__init__()
        self.setWindowTitle(f"{seller_name}'s Profile")
        self.setGeometry(100, 100, 360, 700)
        self.setStyleSheet("""
            QWidget { font-family: 'Arial'; background-color: #f5f5f5; }
            QPushButton { 
                background-color: #e74c3c; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
            .header { 
                background-color: #e74c3c; 
                color: white; 
                padding: 15px; 
                font-size: 18px;
                font-weight: bold;
            }
            .seller-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .product-card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                min-width: 150px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .product-name { 
                font-weight: bold; 
                margin: 5px 0;
                color: #333;
            }
            .price {
                color: #e74c3c;
                font-weight: bold;
                font-size: 16px;
            }
            .rating {
                color: #f39c12;
                font-size: 14px;
            }
        """)
        
        self.seller_name = seller_name
        self.homepage_window = homepage_window
        self.products = self.get_seller_products()
        self.seller_profile_setup_ui()

    def seller_profile_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setProperty("class", "header")
        header_layout = QHBoxLayout(header)
        
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.clicked.connect(self.go_back)
        
        title = QLabel(self.seller_name)
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin-left: 10px;
            }
        """)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header.setLayout(header_layout)
        
        # Scroll area for products
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container for products
        container = QWidget()
        self.products_layout = QVBoxLayout(container)
        self.products_layout.setSpacing(15)
        self.products_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add seller info section
        self.add_seller_info()
        
        # Add products section
        self.add_products_section()
        
        scroll.setWidget(container)
        
        # Add all to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def add_seller_info(self):
        # Seller info card
        seller_card = QWidget()
        seller_card.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Seller name and rating
        name_layout = QHBoxLayout()
        name_label = QLabel(self.seller_name)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        # Rating (example: 4.5 stars)
        rating_layout = QHBoxLayout()
        for _ in range(4):  # 4 full stars
            star = QLabel("★")
            star.setStyleSheet("color: #FFD700; font-size: 16px;")
            rating_layout.addWidget(star)
        half_star = QLabel("½")
        half_star.setStyleSheet("color: #FFD700; font-size: 16px;")
        rating_layout.addWidget(half_star)
        rating_layout.addWidget(QLabel("(4.5)"))
        rating_layout.addStretch()
        
        name_layout.addWidget(name_label)
        name_layout.addLayout(rating_layout)
        
        # Seller stats
        stats_layout = QHBoxLayout()
        stats = [
            ("Products", "50+"),
            ("Rating", "4.5/5"),
            ("Joined", "2023")
        ]
        
        stats_layout = QHBoxLayout()
        for stat, value in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout()
            stat_value = QLabel(value)
            stat_value.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #e74c3c;
                }
            """)
            stat_label = QLabel(stat)
            stat_label.setStyleSheet("font-size: 12px; color: #777;")
            
            stat_layout.addWidget(stat_value)
            stat_layout.addWidget(stat_label)
            stat_layout.setAlignment(Qt.AlignCenter)
            stat_widget.setLayout(stat_layout)
            stats_layout.addWidget(stat_widget)
        
        # Add stats to layout
        layout.addLayout(name_layout)
        layout.addLayout(stats_layout)
        
        # Add seller description
        desc = QLabel("""
            Welcome to my shop! I offer high-quality products with fast shipping.
            Feel free to browse my collection and don't hesitate to contact me 
            if you have any questions.
        """)
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            QLabel {
                color: #555;
                font-size: 14px;
                margin-top: 15px;
                line-height: 1.4;
            }
        """)
        
        layout.addWidget(QLabel("About Seller:"))
        layout.addWidget(desc)
        
        # Add to main layout
        self.products_layout.addWidget(seller_card)
    
    def add_products_section(self):
        # Add section title
        section_title = QLabel("Products")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin: 10px 0 5px 0;
            }
        """)
        self.products_layout.addWidget(section_title)
        
        if not self.products:
            no_products = QLabel("No products available from this seller yet.")
            no_products.setStyleSheet("color: #777; font-style: italic;")
            self.products_layout.addWidget(no_products)
            return
            
        # Add products scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 6px;
                background: #f0f0f0;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 3px;
                min-width: 20px;
            }
        """)
        
        # Container for product cards
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 15)
        
        # Add product cards
        for product in self.products:
            product_card = self.create_product_card(product)
            layout.addWidget(product_card)
        
        # Add stretch to push cards to the left
        layout.addStretch()
        
        scroll.setWidget(container)
        self.products_layout.addWidget(scroll)
    
    def create_product_card(self, product):
        card = QWidget()
        card.setFixedWidth(160)
        card.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 10px;
                padding: 12px;
                border: 1px solid #eee;
            }
            QWidget:hover {
                border: 1px solid #e74c3c;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Product image placeholder
        image = QLabel("🛍️")  # Using emoji as placeholder
        image.setAlignment(Qt.AlignCenter)
        image.setFixedHeight(120)
        image.setStyleSheet("""
            QLabel {
                font-size: 40px;
                background: #f9f9f9;
                border-radius: 8px;
                margin-bottom: 5px;
            }
        """)
        
        # Product name
        name = QLabel(product.get('name', 'Product Name'))
        name.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                font-size: 14px;
                margin: 0;
            }
        """)
        name.setWordWrap(True)
        name.setMaximumHeight(40)
        
        # Product price
        price = QLabel(f"${float(product.get('price', 0)):.2f}")
        price.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                font-size: 16px;
                margin: 2px 0;
            }
        """)
        
        # Rating (example)
        rating = QLabel("★★★★☆ 4.2")  # Placeholder rating
        rating.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-size: 12px;
                margin: 2px 0;
            }
        """)
        
        # Add to cart button
        add_to_cart = QPushButton("Add to Cart")
        add_to_cart.setCursor(Qt.PointingHandCursor)
        add_to_cart.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 0;
                margin-top: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        add_to_cart.clicked.connect(lambda _, p=product: self.add_to_cart(p))
        
        # Add seller name (clickable)
        seller_name = product.get('seller', 'Unknown Seller')
        seller_label = QLabel(f"{seller_name}")
        seller_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #e74c3c;
                font-size: 11px;
                margin: 2px 0;
                padding: 4px 8px;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
                border: 1px solid #c0392b;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            QLabel:hover {
                background-color: #c0392b;
                cursor: pointer;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
        """)
        seller_label.mousePressEvent = lambda e: self.view_seller_profile(seller_name)
        
        # Add all to layout
        layout.addWidget(image)
        layout.addWidget(name)
        layout.addWidget(price)
        layout.addWidget(rating)
        layout.addWidget(seller_label)
        layout.addWidget(add_to_cart)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
        layout.addWidget(seller_label)
        layout.addWidget(add_to_cart)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def view_seller_profile(self, seller_name):
        """Open the profile page for the specified seller"""
        if seller_name != self.seller_name:  # Only open if it's a different seller
            self.seller_profile = SellerProfileUI(seller_name, self.homepage_window)
            self.seller_profile.show()
            self.close()
    
    def add_to_cart(self, product):
        # This method would handle adding the product to cart
        # You can implement cart functionality here
        print(f"Added to cart: {product.get('name')}")
    def get_seller_products(self):
        try:
            if os.path.exists("products.json"):
                with open("products.json", "r") as f:
                    all_products = json.load(f)
                # Filter products by seller name and limit to 10 products
                seller_products = [p for p in all_products if p.get("seller") == self.seller_name]
                return seller_products[:10]  # Return up to 10 products
        except Exception as e:
            print(f"Error loading products: {e}")
        return []
    
    def go_back(self):
        self.homepage_window.show()
        self.close()


class InventoryCartUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART")
        self.setGeometry(100, 100, 360, 600)
        self.homepage_window = homepage_window
        self.edit_mode = False
        self.setStyleSheet("background-color: white;")
        self.cart_setup_ui()

    #Setup ng Add to Cart
    def cart_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        top_bar = QHBoxLayout()

        back_btn = QPushButton("<-")
        back_btn.setStyleSheet("color: white;"
                               "font-size: 18px;"
                               "background: red;"
                               "border: none;"
                               )
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.clicked.connect(self.go_back)
        
        title = QLabel("Inventory Cart")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: red;")

        #Edit Button (Not Fixed)
        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(QCursor(Qt.PointingHandCursor)) 
        edit_btn.clicked.connect(self.toggle_edit_mode)
        edit_btn.setStyleSheet("color: red;"
                               "background: none;"
                               "border: none;")
        

        top_bar.addWidget(back_btn)
        top_bar.addStretch() 
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(edit_btn)

        main_layout.addLayout(top_bar)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search item...")
        self.search_input.setFixedHeight(30)
        self.search_input.textChanged.connect(self.filter_itemization)  
        main_layout.addWidget(self.search_input)

        
        self.all_items = self.get_cart_item()

        
        self.item_list_layout = QVBoxLayout()
        main_layout.addLayout(self.item_list_layout)

       
        self.display_itemization(self.all_items)

        #Proceed to Checkout Boton
        checkout_btn = QPushButton("Proceed to Checkout")
        checkout_btn.setCursor(QCursor(Qt.PointingHandCursor)) 
        checkout_btn.setFixedHeight(40)
        checkout_btn.setStyleSheet("""
                            QPushButton {
                                    background-color: red;
                                    color: white;
                                    font-size: 14px;
                                    border-radius: 10px;
          }
                            QPushButton:hover {
                                    background: #8B0000;
                                    color: white;
        }                                           
    """)
        checkout_btn.clicked.connect(self.open_checkout)
        main_layout.addStretch()
        main_layout.addWidget(checkout_btn)

        self.setLayout(main_layout)
    
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.display_itemization(self.all_items)

    #Creating some Items
    def create_cart_item(self, item):
        image_path, name, price, marketplace = item

        item_layout = QVBoxLayout()
        top_row = QHBoxLayout()

   
        img_label = QLabel()
        img_label.setPixmap(QPixmap(image_path).scaled(60, 60, Qt.KeepAspectRatio))

        #Display ng Name at Price
        name_price_label = QLabel(f"{name} - ${price}")
        name_price_label.setStyleSheet("font-weight: bold; font-size: 13px;")

        qty_layout = QHBoxLayout()
        qty = {"value": 1}
        qty_label = QLabel(str(qty["value"]))
        qty_label.setFixedWidth(20)
        qty_label.setAlignment(Qt.AlignCenter)

        minus_btn = QPushButton("-")
        plus_btn = QPushButton("+")
        for btn in (minus_btn, plus_btn):
            btn.setFixedSize(25, 25)
            btn.setStyleSheet("border: 1px solid red; border-radius: 10px;")

        #Adding Some Quantity
        def increase_qty():
            qty["value"] += 1
            qty_label.setText(str(qty["value"]))

        #Magbabawas ng Quantity
        def decrease_qty():
            if qty["value"] > 1:  
                qty["value"] -= 1
                qty_label.setText(str(qty["value"]))

        plus_btn.clicked.connect(increase_qty)
        minus_btn.clicked.connect(decrease_qty)

        qty_layout.addWidget(minus_btn)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(plus_btn)

        top_row.addWidget(img_label)
        top_row.addWidget(name_price_label)
        top_row.addStretch()
        top_row.addLayout(qty_layout)

        if self.edit_mode:
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("background-color: red; color: white; border-radius: 8px; font-size: 12px;")
            remove_btn.setFixedHeight(30)
            remove_btn.setCursor(QCursor(Qt.PointingHandCursor))
            remove_btn.clicked.connect(lambda: self.remove_item_from_cart(name))
            top_row.addWidget(remove_btn)


        market_label = QLabel(f"🛒 {marketplace}")
        market_label.setStyleSheet("color: red; font-size: 11px;")

        item_layout.addLayout(top_row)
        item_layout.addWidget(market_label)

        return item_layout
    
    #Removing an Item from Cart
    def remove_item_from_cart(self, name):
        if os.path.exists(cart_file()):
            with open(cart_file(), "r") as f:
                cart = json.load(f)
            cart = [item for item in cart if item["name"] != name]
            with open(cart_file(), "w") as f:
                json.dump(cart, f, indent=4)
        self.all_items = self.get_cart_item()
        self.display_itemization(self.all_items)

    def display_itemization(self, items):
        while self.item_list_layout.count():
            item = self.item_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                layout = item.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())
            
            layout.deleteLater()
    # Add new items
        for item in items:
            self.item_list_layout.addLayout(self.create_cart_item(item))


    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
        layout.deleteLater()

    def filter_itemization(self):
        keyword = self.search_input.text().lower()
        filtered = [item for item in self.all_items if keyword in item[1].lower()] 
        self.display_itemization(filtered) 

    def going_back(self):
        self.homepage_window.show()
        self.close()

    #Your Carts that you add
    def get_cart_item(self):
        if os.path.exists(cart_file()):
            with open(cart_file(), "r") as f:
                try:
                    cart = json.load(f)
                    return [(item["image"], item["name"], item["price"], "Marketplace") for item in cart]
                except Exception:
                    return []
        return []

    #Proceeding to Checkout
    def open_checkout(self):
        self.open_checkout_window = CheckoutUI(self) 
        self.open_checkout_window.show()
        self.close()

    #Going Back to Home Page
    def go_back(self):
        self.homepage_window.show()
        self.close()



products = [
    {"name": "Shoes", "price": 100, "stock": 20, "rating": 3},
    {"name": "Laptop", "price": 500, "stock": 50, "rating": 4.5},
    {"name": "Phone", "price": 1000, "stock": 50, "rating": 5}
]

class ProductItem(QWidget):
    def __init__(self, product, display_key):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(QLabel(product['name']))
        layout.addStretch()
        layout.addWidget(QLabel(f"{display_key.capitalize()}: {product[display_key]}"))
        self.setLayout(layout)
        self.setStyleSheet("border: 1px solid red; border-radius: 10px; padding: 10px;")


class ProductWindow(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Product Listing")
        self.setGeometry(100, 100, 360, 600)
        self.homepage_window = homepage_window
        self.current_filter = "price"

        self.layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for an item")
        self.layout.addWidget(self.search_bar)

        # Filter buttons
        filter_layout = QHBoxLayout()
        self.price_btn = QPushButton("Filter by Price")
        self.stock_btn = QPushButton("Filter by Stocks")
        self.rating_btn = QPushButton("Filter by Rating")

        self.price_btn.clicked.connect(lambda: self.set_filter("price"))
        self.stock_btn.clicked.connect(lambda: self.set_filter("stock"))
        self.rating_btn.clicked.connect(lambda: self.set_filter("rating"))

        filter_layout.addWidget(self.price_btn)
        filter_layout.addWidget(self.stock_btn)
        filter_layout.addWidget(self.rating_btn)
        self.layout.addLayout(filter_layout)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Lowest to Highest", "Highest to Lowest"])
        self.sort_combo.currentTextChanged.connect(self.update_products)
        self.layout.addWidget(self.sort_combo)

        # Product list
        self.product_list = QListWidget()
        self.layout.addWidget(self.product_list)

        # Back button to go back to HomePage
        back_btn = QPushButton("<- Back to Home")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("background-color: red; color: white; font-size: 14px; border-radius: 10px;")
        back_btn.clicked.connect(self.go_back)
        self.layout.addWidget(back_btn)

        self.setLayout(self.layout)
        self.update_products()

    def set_filter(self, filter_type):
        self.current_filter = filter_type
        self.update_products()

    def update_products(self):
        self.product_list.clear()
        reverse = self.sort_combo.currentText() == "Highest to Lowest"
        sorted_items = sorted(products, key=lambda x: x[self.current_filter], reverse=reverse)

        for prod in sorted_items:
            item = QListWidgetItem()
            widget = ProductItem(prod, self.current_filter)
            item.setSizeHint(widget.sizeHint())
            self.product_list.addItem(item)
            self.product_list.setItemWidget(item, widget)

    def go_back(self):
        self.homepage_window.show()
        self.close()

#Summary View Window
class SummaryUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Summary")
        self.setGeometry(100, 100, 360, 600)
        self.homepage_window = homepage_window
        self.setStyleSheet("background-color: white;")
        self.summary_setup_ui()

    def summary_setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Summary View")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: red;")
        layout.addWidget(title)

        total_users_lbl = QLabel(f"Total Users: {db.total_users()}")
        total_products_lbl = QLabel(f"Total Products: {db.total_products()}")
        top_name, top_price = db.top_product_by_price()
        top_product_lbl = QLabel(f"Top Product (Highest Price): {top_name if top_name else 'N/A'} {f'($ {top_price})' if top_price else ''}")

        for lbl in (total_users_lbl, total_products_lbl, top_product_lbl):
            lbl.setFont(QFont("Arial", 14))
            lbl.setStyleSheet("color: black;")
            layout.addWidget(lbl)

        back_btn = QPushButton("<- Back to Home")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("background-color: red; color: white; font-size: 14px; border-radius: 10px;")
        back_btn.clicked.connect(self.go_back)
        layout.addStretch()
        layout.addWidget(back_btn)
        self.setLayout(layout)

    def go_back(self):
        self.homepage_window.show()
        self.close()

# ---- Account Security (Change Password) ----
class AccountSecurityUI(QWidget):
    def __init__(self, settings_window, username):
        super().__init__()
        self.settings_window = settings_window
        self.username = username
        self.setWindowTitle("Change Password")
        self.setGeometry(100, 100, 350, 600)
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        back_btn = QPushButton("<- Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Change Password")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.current_input = QLineEdit()
        self.current_input.setPlaceholderText("Current Password")
        self.current_input.setEchoMode(QLineEdit.Password)
        self.new_input = QLineEdit()
        self.new_input.setPlaceholderText("New Password")
        self.new_input.setEchoMode(QLineEdit.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm New Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        for w in (self.current_input, self.new_input, self.confirm_input):
            w.setFixedHeight(40)
            w.setStyleSheet("border:1px solid #ccc; border-radius:10px; padding:0 10px;")
            layout.addWidget(w)

        save_btn = QPushButton("Save")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px; height:40px;")
        save_btn.clicked.connect(self.save_password)
        layout.addWidget(save_btn)
        layout.addStretch()
        self.setLayout(layout)

    def go_back(self):
        self.settings_window.show()
        self.close()

    def save_password(self):
        cur = self.current_input.text().strip()
        new = self.new_input.text().strip()
        conf = self.confirm_input.text().strip()
        if not cur or not new or not conf:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        if not db.validate_user(self.username, cur):
            QMessageBox.warning(self, "Error", "Current password incorrect")
            return
        if new != conf:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
        db.update_password(self.username, new)
        QMessageBox.information(self, "Success", "Password updated successfully")
        self.go_back()

# ---- Bank Accounts UI ----
class BankAccountsUI(QWidget):
    DATA_FILE = "bank_accounts.json"
    def __init__(self, settings_window):
        super().__init__()
        self.settings_window = settings_window
        self.setWindowTitle("Bank Accounts")
        self.setGeometry(100, 100, 350, 600)
        self.setStyleSheet("background-color: white;")
        self.load_accounts()
        self.setup_ui()

    def load_accounts(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    self.accounts = json.load(f)
            except Exception:
                self.accounts = []
        else:
            self.accounts = []

    def save_accounts(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump(self.accounts, f)

    def setup_ui(self):
        layout = QVBoxLayout()
        back_btn = QPushButton("<- Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Bank Accounts")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.list_widget = QListWidget()
        for acc in self.accounts:
            self.list_widget.addItem(f"{acc['bank']} - {acc['number']}")
        layout.addWidget(self.list_widget)

        add_btn = QPushButton("Add Account")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        add_btn.clicked.connect(self.add_account_dialog)
        layout.addWidget(add_btn)
        layout.addStretch()
        self.setLayout(layout)

    def go_back(self):
        self.settings_window.show()
        self.close()

    def add_account_dialog(self):
        bank, ok1 = QInputDialog.getText(self, "Bank", "Enter Bank Name:")
        if not ok1 or not bank.strip():
            return
        number, ok2 = QInputDialog.getText(self, "Account Number", "Enter Account Number:")
        if not ok2 or not number.strip():
            return
        self.accounts.append({"bank": bank.strip(), "number": number.strip()})
        self.list_widget.addItem(f"{bank.strip()} - {number.strip()}")
        self.save_accounts()

# ---- Switch Account Confirmation UI ----
class SwitchAccountUI(QWidget):
    def __init__(self, settings_window, login_window, homepage_window):
        super().__init__()
        self.settings_window = settings_window
        self.login_window = login_window
        self.homepage_window = homepage_window
        self.setWindowTitle("Switch Account")
        self.setGeometry(100, 100, 300, 200)
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()

        label = QLabel("Switch account")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        admin_btn = QPushButton("Admin")
        admin_btn.setCursor(QCursor(Qt.PointingHandCursor))
        admin_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px; height:35px;")
        admin_btn.clicked.connect(lambda: self.ask_password_and_login("admin"))

        user_btn = QPushButton("User")
        user_btn.setCursor(QCursor(Qt.PointingHandCursor))
        user_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px; height:35px;")
        user_btn.clicked.connect(lambda: self.ask_password_and_login("user"))

        logout_btn = QPushButton("Logout & Cancel")
        logout_btn.setCursor(QCursor(Qt.PointingHandCursor))
        logout_btn.clicked.connect(self.confirm_switch)

        cancel_btn = QPushButton("Back")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.clicked.connect(self.cancel)

        layout.addWidget(admin_btn)
        layout.addWidget(user_btn)
        layout.addWidget(logout_btn)
        layout.addWidget(cancel_btn)
        self.setLayout(layout)

    def ask_password_and_login(self, username):
        pwd, ok = QInputDialog.getText(self, "Enter Password", f"Enter password for {username}:", QLineEdit.Password)
        if not ok:
            return
        if not db.validate_user(username, pwd):
            QMessageBox.warning(self, "Invalid", "Incorrect password.")
            return
        # ensure remember_me cleared
        if os.path.exists("remember_me.json"):
            try:
                os.remove("remember_me.json")
            except Exception:
                pass
        self.login_window.username_input.setText(username)
        self.login_window.password_input.setText(pwd)
        self.login_window.login_validation()
        self.settings_window.close()
        self.close()

    def confirm_switch(self):
        if os.path.exists("remember_me.json"):
            try:
                os.remove("remember_me.json")
            except Exception:
                pass
        self.settings_window.close()
        self.homepage_window.close()
        self.login_window.show()
        self.close()

    def cancel(self):
        self.settings_window.show()
        self.close()

# ---- Generic Info Page for settings placeholders ----
class InfoPageUI(QWidget):
    def __init__(self, title_text, settings_window):
        super().__init__()
        self.settings_window = settings_window
        self.setWindowTitle(f"KKKMART - {title_text}")
        self.setGeometry(100, 100, 350, 600)
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setSpacing(15)

        back_btn = QPushButton("<- Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        title = QLabel(title_text)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black;")
        layout.addWidget(title)

        placeholder = QLabel(f"This '{title_text}' page is under construction.")
        placeholder.setFont(QFont("Arial", 12))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(placeholder)
        layout.addStretch()
        self.setLayout(layout)

    def go_back(self):
        self.settings_window.show()
        self.close()

#Checkout Window
class CheckoutUI(QWidget):
    def __init__(self, previous_window, item=None):  
        super().__init__()
        self.previous_window = previous_window
        self.cart_window = previous_window  # maintain existing variable usage
        self.item = item
        self.setWindowTitle("KKKMART - Checkout")
        self.setGeometry(100, 100, 360, 600)
        self.setStyleSheet("background-color: white;")
        self.checkout_setup_ui()
    
    #Setup ng Checkout
    def checkout_setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("CHECK OUT")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: red;"
                            "margin-bottom: 20px;"
                            )
        layout.addWidget(title, alignment = Qt.AlignCenter)

        # Size selection in checkout
        if getattr(self, 'item', None):
            sizes_list = self.item.get('sizes', [])
        else:
            sizes_list = []
        if not sizes_list:
            # Attempt to fetch sizes from products.json based on item name (or first cart item)
            prod_name = None
            if getattr(self, 'item', None):
                prod_name = self.item.get('name')
            else:
                # try cart.json first item
                cart_file = 'cart.json'
                if os.path.exists(cart_file):
                    try:
                        with open(cart_file, 'r') as cf:
                            cart_items = json.load(cf)
                        if cart_items:
                            prod_name = cart_items[0].get('name')
                    except Exception:
                        pass
            if prod_name and os.path.exists('products.json'):
                try:
                    with open('products.json', 'r') as pf:
                        prods = json.load(pf)
                    for prod in prods:
                        if prod.get('name', '').strip().lower() == prod_name.strip().lower():
                            sizes_list = prod.get('size', prod.get('sizes', []))
                            break
                except Exception:
                    sizes_list = []
            # fallback default if still empty
            if not sizes_list:
                sizes_list = ["XS", "S", "M", "L", "XL"]
        size_label = QLabel("Select Size:")
        self.size_combo = QComboBox()
        self.size_combo.addItems([str(s) for s in sizes_list])
        # Pre-select existing size if provided
        if getattr(self, 'item', None) and self.item.get('size'):
            try:
                idx = sizes_list.index(self.item['size'])
                self.size_combo.setCurrentIndex(idx)
            except ValueError:
                pass
        size_layout = QHBoxLayout()
        size_layout.addWidget(size_label)
        size_layout.addStretch()
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)

        coupons_layout = QVBoxLayout() 
        
        avail_label = QLabel("Available Coupons:")
        avail_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        coupons_layout.addWidget(avail_label)

        
        self.coupon1 = QPushButton("10% OFF - APPLY")
        self.coupon2 = QPushButton("FREE SHIPPING - APPLY")
        self.coupon1.setCursor(QCursor(Qt.PointingHandCursor))
        self.coupon2.setCursor(QCursor(Qt.PointingHandCursor))

        for btn in [self.coupon1, self.coupon2]:
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 8px;
                    text-align: left;
                    margin: 5px 0;
                }
                QPushButton:hover {
                    border-color: red;
                }
            """)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            coupons_layout.addWidget(btn)
        self.coupon1.clicked.connect(lambda: self.apply_coupon_code("10OFF"))
        self.coupon2.clicked.connect(lambda: self.apply_coupon_code("FREESHIP"))

        redeem_label = QLabel("Redeem Coupons:")
        redeem_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        coupons_layout.addWidget(redeem_label)

        self.coupon_input = QLineEdit()
        self.coupon_input.setPlaceholderText("Enter coupon code...")
        self.coupon_input.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ccc;")
        coupons_layout.addWidget(self.coupon_input)

        layout.addLayout(coupons_layout)

        apply_btn = QPushButton("Apply Coupon")
        apply_btn.clicked.connect(self.apply_coupon_from_input)
        apply_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: red;
                                    color: white;
                                    font-size: 14px;
                                    padding: 8px;
                                    border-radius: 5px;
                                } 
                                QPushButton:hover { 
                                    background-color: #8B0000;
                                    color: white;
                                }
                                 """)      
        apply_btn.setCursor(QCursor(Qt.PointingHandCursor))
        coupons_layout.addWidget(apply_btn, alignment=Qt.AlignRight)

        payment_group = QVBoxLayout()
        payment_title = QLabel("Payment Method")
        payment_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px;")

        self.payment_radio1 = QRadioButton("Online Payment")
        self.payment_radio2 = QRadioButton("Bank Payment")
        self.payment_radio3= QRadioButton("Cash On Delivery")
        for radio in [self.payment_radio1, self.payment_radio2, self.payment_radio3]:
            radio.setStyleSheet("margin: 5px; font-size: 13px;")

        payment_group.addWidget(payment_title)
        payment_group.addWidget(self.payment_radio1)
        payment_group.addWidget(self.payment_radio2)
        payment_group.addWidget(self.payment_radio3)
        layout.addLayout(payment_group)

        details_group = QVBoxLayout()
        details_title = QLabel("Payment Details")
        details_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px;")

        # Calculate merchandise subtotal
        if getattr(self, 'item', None):
            self.subtotal_value = float(self.item.get('price', 0))
        else:
            self.subtotal_value = 100  # TODO: compute from cart items when integrated
        self.subtotal_label = QLabel(f"Merchandise Subtotal: ${self.subtotal_value}")
        self.discount_label = QLabel("Coupons Discount Subtotal: $0")
        self.total_label = QLabel(f"Total Payment: ${self.subtotal_value}")

        for label in [self.subtotal_label, self.discount_label, self.total_label]:
            label.setStyleSheet("margin: 5px; font-size: 13px;")

        details_group.addWidget(details_title)
        details_group.addWidget(self.subtotal_label)
        details_group.addWidget(self.discount_label)
        details_group.addWidget(self.total_label)
        layout.addLayout(details_group)

        order_btn = QPushButton("Place Order")
        order_btn.setStyleSheet("""
                    QPushButton {
                        background-color: red;
                        color: white;
                        font-size: 16px;
                        padding: 12px;
                        border-radius: 10px;
                        margin-top: 20px;                                 
         } 
                    QPushButton:hover {
                        background-color: #8B0000;
                        color: white;
        }                                        
    """)
        order_btn.setCursor(QCursor(Qt.PointingHandCursor))
        order_btn.clicked.connect(self.place_order)
        layout.addWidget(order_btn, alignment = Qt.AlignCenter)

        back_btn = QPushButton("<-- Back")
        back_btn.setStyleSheet("color: red; border: none; font-size 12px;") 
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.clicked.connect(self.back_to_cart)
        layout.addWidget(back_btn, alignment = Qt.AlignLeft | Qt.AlignTop) 

        self.setLayout(layout)

    def show_payment_confirmation(self, method):
        QMessageBox.information(
            self,
            "Payment Confirmation",
            f"Your payment via {method} was successful!\nThank you for your purchase."
        )

    def complete_payment(self, method):
        self.show_payment_confirmation(method)

    def apply_coupon_code(self, code):
        code = code.upper()
        subtotal = self.subtotal_value
        if code in COUPONS:
            coupon = COUPONS[code]
            if subtotal >= coupon.get("min_spend", 0):
                discount = subtotal * coupon["discount"]
                if "max_discount" in coupon:
                    discount = min(discount, coupon["max_discount"])
                self.discount_label.setText(f"Coupons Discount Subtotal: ${discount:.2f}")
                self.total_label.setText(f"Total Payment: ${subtotal - discount:.2f}")
                QMessageBox.information(self, "Coupon Applied", f"{coupon['desc']} applied!")
            else:
                QMessageBox.warning(self, "Coupon Not Applied", f"Minimum spend not met for {code}.")
        else:
            QMessageBox.warning(self, "Invalid Coupon", "This coupon code is not valid.")

    def apply_coupon_from_input(self):
        code = self.coupon_input.text().strip().upper()
        self.apply_coupon_code(code)


    #Placing your order
    def place_order(self):
        """Validate payment, save order, show confirmation and order history."""
        # Determine selected payment method
        if self.payment_radio1.isChecked():
            method = "Online"
        elif self.payment_radio2.isChecked():
            method = "Bank"
        elif self.payment_radio3.isChecked():
            method = "Cash On Delivery"
        else:
            QMessageBox.warning(self, "No Payment Method", "Please select a payment method.")
            return

        # Show payment success dialog
        self.show_payment_confirmation(method)

        # Persist the order
        self.save_order(method)
        # Record a notification for this order
        save_notification(f"Your order has been placed successfully on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Show order history window
        self.order_history_window = OrderHistoryUI(self)
        self.order_history_window.show()
        self.hide()

    def save_order(self, method):
        """Save the completed order into orders.json for history."""
        order_file = "orders.json"
        orders = []
        if os.path.exists(order_file):
            try:
                with open(order_file, "r") as f:
                    orders = json.load(f)
            except Exception:
                orders = []

        # Add selected size to item before saving
        if getattr(self, 'item', None) and hasattr(self, 'size_combo'):
            self.item['selected_size'] = self.size_combo.currentText()

        # Build order record
        order_record = {
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method": method,
            "subtotal": self.subtotal_value,
            "discount": float(self.discount_label.text().split("$")[-1]),
            "total": float(self.total_label.text().split("$")[-1]),
            "items": [self.item] if getattr(self, 'item', None) else self.get_cart_items()
        }
        orders.append(order_record)
        with open(order_file, "w") as f:
            json.dump(orders, f, indent=4)

        # Reduce stocks based on purchased items
        self.reduce_stocks(order_record["items"])

    def get_cart_items(self):
        """Return items currently in this user's cart file."""
        file_path = cart_file()
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def reduce_stocks(self, items):
        """Decrease stock count in both products.json and database according to purchased items."""
        products_file = "products.json"
        if not os.path.exists(products_file):
            return
            
        # Count quantities per item name
        quantity_map = {}
        for itm in items:
            name = itm.get("name", "").strip().lower()
            quantity_map[name] = quantity_map.get(name, 0) + 1
            
        # Update database first
        conn = None
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            for product_name, quantity in quantity_map.items():
                # Update database stock
                cursor.execute("""
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND stock >= ?
                """, (quantity, product_name, quantity))
                
            conn.commit()
            
        except Exception as e:
            print(f"Error updating database stock: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        
        # Then update JSON file
        try:
            with open(products_file, "r") as f:
                products = json.load(f)
                
            changed = False
            for prod in products:
                prod_name = prod.get("name", "").strip().lower()
                if prod_name in quantity_map:
                    try:
                        current_stock = int(prod.get("stocks", prod.get("stock", 0)))
                        new_stock = max(current_stock - quantity_map[prod_name], 0)
                        if new_stock != current_stock:
                            if "stocks" in prod:
                                prod["stocks"] = str(new_stock)
                            else:
                                prod["stock"] = str(new_stock)
                            changed = True
                    except ValueError:
                        continue
                        
            if changed:
                with open(products_file, "w") as f:
                    json.dump(products, f, indent=4)
                    
        except Exception as e:
            print(f"Error updating JSON stock: {e}")

    def place_order(self):
    # Validate payment method selection
        if self.payment_radio1.isChecked():
            method = "Online"
        # Optionally, validate online payment details here
        elif self.payment_radio2.isChecked():
            method = "Bank"
        # Optionally, validate bank details here
        elif self.payment_radio3.isChecked():
            method = "Cash On Delivery"
        else:
            QMessageBox.warning(self, "No Payment Method", "Please select a payment method.")
            return

    # If all validations pass, finalize order
        self.show_payment_confirmation(method)
        # Save order and return to homepage
        self.save_order(method)
        self.go_home_after_order()


    def go_home_after_order(self):
        """Navigate back to the main HomePage after successful purchase."""
        target = None
        if hasattr(self.previous_window, 'homepage_window'):
            target = self.previous_window.homepage_window
        elif hasattr(self.previous_window, 'previous_window') and hasattr(self.previous_window.previous_window,'homepage_window'):
            target = self.previous_window.previous_window.homepage_window
        if target is None:
            target = self.previous_window
        target.show()
        self.close()

    #Going Back to cart window
    def back_to_cart(self):
        self.cart_window.show()
        self.close()


class OrderHistoryUI(QWidget):
    def __init__(self, previous_window):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("KKKMART - Order History")
        self.setGeometry(100, 100, 400, 700)  # Slightly larger for better spacing
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QWidget {
                background-color: #f8f9fa;
            }
            QFrame#orderCard {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QLabel#orderTitle {
                color: #2d3436;
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#orderDate {
                color: #636e72;
                font-size: 12px;
            }
            QLabel#orderPrice {
                color: #00b894;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#orderStatus {
                color: white;
                font-size: 11px;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 10px;
                background: #00b894;
            }
            QPushButton#backButton {
                background: transparent;
                border: none;
                color: #2d3436;
                font-size: 18px;
                padding: 8px;
                border-radius: 20px;
            }
            QPushButton#backButton:hover {
                background: #f1f2f6;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #b2bec3;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.build_ui()

    def build_ui(self):
        """Create Order History page with scrollable list of past orders."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(0)

        # ---- Top Bar ----
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 15)
        
        # Back button with icon
        back_btn = QPushButton("←")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setObjectName("backButton")
        back_btn.setFixedSize(40, 40)
        back_btn.clicked.connect(self.go_back)
        
        # Page title
        title = QLabel("Order History")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 5px;
        """)
        
        # Subtitle
        subtitle = QLabel("Your recent purchases")
        subtitle.setStyleSheet("color: #636e72; font-size: 14px;")
        
        # Add to top bar
        text_layout = QVBoxLayout()
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        text_layout.setSpacing(0)
        
        top_bar.addWidget(back_btn, alignment=Qt.AlignLeft | Qt.AlignTop)
        top_bar.addSpacing(10)
        top_bar.addLayout(text_layout)
        top_bar.addStretch()
        
        main_layout.addLayout(top_bar)
        
        # Add spacing
        main_layout.addSpacing(10)
        
        # ---- Scroll Area for orders ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        orders_layout = QVBoxLayout(container)
        orders_layout.setContentsMargins(0, 0, 5, 0)  # Right padding for scrollbar
        orders_layout.setSpacing(15)
        
        # Load orders
        orders = self.load_orders()
        
        if not orders:
            # Empty state
            empty_container = QWidget()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setContentsMargins(0, 50, 0, 50)
            
            icon = QLabel("📦")
            icon.setStyleSheet("font-size: 50px; text-align: center;")
            icon.setAlignment(Qt.AlignCenter)
            
            empty_text = QLabel("No orders yet")
            empty_text.setStyleSheet("""
                font-size: 18px;
                font-weight: 600;
                color: #2d3436;
                text-align: center;
                margin: 10px 0 5px 0;
            """)
            
            empty_subtext = QLabel("Your completed orders will appear here")
            empty_subtext.setStyleSheet("""
                font-size: 14px;
                color: #636e72;
                text-align: center;
            """)
            
            empty_layout.addWidget(icon)
            empty_layout.addWidget(empty_text)
            empty_layout.addWidget(empty_subtext)
            empty_layout.addStretch()
            
            orders_layout.addWidget(empty_container)
        else:
            # Add orders in reverse chronological order (newest first)
            for order in reversed(orders):
                self.add_order_card(orders_layout, order)
        
        orders_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def add_order_card(self, layout, order):
        """Create and add a single order card to the layout"""
        # Main card container
        card = QFrame()
        card.setObjectName("orderCard")
        card.setMinimumHeight(120)
        
        # Main layout for the card
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Top row - Order number and date
        top_row = QHBoxLayout()
        
        order_title = QLabel(f"Order #{order.get('order_id', 'N/A')}")
        order_title.setObjectName("orderTitle")
        
        order_date = QLabel(order.get('datetime', 'No date'))
        order_date.setObjectName("orderDate")
        
        top_row.addWidget(order_title)
        top_row.addStretch()
        top_row.addWidget(order_date)
        
        # Middle row - Items preview
        items = order.get('items', [])
        items_text = ", ".join([i.get('name', '')[:20] + ('...' if len(i.get('name', '')) > 20 else '') 
                              for i in items[:2]])  # Show first 2 items
        if len(items) > 2:
            items_text += f" +{len(items) - 2} more"
            
        items_label = QLabel(items_text if items else "No items")
        items_label.setStyleSheet("""
            color: #636e72;
            font-size: 13px;
            padding: 5px 0;
        """)
        items_label.setWordWrap(True)
        
        # Bottom row - Price and status
        bottom_row = QHBoxLayout()
        
        total = float(order.get('total', 0))
        total_label = QLabel(f"${total:.2f}")
        total_label.setObjectName("orderPrice")
        
        status = QLabel("Delivered")
        status.setObjectName("orderStatus")
        
        bottom_row.addWidget(total_label, alignment=Qt.AlignLeft)
        bottom_row.addStretch()
        bottom_row.addWidget(status, alignment=Qt.AlignRight)
        
        # Add all rows to card
        card_layout.addLayout(top_row)
        card_layout.addWidget(items_label)
        card_layout.addLayout(bottom_row)
        
        # Add card to layout
        layout.addWidget(card)

    def load_orders(self):
        """Load orders from JSON file with error handling"""
        try:
            if os.path.exists("orders.json"):
                with open("orders.json", "r") as f:
                    orders = json.load(f)
                    # Ensure each order has an ID if missing
                    for i, order in enumerate(orders, 1):
                        if 'order_id' not in order:
                            order['order_id'] = f"{i:04d}"
                    return orders
        except Exception as e:
            print(f"Error loading orders: {e}")
        return []

    def go_back(self):
        """Return to the previous window"""
        if hasattr(self.previous_window, 'show'):
            self.previous_window.show()
        self.close()

# Coupon Window
class CouponsUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Coupons")
        self.setGeometry(100, 100, 400, 700)
        self.homepage_window = homepage_window
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        self.coupons_setup_ui()

    def darken_color(self, hex_color, percent):
        """Darken a hex color by a given percentage (0-100)."""
        # Remove the '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate darkening factor (0-1)
        factor = 1 - (percent / 100.0)
        
        # Apply darkening to each RGB component
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def coupons_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top Bar with Back Button and Title
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 10)

        back_btn = QPushButton("←")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background: #ff4757;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                width: 40px;
                height: 40px;
                padding: 0;
            }
            QPushButton:hover {
                background: #ff6b81;
            }
        """)
        back_btn.clicked.connect(self.go_back)

        title = QLabel("My Coupons")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2f3542;")

        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(QLabel(""))  # Empty label for balance

        main_layout.addLayout(top_bar)

        # Voucher Code Redemption
        redemption_frame = QFrame()
        redemption_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 15px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        redemption_layout = QVBoxLayout(redemption_frame)
        
        redemption_label = QLabel("Redeem Voucher")
        redemption_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        redemption_label.setStyleSheet("color: #2f3542; margin-bottom: 10px;")
        
        input_layout = QHBoxLayout()
        
        self.redemption_input = QLineEdit()
        self.redemption_input.setPlaceholderText("Enter voucher code")
        self.redemption_input.setFixedHeight(45)
        self.redemption_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe4ea;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
                color: #2f3542;
            }
            QLineEdit:focus {
                border: 2px solid #ff4757;
            }
        """)
        
        redeem_btn = QPushButton("Apply")
        redeem_btn.setFixedSize(100, 45)
        redeem_btn.setCursor(QCursor(Qt.PointingHandCursor))
        redeem_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff4757, stop:1 #ff6b81);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #ff6b81, #ff8fa3);
            }
            QPushButton:pressed {
                background: #ff4757;
            }
        """)
        redeem_btn.clicked.connect(self.redeem_coupon)
        
        input_layout.addWidget(self.redemption_input)
        input_layout.addWidget(redeem_btn)
        
        redemption_layout.addWidget(redemption_label)
        redemption_layout.addLayout(input_layout)
        
        main_layout.addWidget(redemption_frame)
        
        # Available Coupons Section
        available_label = QLabel("Available Coupons")
        available_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        available_label.setStyleSheet("color: #2f3542; margin: 10px 0;")
        main_layout.addWidget(available_label)
        
        # Scroll Area for Coupons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #a4b0be;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        
        # Coupons List
        coupons_data = [
            {"code": "50OFF", "title": "50% Off (Max $50)", "min_spend": "$0", "expiring": "23h 59m", "color": "#ff6b81"},
            {"code": "15OFF", "title": "15% Off (Max $150)", "min_spend": "$200", "expiring": "1d 12h", "color": "#2ed573"},
            {"code": "20OFF", "title": "20% Off (Max $100)", "min_spend": "$300", "expiring": "2d 5h", "color": "ff7f50"},
            {"code": "10OFF", "title": "10% Off All Items", "min_spend": "$0", "expiring": "3d 0h", "color": "#ffa502"},
            {"code": "FREESHIP", "title": "Free Shipping", "min_spend": "$0", "expiring": "5d 6h", "color": "#1e90ff"},
        ]

        # Create coupon cards
        for coupon in coupons_data:
            coupon_frame = QFrame()
            coupon_frame.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 15px;
                    border-left: 6px solid {coupon['color']};
                    padding: 0;
                }}
            """)
            
            # Add hover effect using event filter
            coupon_frame.enterEvent = lambda e, f=coupon_frame: f.setStyleSheet(f"""
                QFrame {{
                    background: #ffffff;
                    border-radius: 15px;
                    border-left: 6px solid {coupon['color']};
                    padding: 0;
                    border-top: 1px solid #e0e0e0;
                    border-right: 1px solid #e0e0e0;
                    border-bottom: 1px solid #e0e0e0;
                }}
            """)
            coupon_frame.leaveEvent = lambda e, f=coupon_frame, c=coupon: f.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 15px;
                    border-left: 6px solid {c['color']};
                    padding: 0;
                }}
            """)
            
            coupon_layout = QVBoxLayout(coupon_frame)
            coupon_layout.setContentsMargins(20, 20, 20, 20)
            coupon_layout.setSpacing(10)
            
            # Top row with title and code
            top_row = QHBoxLayout()
            
            title_label = QLabel(coupon["title"])
            title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            title_label.setStyleSheet(f"color: {coupon['color']};")
            
            code_frame = QFrame()
            code_frame.setStyleSheet("""
                QFrame {
                    background: #f1f2f6;
                    border-radius: 12px;
                    padding: 2px 10px;
                }
            """)
            code_layout = QHBoxLayout(code_frame)
            code_layout.setContentsMargins(5, 2, 5, 2)
            
            code_icon = QLabel("🎟️")
            code_label = QLabel(coupon['code'])
            code_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            code_label.setStyleSheet("color: #2f3542;")
            
            code_layout.addWidget(code_icon)
            code_layout.addWidget(code_label)
            
            top_row.addWidget(title_label)
            top_row.addStretch()
            top_row.addWidget(code_frame)
            
            # Details row
            details_row = QHBoxLayout()
            
            min_spend_label = QLabel(f"Min. spend: {coupon['min_spend']}")
            min_spend_label.setStyleSheet("color: #747d8c; font-size: 13px;")
            
            expiry_label = QLabel(f"Expires in: {coupon['expiring']}")
            expiring_label = expiry_label  # Keep both names for backward compatibility
            expiry_label.setStyleSheet("""
                QLabel {
                    color: #ff6b81;
                    font-size: 12px;
                    font-weight: bold;
                    background: #ffebee;
                    padding: 3px 8px;
                    border-radius: 10px;
                }
            """)
            
            details_row.addWidget(min_spend_label)
            details_row.addStretch()
            details_row.addWidget(expiry_label)
            
            # Use button
            use_btn = QPushButton("USE NOW")
            use_btn.setFixedHeight(40)
            use_btn.setCursor(QCursor(Qt.PointingHandCursor))
            use_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {coupon['color']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background: {self.darken_color(coupon['color'], 10)};
                }}
                QPushButton:pressed {{
                    background: {self.darken_color(coupon['color'], 20)};
                }}
            """)
            
            # Connect the button to copy code and show message
            use_btn.clicked.connect(lambda checked, code=coupon['code']: self.use_coupon(code))
            
            # Add widgets to layout
            coupon_layout.addLayout(top_row)
            coupon_layout.addLayout(details_row)
            coupon_layout.addWidget(use_btn)
            
            # Add to scroll layout
            scroll_layout.addWidget(coupon_frame)
        
        # Add stretch to push content to top
        scroll_layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Set main layout
        top_row.addWidget(use_btn)

        coupon_layout.addLayout(top_row)
        coupon_layout.addWidget(min_spend_label)
        coupon_layout.addWidget(expiring_label)

        coupon_frame.setLayout(coupon_layout)
        main_layout.addWidget(coupon_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)



# Redeem Coupon Logic
    def use_coupon(self, code):
        """Handle when a coupon is used from the UI"""
        QApplication.clipboard().setText(code)
        QMessageBox.information(
            self,
            "Coupon Applied",
            f"Coupon '{code}' has been copied to your clipboard!\n\n"
            "Paste it at checkout to apply your discount.",
            QMessageBox.Ok
        )

    def redeem_coupon(self):
        code = self.redemption_input.text().strip().upper()
        if code in COUPONS:
            QApplication.clipboard().setText(code)
            QMessageBox.information(self, "Coupon Redeemed", f"Coupon '{code}' is valid!\nCopied to clipboard. Use it at checkout.")
        else:
            QMessageBox.warning(self, "Invalid Coupon", "This coupon code is not valid.")


    def go_back(self):
        self.homepage_window.show()
        self.close()


class NotificationUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Notifications")
        self.setGeometry(100, 100, 360, 600)
        self.homepage_window = homepage_window
        self.setStyleSheet("background-color: white;")
        self.notification_setup_ui()

    def notification_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        top_bar = QHBoxLayout()

        back_btn = QPushButton("←")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("color: white; font-size: 18px; background: red; border: none;")
        back_btn.clicked.connect(self.go_back)

        title = QLabel("Notifications")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: black;")
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                background: red;
                border: none;
                padding: 4px 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #cc0000;
            }
        """)
        clear_btn.clicked.connect(self.clear_all)

        # Add widgets to top bar
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(clear_btn)

        main_layout.addLayout(top_bar)

        notification_data = load_notifications()
        if not notification_data:
            notification_data = ["No notifications yet."]

        for text in notification_data:
            notif_frame = QFrame()
            notif_frame.setStyleSheet("""
                QFrame {   
                    border: 2px solid red;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            notif_layout = QVBoxLayout()

            notif_label = QLabel(text)
            notif_label.setWordWrap(True)
            notif_label.setFont(QFont("Arial", 12))
            notif_label.setStyleSheet("font-size: 14px; color: black;")

            notif_layout.addWidget(notif_label)
            notif_frame.setLayout(notif_layout)

            main_layout.addWidget(notif_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def clear_all(self):
        if QMessageBox.question(self, "Clear Notifications", "Delete all notifications?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            clear_notifications()
            # Clear the existing layout and rebuild it
            layout = self.layout()
            if layout:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            self.notification_setup_ui()
            self.refresh()

    def refresh(self):
        # recreate UI
        self.setLayout(QVBoxLayout())  # reset
        self.notification_setup_ui()

    def go_back(self):
        self.homepage_window.show()
        self.close()
 


#Account Settings
class AccountSettingsUI(QWidget):
    def __init__(self, login_window, homepage_window):
        super().__init__()
        self.login_window = login_window  
        self.homepage_window = homepage_window
        self.setWindowTitle("Account Settings")
        self.setGeometry(100, 100, 350, 600)
        self.setStyleSheet("background-color: white;")
        self.settings_setup_ui()

    #Setup ng Settings
    def settings_setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        top_row = QHBoxLayout()

        #By Clicking this and going back to homepage
        back_btn = QPushButton("←")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("""
                   QPushButton {
                    background-color: red;
                    color: white;
                    font-size: 18px;
                    border: 1px solid red;
                    border-radius: 10px;
              }
        """)
        back_btn.clicked.connect(self.homepage_again)


        title = QLabel("Account Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))


        top_row.addWidget(back_btn)
        top_row.addStretch()
        top_row.addWidget(title)
        top_row.addStretch()

        layout.addLayout(top_row)

        #Labeling all sections
        def section_label(text):
            label = QLabel(text)
            label.setFont(QFont("Arial", 11, QFont.Bold))
            label.setStyleSheet("color: red; margin-top: 10px;")
            return label

        layout.addWidget(section_label("My Account"))
        layout.addLayout(self.button_row("Account | Security", "Bank Accounts"))
        layout.addWidget(section_label("Settings"))
        layout.addWidget(self.single_button("Notification Settings"))
        layout.addLayout(self.button_row("Privacy Settings", "Language"))
        layout.addWidget(section_label("Support"))
        layout.addLayout(self.button_row("Help Centre", "Community Rules"))
        layout.addLayout(self.button_row("About", "KKKMart Policies"))

        #Switch Button
        switch_btn = QPushButton("Switch Account")
        switch_btn.setCursor(QCursor(Qt.PointingHandCursor))
        #Log Out Button
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(QCursor(Qt.PointingHandCursor))

        for btn in (switch_btn, logout_btn):
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    font-size: 14px;
                    border-radius: 10px;
                }
            """)

        switch_btn.clicked.connect(self.switch_account)
        logout_btn.clicked.connect(self.logout)

        layout.addSpacing(20)
        layout.addWidget(switch_btn)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    
    def button_row(self, left_text, right_text):
        hbox = QHBoxLayout()
        hbox.addWidget(self.single_button(left_text))
        hbox.addWidget(self.single_button(right_text))
        return hbox

    #Single between left and right
    def single_button(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                border: 1px solid red;
                border-radius: 20px;
                font-size: 12px;
                padding: 5px;
            }
        """)
        btn.clicked.connect(lambda _, name=text: self.open_setting_page(name))
        return btn

    #Going back to Home Page
    def homepage_again(self):
        self.homepage_window.show()  
        self.close()

    #Log out and going back to login interface
    def open_setting_page(self, name):
        if name == "Account | Security":
            self.sub_window = AccountSecurityUI(self, self.homepage_window.username)
        elif name == "Bank Accounts":
            self.sub_window = BankAccountsUI(self)
        elif name in ("Notification Settings", "Privacy Settings", "Language"):
            self.sub_window = InfoPageUI(name, self)  # still placeholder
        else:
            self.sub_window = InfoPageUI(name, self)
        self.sub_window.show()
        self.hide()

    def switch_account(self):
        self.switch_ui = SwitchAccountUI(self, self.login_window, self.homepage_window)
        self.switch_ui.show()
        self.hide()

    def logout(self):
        self.login_window.show()
        self.close()


# ---------------------
# Profile display UI
class ProfileUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.homepage_window = homepage_window
        self.username = homepage_window.username
        self.setWindowTitle("My Profile")
        self.setGeometry(100, 100, 400, 700)
        self.setup_ui()
        self.setMinimumSize(360, 600)

    def setup_ui(self):
        # Main container with shadow effect
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QLabel#subtitle {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton#edit_btn {
                background-color: #3498db;
                color: white;
            }
            QPushButton#edit_btn:hover {
                background-color: #2980b9;
                box-shadow: 0 2px 8px rgba(41, 128, 185, 0.3);
            }
            QPushButton#back_btn {
                background-color: #95a5a6;
                color: white;
                margin-top: 10px;
            }
            QPushButton#back_btn:hover {
                background-color: #7f8c8d;
                box-shadow: 0 2px 8px rgba(149, 165, 166, 0.3);
            }
            .profile-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            .info-row {
                padding: 12px 0;
                border-bottom: 1px solid #eee;
            }
            .info-row:last-child {
                border-bottom: none;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with avatar and welcome
        header = QVBoxLayout()
        header.setAlignment(Qt.AlignCenter)
        
        # Avatar placeholder
        avatar = QLabel()
        avatar.setFixedSize(100, 100)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                border-radius: 50%;
                color: white;
                font-size: 40px;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 10px;
            }
        """)
        # Add first letter of username as avatar
        avatar_letter = self.username[0].upper() if self.username else '?'
        avatar.setText(avatar_letter)
        avatar.setAlignment(Qt.AlignCenter)
        
        title = QLabel(f"Hello, {self.username}" if self.username else "My Profile")
        title.setObjectName("title")
        
        subtitle = QLabel("Manage your account information")
        subtitle.setObjectName("subtitle")
        
        header.addWidget(avatar)
        header.addWidget(title)
        header.addWidget(subtitle)
        
        # Profile Info Card
        info_card = QWidget()
        info_card.setObjectName("profile_card")
        info_card.setStyleSheet("""
            QWidget#profile_card {
                background: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Get user data
        conn = db.connect()
        cur = conn.cursor()
        cur.execute("SELECT username, email, phone FROM users WHERE username=?", (self.username,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            for label, value in zip(['Username', 'Email', 'Phone'], row):
                # Create a container for each info row
                row_widget = QWidget()
                row_widget.setStyleSheet("""
                    QLabel { 
                        color: #7f8c8d;
                        font-size: 13px;
                        margin: 0;
                        padding: 0;
                    }
                    QLabel.value {
                        color: #2c3e50;
                        font-weight: 500;
                        font-size: 14px;
                    }
                """)
                
                row_layout = QVBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 12, 0, 12)
                
                # Label
                lbl = QLabel(label.upper())
                lbl.setStyleSheet("font-size: 11px; color: #95a5a6; font-weight: 600; letter-spacing: 0.5px;")
                
                # Value
                val = QLabel(str(value) if value else "Not set")
                val.setStyleSheet("font-size: 14px; color: #2c3e50; font-weight: 500; margin-top: 2px;")
                
                row_layout.addWidget(lbl)
                row_layout.addWidget(val)
                
                # Add bottom border except for last item
                if label.lower() != 'phone':
                    line = QFrame()
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setStyleSheet("color: #ecf0f1;")
                    row_layout.addWidget(line)
                
                info_layout.addWidget(row_widget)
        
        info_card.setLayout(info_layout)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        edit_btn = QPushButton("Edit Profile")
        edit_btn.setObjectName("edit_btn")
        edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        edit_btn.setFixedHeight(45)
        edit_btn.clicked.connect(self.open_edit)
        
        back_btn = QPushButton("Back to Home")
        back_btn.setObjectName("back_btn")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setFixedHeight(45)
        back_btn.clicked.connect(self.go_back)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(back_btn)
        
        # Add all to main layout
        layout.addLayout(header)
        layout.addWidget(info_card, 1)
        layout.addLayout(btn_layout)
        
        main_widget.setLayout(layout)
        
        # Scroll area for smaller screens
        scroll = QScrollArea()
        scroll.setWidget(main_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)

    def open_edit(self):
        self.edit_window = AccountSecurityUI(self.homepage_window, self.username)
        self.edit_window.show()
        self.close()

    def go_back(self):
        self.homepage_window.show()
        self.close()


class AccountSecurityUI(QWidget):
    def __init__(self, settings_window, username):
        super().__init__()
        self.settings_window = settings_window
        self.username = username
        self.setWindowTitle("Account | Security")
        self.setGeometry(120, 120, 350, 500)
        self.setStyleSheet("background:white;")
        self.build_ui()

    def build_ui(self):
        user = db.validate_user(self.username, db.validate_user(self.username, "")[2]) if db.validate_user(self.username, "") else None
        # fetch full row via custom function
        conn=db.connect(); cur=conn.cursor()
        cur.execute("SELECT username,email,phone FROM users WHERE username=?", (self.username,))
        row=cur.fetchone(); conn.close()
        username, email, phone = row if row else (self.username, "", "")

        layout = QVBoxLayout(); layout.setSpacing(10)
        title = QLabel("Edit Profile"); title.setFont(QFont("Arial",16,QFont.Bold)); title.setAlignment(Qt.AlignCenter); title.setStyleSheet("color:red;")
        layout.addWidget(title)

        # Username (read-only)
        self.user_edit = QLineEdit(username); self.user_edit.setReadOnly(True)
        layout.addWidget(QLabel("Username")); layout.addWidget(self.user_edit)
        # Email
        self.email_edit = QLineEdit(email); layout.addWidget(QLabel("Email")); layout.addWidget(self.email_edit)
        # Phone
        self.phone_edit = QLineEdit(phone); layout.addWidget(QLabel("Phone")); layout.addWidget(self.phone_edit)
        # Password change
        self.pass_edit = QLineEdit(); self.pass_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("New Password (leave blank to keep)")); layout.addWidget(self.pass_edit)

        save_btn = QPushButton("Save Changes"); save_btn.setStyleSheet("background:red;color:white;border-radius:10px;height:35px;"); save_btn.clicked.connect(self.save_changes)
        back_btn = QPushButton("<- Back"); back_btn.clicked.connect(self.go_back)
        layout.addWidget(save_btn); layout.addWidget(back_btn)
        self.setLayout(layout)

    def save_changes(self):
        email = self.email_edit.text().strip(); phone = self.phone_edit.text().strip(); pwd = self.pass_edit.text().strip() or None
        if not email or not phone:
            QMessageBox.warning(self,"Input Error","Email and Phone cannot be empty."); return
        if pwd and len(pwd)<6:
            QMessageBox.warning(self,"Input Error","Password too short."); return
        if db.update_user_info(self.username, email=email, phone=phone, password=pwd):
            QMessageBox.information(self,"Updated","Profile updated successfully")
            self.go_back()
        else:
            QMessageBox.warning(self,"No Changes","Nothing was updated.")

    def go_back(self):
        self.settings_window.show(); self.close()
# ---------------------


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginUI()
    window.show()
    sys.exit(app.exec_())