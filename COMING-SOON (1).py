import sys
import re
import os
import json
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap, QIcon, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, 
    QSizePolicy, QGridLayout, QFrame, QComboBox, QRadioButton, QListWidget,
    QListWidgetItem, QTextEdit, QCheckBox, QGraphicsOpacityEffect, QDialog,
    QScrollArea, QSizeGrip
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve

# Import styles
from styles1 import *


COUPONS = {
    "10OFF": {"discount": 0.10, "desc": "10% OFF", "min_spend": 0},
    "FREESHIP": {"discount": 0.00, "desc": "Free Shipping", "min_spend": 0},
    "50OFF": {"discount": 0.50, "desc": "50% OFF (max $50)", "min_spend": 0, "max_discount": 50},
    "15OFF": {"discount": 0.15, "desc": "15% OFF (max $150)", "min_spend": 200, "max_discount": 150},
    "20OFF": {"discount": 0.20, "desc": "20% OFF (max $100)", "min_spend": 300, "max_discount": 100},
}

#Magnonotify after mo mag buy ng item
def add_notification(message):
    try:
        with open("notifications.json", "r") as f:
            notifications = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        notifications = []
    notifications.append(message)
    with open("notifications.json", "w") as f:
        json.dump(notifications, f)

#count ng mga notification
def get_notification_count():
    try:
        with open("notifications.json", "r") as f:
            notifications = json.load(f)
        return len(notifications)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

#Aalin ang mga notification
def clear_notifications():
    with open("notifications.json", "w") as f:
        json.dump([], f)

def fade_in_animation(widget, duration=800):
    """Apply a fade-in animation to a widget"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start()
    
    # Store animation on the widget to prevent garbage collection
    widget.animation = animation
    return animation



class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KKKMART - Login")
        self.setGeometry(100, 100, 400, 700)
        self.setFixedSize(400, 700)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.setWindowIcon(QIcon("KKK2.png"))
        

        self.users = {
            "user1": "user123",
            "user2": "user222"
        }
        
        # Load remembered credentials if they exist
        if os.path.exists("remember_me.json"):
            try:
                with open("remember_me.json", "r") as f:
                    remembered = json.load(f)
                    if "username" in remembered and "password" in remembered:
                        self.users[remembered["username"]] = remembered["password"]
            except Exception as e:
                print(f"Error loading remembered credentials: {e}")
        
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        self.setLayout(main_layout)
        
        # Logo and Title
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(15)
        
        # Logo
        logo = QLabel()
        logo_pixmap = QPixmap("KKK2.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("background-color: transparent;")
        fade_in_animation(logo)
        
        # Title
        title = QLabel("KKKMART")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        self.subtitle = QLabel("Welcome back! Please login to your account.")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(f"color: {DARK_GRAY}; font-size: 14px;")
        
        # Add to logo container
        logo_layout.addWidget(logo)
        logo_layout.addWidget(title)
        logo_layout.addWidget(self.subtitle)
        
        # Error message label (initially hidden)
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #808080; font-size: 13px; min-height: 20px;")
        self.error_label.setWordWrap(True)
        logo_layout.addWidget(self.error_label)
        
        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 0, 30, 0)  # Added left and right margins
        form_layout.setSpacing(15)  # Reduced spacing slightly
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setProperty("class", "input-field")
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setProperty("class", "input-field")
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet(f"color: {DARK_GRAY}; font-size: 13px;")
        
        # Show password checkbox
        self.show_password = QCheckBox("Show Password")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        self.show_password.setStyleSheet(f"color: {DARK_GRAY}; font-size: 13px;")
        
        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_btn.clicked.connect(self.login_validation)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: darkgray !important;
                border: 2px solid {PRIMARY_COLOR};
                border-radius: 24px;
                padding: 12px 32px;
                font-size: 15px;
                font-weight: 800;
                min-height: 48px;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
                border-color: {ACCENT_COLOR};
                color: darkgray !important;
            }}
            QPushButton:pressed {{
                background-color: #B71C1C;
                border-color: #B71C1C;
            }}
            QPushButton:disabled {{
                background-color: #E0E0E0;
                border-color: #E0E0E0;
                color: #9E9E9E !important;
            }}
        """)
        # Register link
        register_layout = QHBoxLayout()
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.setSpacing(5)
        
        register_label = QLabel("Don't have an account?")
        register_label.setStyleSheet(f"color: {DARK_GRAY}; font-size: 13px;")
        
        self.register_link = QPushButton("Register here")
        self.register_link.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PRIMARY_COLOR};
                border: none;
                text-decoration: underline;
                font-size: 13px;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {ACCENT_COLOR};
            }}
        """)
        self.register_link.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_link.clicked.connect(self.show_register_ui)
        
        register_layout.addStretch()
        register_layout.addWidget(register_label)
        register_layout.addWidget(self.register_link)
        register_layout.addStretch()
        
        # Add widgets to form layout
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addWidget(self.show_password)
        form_layout.addWidget(self.login_btn)
        form_layout.addLayout(register_layout)
        
        # Add containers to main layout
        main_layout.addWidget(logo_container, alignment=Qt.AlignTop)
        main_layout.addWidget(form_container, alignment=Qt.AlignTop)
        main_layout.addStretch()
        
        # Apply fade in animation to form elements
        for i in range(form_layout.count()):
            widget = form_layout.itemAt(i).widget()
            if widget:
                fade_in_animation(widget, duration=800 + (i * 100))  # Staggered animation
    
    def apply_styles(self):
        # Apply styles to input fields and buttons
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS};
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                min-height: {BUTTON_HEIGHT};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
            QLineEdit, QComboBox, QTextEdit {{
                border: 1px solid #E0E0E0;
                border-radius: {BORDER_RADIUS};
                padding: 12px 16px;
                font-size: 14px;
                min-height: {INPUT_HEIGHT};
                background: {WHITE};
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
            }}
            QLabel#headerLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {PRIMARY_COLOR};
                margin-bottom: 10px;
            }}
        """)
    
    def fill_credentials(self, username, password):
        """Fill in the login form with the provided credentials"""
        self.username_input.setText(username)
        self.password_input.setText(password)
        # Clear any previous error messages
        self.error_label.setText("")
        self.username_input.setStyleSheet("")
        self.password_input.setStyleSheet("")
    
    def toggle_password_visibility(self):
        """Toggle password visibility in the password field"""
        if self.show_password.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def hash_password(self, password):
        """Hash a password for storing."""
        import hashlib
        import binascii
        import os
        from base64 import urlsafe_b64encode, urlsafe_b64decode
        
        # Generate a random salt
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        # Hash the password with the salt
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        # Return the hashed password with salt
        return (salt + pwdhash).decode('ascii')
    
    def verify_password(self, stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        import hashlib
        import binascii
        from base64 import urlsafe_b64encode, urlsafe_b64decode
        
        # For backward compatibility with plain text passwords
        if stored_password == provided_password:
            return True
            
        try:
            # Extract the salt and hash from the stored password
            salt = stored_password[:64].encode('ascii')
            stored_hash = stored_password[64:]
            # Hash the provided password with the same salt
            pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
            pwdhash = binascii.hexlify(pwdhash).decode('ascii')
            # Compare the hashes
            return pwdhash == stored_hash
        except (ValueError, IndexError):
            return False
    
    def login_validation(self):
        """Validate login credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Reset error state
        self.error_label.setText("")
        self.username_input.setStyleSheet("")
        self.password_input.setStyleSheet("")
        
        # Validate inputs
        if not username:
            self.show_error("Please enter your username", self.username_input)
            return
            
        if not password:
            self.show_error("Please enter your password", self.password_input)
            return
            
        # Check credentials
        if username in self.users and self.verify_password(self.users[username], password):
            # Handle remember me functionality
            if hasattr(self, 'remember_checkbox') and self.remember_checkbox.isChecked():
                with open("remember_me.json", "w") as f:
                    # Only store username in remember_me.json for security
                    json.dump({"username": username}, f)
            elif os.path.exists("remember_me.json"):
                os.remove("remember_me.json")
                
            self.handle_successful_login(username)
        else:
            self.show_error("Invalid username or password")
    
    def handle_successful_login(self, username):
        """Handle actions after successful login"""
        # Create a custom message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Login Successful")
        msg_box.setText(f"Welcome back, {username}!")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowIcon(QIcon("KKK2.png"))
        
        # Set the style for the message box
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 16px;
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_COLOR_DARK};
            }}
        """)
        
        # Show the message box
        msg_box.exec_()
        
        # Initialize accounts dictionary with empty carts
        accounts = {user: {"cart": []} for user in self.users}
        
        # Proceed to main application with accounts data
        self.open_home_page(username, accounts)
    
    def show_register_ui(self):
        """Show the registration UI"""
        self.register_ui = RegisterUI(self)
        self.register_ui.show()
        self.hide()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up any resources if needed
        super().closeEvent(event)

    def epbidatcom_login(self):
        QMessageBox.information(self, "Login", "Facebook login is not implemented yet.")

    def gulugulu_login(self):
        QMessageBox.information(self, "Login", "Google login is not implemented yet.")


    def create_input(self, placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(40)
        input_field.setFixedWidth(270)
        input_field.setStyleSheet("border: 1px solid #ccc; border-radius: 10px; padding: 0 10px;")
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        return input_field

    def open_register(self):
        self.register_window = RegisterUI(self)
        self.register_window.show()
        self.hide()

    def open_home_page(self, username, accounts):
        """Open the home page after successful login"""
        self.homepage = HomePageUI(username, self, accounts)
        self.homepage.show()
        self.hide()

    def show_error(self, message, field=None):
        """Show error message and optionally highlight a field"""
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        
        if field:
            field.setStyleSheet("""
                border: 2px solid #d32f2f;
                border-radius: 4px;
                padding: 8px 12px;
            """)
    
    def show_hide_password(self):
        if self.toggle_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setIcon(QIcon("close.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setIcon(QIcon("open.png"))

    def add_new_user(self, username, password):
        self.users[username] = self.hash_password(password)

#This is Register Window
class RegisterUI(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Create New Account")
        self.setGeometry(100, 100, 400, 700)
        self.setFixedSize(400, 700)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.setWindowIcon(QIcon("KKK2.png"))
        self.register_setup_ui()
        self.apply_styles()
        

    def register_setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        self.setLayout(main_layout)
        
        # Logo and Title
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(15)
        
        # Logo
        logo = QLabel()
        logo_pixmap = QPixmap("KKK2.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("background-color: transparent;")
        fade_in_animation(logo)
        
        # Title
        title = QLabel("Create Account")
        title.setObjectName("headerLabel")
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Fill in your details to create an account.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {DARK_GRAY}; font-size: 14px;")
        
        # Add to logo container
        logo_layout.addWidget(logo)
        logo_layout.addWidget(title)
        logo_layout.addWidget(subtitle)
        
        # Error message label (initially hidden)
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #808080; font-size: 13px; min-height: 20px;")
        self.error_label.setWordWrap(True)
        logo_layout.addWidget(self.error_label)
        
        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        self.username_input.setProperty("class", "input-field")
        
        # Email field
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        self.email_input.setProperty("class", "input-field")
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setProperty("class", "input-field")
        
        # Confirm Password field
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setProperty("class", "input-field")
        
        # Show password checkbox
        self.show_password = QCheckBox("Show Passwords")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        self.show_password.setStyleSheet(f"color: {DARK_GRAY}; font-size: 13px;")
        
        # Register button
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setObjectName("register_btn")
        self.register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_btn.clicked.connect(self.register_validation)
        self.register_btn.setMinimumHeight(28)  # Further reduced height
        self.register_btn.setStyleSheet("""
            QPushButton#register_btn {
                background-color: #E31837;
                color: white;
                border: 1px solid #D32F2F;
                border-radius: 5px;
                padding: 4px 14px;
                font-size: 18px;
                font-weight: 600;
                min-width: 200px;
                margin: 8px 0 4px 0;
            }
            QPushButton#register_btn:hover {
                background-color: #D32F2F;
            }
            QPushButton#register_btn:pressed {
                background-color: #A50D2D;
            }
        """)
        
        # Login link
        login_layout = QHBoxLayout()
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(5)
        
        login_label = QLabel("Already have an account?")
        login_label.setStyleSheet(f"color: {DARK_GRAY}; font-size: 11px; border: none;")
        
        self.login_link = QPushButton("Login here")
        self.login_link.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PRIMARY_COLOR};
                border: none;
                text-decoration: underline;
                font-size: 11px;
                padding: 0;
                margin: 0;
            }}
            QPushButton:hover {{
                color: {ACCENT_COLOR};
            }}
        """)
        self.login_link.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_link.clicked.connect(self.back_to_login)
        
        login_layout.addStretch()
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_link)
        login_layout.addStretch()
        
        # Add widgets to form layout
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addWidget(self.show_password)
        form_layout.addWidget(self.register_btn)
        form_layout.addLayout(login_layout)
        
        # Add containers to main layout
        main_layout.addWidget(logo_container, alignment=Qt.AlignTop)
        main_layout.addWidget(form_container, alignment=Qt.AlignTop)
        main_layout.addStretch()
        
        # Apply fade in animation to form elements
        for i in range(form_layout.count()):
            widget = form_layout.itemAt(i).widget()
            if widget:
                fade_in_animation(widget, duration=800 + (i * 100))  # Staggered animation
    
    def apply_styles(self):
        # Apply styles to input fields and buttons
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS};
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 800;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
                color: white;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                border: 1px solid #E0E0E0;
                border-radius: {BORDER_RADIUS};
                padding: 12px 16px;
                font-size: 14px;
                min-height: {INPUT_HEIGHT};
                background: {WHITE};
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
            }}
            QLabel#headerLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {PRIMARY_COLOR};
                margin-bottom: 10px;
            }}
        """)

    def setup_input(self, widget, layout):
        """Legacy method for setting up input fields"""
        widget.setStyleSheet("""
            padding: 12px 16px;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-size: 14px;
            background: white;
        """)
        widget.setMinimumHeight(44)
        if isinstance(layout, QVBoxLayout) or isinstance(layout, QHBoxLayout):
            layout.addWidget(widget)
        return widget

    def toggle_password_visibility(self, state):
        """Toggle password visibility for both password fields"""
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            
    def register_validation(self):
        """Validate registration form and create new account"""
        # Get input values
        username = getattr(self, 'username_input', getattr(self, 'name_input', None))
        username = username.text().strip() if username else ""
        
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = getattr(self, 'confirm_password_input', self.password_input).text()
        phone = getattr(self, 'phone_input', None)
        phone = phone.text().strip() if phone else ""
        
        # Reset error state
        if hasattr(self, 'error_label'):
            self.error_label.setText("")
            self.error_label.setStyleSheet(f"color: {ERROR_COLOR};")
        
        # Validate inputs
        if not username:
            # Try to get the username input field, default to None if it doesn't exist
            username_field = getattr(self, 'username_input', None)
            if username_field is None:
                username_field = getattr(self, 'name_input', None)
            self.show_error("Please enter a username", username_field)
            return
            
        if not email:
            self.show_error("Please enter your email address", self.email_input)
            return
            
        # Basic email validation
        if "@" not in email or "." not in email:
            self.show_error("Please enter a valid email address", self.email_input)
            return
            
        if not password:
            self.show_error("Please create a password", self.password_input)
            return
            
        if len(password) < 6:
            self.show_error("Password must be at least 6 characters long", self.password_input)
            return
            
        if hasattr(self, 'confirm_password_input') and password != confirm_password:
            self.show_error("Passwords do not match", self.confirm_password_input)
            return
            
        # Phone validation if phone field exists
        if hasattr(self, 'phone_input') and phone:
            if not phone.isdigit() or len(phone) < 11:
                self.show_error("Please enter a valid phone number", self.phone_input)
                return
        
        # Check if username already exists
        if username in self.login_window.users:
            self.show_error("Username already exists", getattr(self, 'username_input', self.name_input))
            return
        
        # If all validations pass, create the account
        self.login_window.add_new_user(username, password)
        
        # Show success message
        if hasattr(self, 'error_label'):
            self.error_label.setStyleSheet(f"color: {SUCCESS_COLOR};")
            self.error_label.setText("Account created successfully! Redirecting to login...")
            
            # Disable the register button to prevent multiple submissions
            if hasattr(self, 'register_btn'):
                self.register_btn.setEnabled(False)
            
            # Return to login after a short delay
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.back_to_login)
        else:
            # Fallback if error_label doesn't exist
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.back_to_login()
            
        # Reset password visibility
        if hasattr(self, 'show_password'):
            self.show_password.setChecked(False)
        self.toggle_password_visibility()

    def show_error(self, message, field=None):
        """Show error message and optionally highlight a field"""
        if hasattr(self, 'error_label'):
            self.error_label.setText(message)
            self.error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        
        if field:
            field.setStyleSheet("""
                border: 2px solid #d32f2f;
                border-radius: 4px;
                padding: 8px 12px;
            """)
    
    def back_to_login(self):
        """Return to the login screen"""
        if hasattr(self, 'login_window') and self.login_window:
            self.login_window.show()
        self.close()
        
    # Backward compatibility
    def password_visibility(self):
        if hasattr(self, 'toggle_register_password'):
            self.toggle_register_password.toggle()
        self.toggle_password_visibility()
    
#HomePage Window
class HomePageUI(QWidget):
    def __init__(self, username, login_window, accounts):
        super().__init__()
        self.setWindowTitle("KKKMART - Home")
        self.setGeometry(100, 100, 360, 640)
        self.username = username
        self.login_window = login_window
        self.accounts = accounts
        self.setFixedSize(360,640)
        self.products = self.load_products()
        self.setStyleSheet("background-color: white;")
        self.homepage_setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))
        

    #Setup ng Home Page
    def homepage_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        

        header = QHBoxLayout()
        title = QLabel("KKKMART")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: black;")

        profile = QLabel()
        profile.setPixmap(QPixmap("UserIcon.png").scaled(30, 30, Qt.KeepAspectRatio))
        header.addWidget(title)
        header.addStretch()
        header.addWidget(profile)

        search_layout = QHBoxLayout()
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search for an Item")
        search_box.setFixedHeight(35)
        search_box.setStyleSheet("border: 1px solid #ccc; color: black; border-radius: 10px;")
        search_btn = QPushButton("🔍")
        search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        search_btn.setFixedSize(40, 35)
        search_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        search_btn.clicked.connect(self.open_product_listing)
        search_layout.addWidget(search_box)
        search_layout.addWidget(search_btn)
        

        sale_banner = QLabel("SALE! 50% OFF")
        sale_banner.setFont(QFont("Arial", 24, QFont.Bold))
        sale_banner.setAlignment(Qt.AlignLeft)
        sale_banner.setStyleSheet("color: red;" 
                                  "font-weight: bold;" 
                                  "border 2px solid red;" 
                                  "padding: 6px; " 
                                  "border-radius: 10px;")
        

        head_layout = QHBoxLayout()
        head_layout.addStretch()

        add_product_btn = QPushButton("Add Product")
        add_product_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        add_product_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_product_btn.clicked.connect(self.open_add_product)
        head_layout.addWidget(add_product_btn)

        main_layout.addLayout(head_layout)


        #Grid Layout para sa mga pictures
        grid = QGridLayout()
        products_grid = [
            {"image": "sneakers.png", "name": "Shoes", "price": "$70", "stocks": "20", "rating": "⭐⭐⭐⭐⭐", 
             "description": "Comfortable sneakers for everyday wear.", "seller": "Shoe Marketplace"},
            {"image": "laptop.png", "name": "ASUS Republic of Gamers", "price": "$600", "stocks": "50", "rating": "⭐⭐⭐⭐⭐",
              "description": "High-performance laptop for work and play.", "seller": "Laptop Marketplace"},
            {"image": "phone.png", "name": "NOKIA PHONE", "price": "$300", "stocks": "50", "rating": "⭐⭐⭐⭐⭐",
                "description": "Latest smartphone with advanced features.", "seller": "Phone Marketplace"},
            {"image": "clothes.png", "name": "Tupad Clothes", "price": "$150", "stocks": "30", "rating": "⭐⭐⭐",
                "description": "Bibile ka neto? Matuto kang TUMUPAD sa usapan!", "seller": "Tupad Clothing System"}
        ]
        positions = [(i, j) for i in range(2) for j in range(2)]
        for pos, product in zip(positions, products_grid):
            btn = QPushButton()
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setIcon(QIcon(product["image"]))
            btn.setIconSize(QSize(130, 100))
            btn.setStyleSheet("border: 2px solid red; border-radius: 10px; background-color: white;")
            btn.clicked.connect(lambda _, p=product: self.open_item_details(
                p["image"], p["name"], p["price"], p["stocks"], p["rating"], p["description"], p["seller"]
            ))
            grid.addWidget(btn, *pos)

        grid_wrapper = QWidget()
        grid_wrapper.setLayout(grid)

        nav = QHBoxLayout()
        nav_icons = {
            "cart": "cart.png",
            "coupons": "coupons.png",
            "home": "home.png",
            "bell": "bell.png",
            "settings": "settings.png"
        }
        #This Button is when you clicked them, they will proceed to their window
        for name, path in nav_icons.items():
            btn = QPushButton()
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(30, 30))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedSize(50,50)
            btn.setStyleSheet("border: 2px solid red;" 
                              "border-radius: 10px;"
                              "background-color: white;")

            if name == "settings":
                btn.clicked.connect(self.open_settings)
            
            elif name == "cart":
                btn.clicked.connect(self.open_inventory)

            elif name == "coupons":
                btn.clicked.connect(self.open_coupons)

            elif name == "bell":
                btn.clicked.connect(self.open_notification)
                self.notif_btn = btn

            nav.addWidget(btn)
        
    
        self.update_notification()  
        notif_count = get_notification_count()
        if notif_count > 0:
            self.notif_btn.setText(str(notif_count))
        
        else:
            self.notif_btn.setText("")

        
        nav_container = QWidget()
        nav_container.setLayout(nav)
        nav_container.setStyleSheet("""
                        QWidget {
                            border: 2px solid red;
                            border-radius: 15px;
                            padding: 5px;
                            background-color: red;                                
             }                                     
        """)

        main_layout.addLayout(header)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(sale_banner)
        main_layout.addWidget(grid_wrapper)
        main_layout.addStretch()
        main_layout.addWidget(nav_container)
        self.setLayout(main_layout)
    
    def update_notification(self):
        notif_count = get_notification_count()
        if notif_count > 0:
            self.notif_btn.setText(str(notif_count))
        else:
            self.notif_btn.setText("")


    def load_products(self):
        with open("products.json", "r") as f:
            return json.load(f)
    
    #Proceeding Add to Cart
    def open_inventory(self):
        self.cart_window = InventoryCartUI(self)
        self.cart_window.show()
        self.close()

    #Proceeding to Settings
    def open_settings(self):
        self.settings_window = AccountSettingsUI(self.login_window, self, 
                                                 self.accounts,
                                                 self.username)
        self.settings_window.show()
        self.close()
    
    def open_product_listing(self):
        self.product_window = ProductWindow(self)
        self.product_window.show()
        self.close()

    def open_coupons(self):
        self.coupons_window = CouponsUI(self)
        self.coupons_window.show()
        self.close()

    def open_item_details(self, image_path, name, price, stocks, rating, description, seller):
        self.item_details_window = ItemDetailsUI(self, image_path, name, price, stocks, rating, description, seller)
        self.item_details_window.show()
        self.close()
    
    def open_notification(self):
        try:
            with open("notifications.json", "r") as f:
                notifications = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            notifications = []
        self.notification_window = NotificationUI(notifications, self)
        self.notification_window.show()
        self.hide()

    def open_add_product(self):
        self.add_product_window = AddProductUI(self)
        self.add_product_window.show()
        self.close()

class AddProductUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("Add New Product")
        self.setGeometry(100, 100, 360, 500)
        self.setFixedSize(350,500)
        self.homepage_window = homepage_window
        self.setStyleSheet("background-color: white;")
        self.setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))
        

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

    
        header_layout = QHBoxLayout()
    
        back_btn = QPushButton("<- Back")
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("background-color: red;")
        header_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        header_layout.addStretch()  
    
        add_btn = QPushButton("Add Product")
        add_btn.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        add_btn.clicked.connect(self.save_product)
        header_layout.addWidget(add_btn, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)

    
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product Name")
        main_layout.addWidget(self.name_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        main_layout.addWidget(self.price_input)

        self.stocks_input = QLineEdit()
        self.stocks_input.setPlaceholderText("Stocks")
        main_layout.addWidget(self.stocks_input)

        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("Rating (e.g. 4.5)")
        main_layout.addWidget(self.rating_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description")
        main_layout.addWidget(self.desc_input)

        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Insert Filename here (e.g. sneakers.png)")
        main_layout.addWidget(self.image_input)

        self.setLayout(main_layout)

    def save_product(self):
        product = {
            "image": self.image_input.text().strip(),
            "name": self.name_input.text().strip(),
            "price": self.price_input.text().strip(),
            "stocks": self.stocks_input.text().strip(),
            "rating": self.rating_input.text().strip(),
            "description": self.desc_input.toPlainText().strip() 
        }
        if not all(product.values()):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Input Error")
            msg.setText("Please fill in all fields.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            msg.exec_()
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
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText("Product added!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        msg.exec_()
        self.go_back()

    def go_back(self):
        self.homepage_window.show()
        self.close()


class ItemDetailsUI(QWidget):
    def __init__(self, homepage_window, image, name, price, stocks, rating, description, seller):
        super().__init__()
        self.setWindowTitle("KKKMART - Item Details")
        self.setGeometry(100, 100, 360, 640)
        self.homepage_window = homepage_window
        self.seller = seller
        self.setStyleSheet("background-color: white;")
        
        # Store values
        self.image = image
        self.name = name
        self.price = price
        self.stocks = stocks
        self.rating = rating
        self.description = description
        self.seller = seller
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
        pixmap = QPixmap(self.image)
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
        chat_btn.setStyleSheet("background-color: orange; color: white; border-radius: 8px; font-size: 11px;")
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

        original_price = float(self.price.replace("$", "").strip())
        discount_percent = 50
        discounted_price = original_price * (discount_percent / 100)

        sale_label = QLabel(f"Sale: {discount_percent}% OFF")
        sale_label.setStyleSheet("color: white; background-color: red; font-weight: bold; padding: 2px 8px; border-radius: 5px;")
        main_layout.addWidget(sale_label)

        orig_price_label = QLabel(f"<s>${original_price:.2f}</s>")
        orig_price_label.setStyleSheet("color: gray; font-size: 14px;")
        main_layout.addWidget(orig_price_label)

        sale_price_label = QLabel(f"${discounted_price:.2f}")
        sale_price_label.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        main_layout.addWidget(sale_price_label)


        buy_now_btn = QPushButton("Buy Now")
        buy_now_btn.setCursor(QCursor(Qt.PointingHandCursor))
        buy_now_btn.setStyleSheet("background-color: green; color: white; border-radius: 8px; font-size: 14px;")
        buy_now_btn.setFixedHeight(40)
        buy_now_btn.setFixedWidth(120)
        buy_now_btn.clicked.connect(self.buy_items)
        button_layout.addWidget(chat_btn)
        button_layout.addWidget(add_to_cart_btn)
        button_layout.addWidget(buy_now_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def buy_items(self):
        add_notification(f"You purchased {self.name} for {self.price}!")
        self.checkout_window = CheckoutUI(self.homepage_window, {
            "name": self.name,
            "price": float(self.price.replace("$", "").strip())

        })
        self.checkout_window.show()
        self.hide()
        

    def chat_to_seller(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Chat")
        msg.setText(f"Starting chat with seller: {self.seller}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        msg.exec_()

    def add_to_cart(self):
        item = {
            "image": self.image,
            "name": self.name,
            "price": self.price,
            "stocks": self.stocks,
            "rating": self.rating,
            "description": self.description,
            "seller": self.seller
    }

        cart = []
        if os.path.exists("cart.json"):
            with open("cart.json", "r") as f:
                try:
                    cart = json.load(f)
                except Exception:
                    cart = []
        cart.append(item)
        with open("cart.json", "w") as f:
            json.dump(cart, f, indent=4)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Added to Cart")
        msg.setText(f"{self.name} has been added to your cart!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        msg.exec_()

    def go_back(self):
        self.homepage_window.show()
        self.close()


class SellerProfileUI(QWidget):
    def __init__(self, seller_name, homepage_window):
        super().__init__()
        self.setWindowTitle(f"{seller_name}'s Profile")
        self.setGeometry(100, 100, 360, 600)
        self.seller_name = seller_name
        self.homepage_window = homepage_window
        self.seller_profile_setup_ui()

    def seller_profile_setup_ui(self):
        layout = QVBoxLayout()
        
        seller_label = QLabel(f"Seller: {self.seller_name}")
        seller_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(seller_label)

        products = self.get_seller_products()
        for prod in products:
            prod_label = QLabel(f"{prod['name']} - ${prod['price']}")
            layout.addWidget(prod_label)

        back_btn = QPushButton("<- Back")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def get_seller_products(self):
        if os.path.exists("products.json"):
            with open("products.json", "r") as f:
                all_products = json.load(f)
            return [p for p in all_products if p.get("seller") == self.seller_name]
        return []

    def go_back(self):
        self.homepage_window.show()
        self.close()

#Add to Cart Window
class InventoryCartUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART")
        self.setGeometry(100, 100, 360, 600)
        self.homepage_window = homepage_window
        self.edit_mode = False
        self.setStyleSheet("background-color: white;")
        self.cart_setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))
        

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

        #Edit Button
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
        if os.path.exists("cart.json"):
            with open("cart.json", "r") as f:
                cart = json.load(f)
            cart = [item for item in cart if item["name"] != name]
            with open("cart.json", "w") as f:
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
        if layout is None:
            return
            
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item is None:
                continue
                
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)
                    child_layout.deleteLater()

    def filter_itemization(self):
        keyword = self.search_input.text().lower()
        filtered = [item for item in self.all_items if keyword in item[1].lower()] 
        self.display_itemization(filtered) 

    def going_back(self):
        self.homepage_window.show()
        self.close()

    #Your Carts that you add
    def get_cart_item(self):
        if os.path.exists("cart.json"):
            with open("cart.json", "r") as f:
                try:
                    cart = json.load(f)
                    return [(item["image"], item["name"], item["price"], "Marketplace") for item in cart]
                except Exception:
                    return []
        return []

    #Proceeding to Checkout
    def open_checkout(self):
        self.open_checkout_window = CheckoutUI(self, self.homepage_window) 
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
        self.product = product
        self.setLayout(layout)
        self.setStyleSheet("border: none; border-radius: 10px; padding: 10px;")


class ProductWindow(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Product Listing")
        self.setGeometry(100, 100, 360, 600)
        self.homepage_window = homepage_window
        self.all_items = []
        self.current_filter = "price"

        with open("products.json", "r") as f:
            self.products = json.load(f)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create a container for the main content
        content_layout = QVBoxLayout()
        
        # Add Back button at the top
        back_btn = QPushButton("Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: red;
                border: 1px solid red;
                border-radius: 15px;
                padding: 8px 15px;
                text-align: center;
                font-weight: bold;
                margin-bottom: 10px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #FFE6E6;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        content_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for an item")
        self.search_bar.textChanged.connect(self.filter_items)
        content_layout.addWidget(self.search_bar)

        # Filter buttons
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)  # Add some spacing between buttons
        
        # Style for filter buttons
        filter_button_style = """
            QPushButton {
                color: #FF0000;  /* Red text */
                background-color: white;
                border: none;  /* Remove any border */
                padding: 8px 15px;  /* Add some padding */
            }
            QPushButton:hover {
                background-color: #FFE6E6;  /* Light red on hover */
            }
            QPushButton:pressed {
                background-color: #FFCCCC;  /* Slightly darker red when pressed */
            }
        """
        
        self.price_btn = QPushButton("Filter by Price")
        self.stock_btn = QPushButton("Filter by Stocks")
        self.rating_btn = QPushButton("Filter by Rating")
        
        # Apply the style to all filter buttons
        for btn in [self.price_btn, self.stock_btn, self.rating_btn]:
            btn.setStyleSheet(filter_button_style)
            btn.setCursor(Qt.PointingHandCursor)

        self.price_btn.clicked.connect(lambda: self.set_filter("price"))
        self.stock_btn.clicked.connect(lambda: self.set_filter("stock"))
        self.rating_btn.clicked.connect(lambda: self.set_filter("rating"))

        filter_layout.addWidget(self.price_btn)
        filter_layout.addWidget(self.stock_btn)
        filter_layout.addWidget(self.rating_btn)
        content_layout.addLayout(filter_layout)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Lowest to Highest", "Highest to Lowest"])
        self.sort_combo.currentTextChanged.connect(self.update_products)
        content_layout.addWidget(self.sort_combo)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)  # Add the rest of the content

        # Product list
        self.product_list = QListWidget()
        content_layout.addWidget(self.product_list)
        
        # Add a bottom back button for better navigation
        bottom_btn = QPushButton("Back to Home")
        bottom_btn.setCursor(QCursor(Qt.PointingHandCursor))
        bottom_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: red;
                border: 1px solid red;
                border-radius: 15px;
                padding: 8px 20px;
                text-align: center;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #FFE6E6;
            }
        """)
        bottom_btn.clicked.connect(self.go_back)
        
        # Add some spacing and the back button to the main layout
        content_layout.addSpacing(10)
        content_layout.addWidget(bottom_btn, alignment=Qt.AlignCenter)
        content_layout.addStretch()
        
        self.update_products()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.clear()
            if child is None:
                continue
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
    
    def filter_items(self):
        keyword = self.search_bar.text().lower()
        filtered = [item for item in self.all_items if keyword in item[1].lower()]
        self.display_item(filtered)

    def display_item(self, items):
        self.clear_layout(self.product_list)
        for item in items:
            name = item[1]
            price = item[2]
            stock = item[3]
            rating = item[4]
            label = QLabel(f"{name} | ₱{price} | Stock: {stock} | Rating: {rating}")
            self.product_list.addWidget(label)


    def handle_item(self, item):
        widget = self.product_list.itemWidget(item)
        product = widget.product
        self.opening_item_details(
        product["image"], product["name"], product["price"], product["stock"],
        product["rating"], product["description"], product["seller"]
    )
        self.items_details_window.show()
        self.close()                               
            
    def opening_item_details(self, image_path, name, price, stocks, rating, description, seller):   
        self.items_details_window = ItemDetailsUI(
            self.homepage_window, image_path, name, price, stocks, rating, description, seller
        )
        self.items_details_window.show()
        self.close()                       

    def set_filter(self, filter_type):
        self.current_filter = filter_type
        self.update_products()

    def update_products(self):
        self.product_list.clear()
        reverse = self.sort_combo.currentText() == "Highest to Lowest"
        sorted_items = sorted(self.products, key=lambda x: x.get(self.current_filter, 0), reverse=reverse)


        for prod in sorted_items:
            item = QListWidgetItem()
            widget = ProductItem(prod, self.current_filter)
            item.setSizeHint(widget.sizeHint())
            self.product_list.addItem(item)
            self.product_list.setItemWidget(item, widget)

        self.product_list.itemClicked.connect(self.handle_item)

    def go_back(self):
        self.homepage_window.show()
        self.close()

#Checkout Window
class CheckoutUI(QWidget):
    def __init__(self, cart_window, homepage_window, product_data=None):  
        super().__init__()
        self.cart_window = cart_window
        self.homepage_window = homepage_window
        self.product_data = product_data or {}
        self.applied_discount = 0
        self.setWindowIcon(QIcon("KKK2.png"))
        self.setWindowTitle("KKKMART - Checkout")
        self.setGeometry(100, 100, 360, 600)
        self.setStyleSheet("background-color: white;")
        self.checkout_setup_ui()
    
    #Setup ng Checkout
    def checkout_setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("CHECK OUT")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("""
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 30px;
            text-align: center;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 10px;
        """)
        layout.addWidget(title)

        # Product name section
        if self.product_data.get("name"):
            product_frame = QFrame()
            product_frame.setStyleSheet("""
                background: #fff;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            """)
            
            product_layout = QVBoxLayout()
            product_name = QLabel(f"Item: {self.product_data['name']}")
            product_name.setFont(QFont("Arial", 16))
            product_name.setStyleSheet("""
                color: #2c3e50;
                font-weight: 500;
                margin-bottom: 10px;
            """)
            product_layout.addWidget(product_name)
            
            price_label = QLabel(f"Price: ${self.product_data.get('price', 0.0):.2f}")
            price_label.setFont(QFont("Arial", 14))
            price_label.setStyleSheet("""
                color: #e74c3c;
                font-weight: bold;
            """)
            product_layout.addWidget(price_label)
            
            product_frame.setLayout(product_layout)
            layout.addWidget(product_frame)

        # Coupons section
        coupons_frame = QFrame()
        coupons_frame.setStyleSheet("""
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        """)

        coupons_layout = QVBoxLayout() 
        
        avail_label = QLabel("Available Coupons:")
        avail_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        coupons_layout.addWidget(avail_label)

        
        self.coupon1 = QPushButton("10OFF - APPLY")
        self.coupon2 = QPushButton("FREESHIP - APPLY")
        
        for btn in [self.coupon1, self.coupon2]:
            btn.setFont(QFont("Arial", 12, QFont.Bold))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    color: #D32F2F;
                    border: 2px solid #D32F2F;
                    border-radius: 5px;
                    padding: 10px 25px;
                    text-align: left;
                    margin: 5px 0;
                    min-width: 120px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #FFEBEE;
                    border-color: #B71C1C;
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
        apply_btn.setFont(QFont("Arial", 12))
        apply_btn.setCursor(QCursor(Qt.PointingHandCursor))
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

        # Initialize payment values
        self.subtotal_value = self.product_data.get("price", 100)
        self.shipping_fee = 10.00  # Flat shipping fee
        self.tax_rate = 0.12  # 12% tax rate
        self.applied_discount = 0.00
        
        # Calculate initial values
        self.tax_amount = self.subtotal_value * self.tax_rate
        self.total_amount = self.subtotal_value + self.shipping_fee + self.tax_amount - self.applied_discount
        
        # Create payment detail labels
        self.subtotal_label = QLabel(f"Merchandise Subtotal: ${self.subtotal_value:.2f}")
        self.shipping_label = QLabel(f"Shipping Fee: ${self.shipping_fee:.2f}")
        self.tax_label = QLabel(f"Tax ({self.tax_rate*100:.0f}%): ${self.tax_amount:.2f}")
        self.discount_label = QLabel("Discount: -$0.00")
        
        # Create a line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #ccc;")
        
        self.total_label = QLabel(f"Total Payment: ${self.total_amount:.2f}")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 15px; color: red;")

        # Apply consistent styling to all labels
        for label in [self.subtotal_label, self.shipping_label, self.tax_label, self.discount_label]:
            label.setStyleSheet("margin: 5px; font-size: 13px; color: #333;")

        details_group.addWidget(details_title)
        details_group.addWidget(self.subtotal_label)
        details_group.addWidget(self.shipping_label)
        details_group.addWidget(self.tax_label)
        details_group.addWidget(self.discount_label)
        details_group.addWidget(separator)
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

        back_btn = QPushButton("<-- Back to Cart")
        back_btn.setStyleSheet("color: red; border: none; font-size 12px;") 
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.clicked.connect(self.back_to_cart)
        layout.addWidget(back_btn, alignment = Qt.AlignLeft | Qt.AlignTop) 

        self.setLayout(layout)

    def show_payment_confirmation(self, method):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Payment Confirmation")
        msg.setText(f"Your payment via {method} was successful!\nThank you for your purchase.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        msg.exec_()

    def complete_payment(self, method):
        self.show_payment_confirmation(method)

    def apply_coupon_code(self, code):
        code = code.upper()
        subtotal = self.subtotal_value
        self.applied_discount = 0
        if code in COUPONS:
            coupon = COUPONS[code]
            if subtotal >= coupon.get("min_spend", 0):
                discount = subtotal * coupon["discount"]
                if "max_discount" in coupon:
                    discount = min(discount, coupon["max_discount"])
                self.applied_discount = discount
                self.discount_label.setText(f"Coupons Discount Subtotal: ${self.applied_discount:.2f}")
                self.total_label.setText(f"Total Payment: ${subtotal - self.applied_discount:.2f}")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Coupon Applied")
                msg.setText(f"{coupon['desc']} applied!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet("""
                    QPushButton {
                        background-color: red;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #cc0000;
                    }
                """)
                msg.exec_()
            else:
                self.applied_discount = 0.00
                self.discount_label.setText("Discount: -$0.00")
                self.total_label.setText(f"Total Payment: ${subtotal + self.shipping_fee + self.tax_amount:.2f}")
                self.total_amount = subtotal + self.shipping_fee + self.tax_amount
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Coupon Not Applied")
                msg.setText(f"Minimum spend not met for {code}.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet("""
                    QPushButton {
                        background-color: red;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #cc0000;
                    }
                """)
                msg.exec_()
        else:
            self.applied_discount = 0.00
            self.discount_label.setText("Discount: -$0.00")
            self.total_label.setText(f"Total Payment: ${subtotal + self.shipping_fee + self.tax_amount:.2f}")
            self.total_amount = subtotal + self.shipping_fee + self.tax_amount
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Invalid Coupon")
            msg.setText("This coupon code is not valid.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            msg.exec_()

    def apply_coupon_from_input(self):
        code = self.coupon_input.text().strip().upper()
        self.apply_coupon_code(code)


    #Placing your order
    def place_order(self):
    
        if self.payment_radio1.isChecked():
            method = "Online"
        
        elif self.payment_radio2.isChecked():
            method = "Bank"
        
        elif self.payment_radio3.isChecked():
            method = "Cash On Delivery"
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("No Payment Method")
            msg.setText("Please select a payment method.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            msg.exec_()
            return

        self.show_payment_confirmation(method)

        order = {
            "name": self.product_data.get("name", "Unknown Item"),
            "price": self.subtotal_value,
            "shipping_fee": f"{self.shipping_fee:.2f}",
            "tax": f"{self.tax_amount:.2f}",
            "discount": f"{self.applied_discount:.2f}",
            "total": f"{self.total_amount:.2f}",
            "payment_method": method
        }

        try:
            with open("purchases.json", "r") as f:
                history = json.load(f)
        
        except:
            history = []

        history.append(order)

        with open("purchases.json", "w") as f:
            json.dump(history, f, indent=4)
        
        # I use Built in Functions
        if isinstance(self.cart_window, InventoryCartUI):
            if os.path.exists("cart.json"):
                os.remove("cart.json")

        if hasattr(self.cart_window, "homepage_window"):
            self.cart_window.homepage_window.show()  
        else:
            self.cart_window.show() 
        
        self.close()
    

    #Going Back to cart window
    def back_to_cart(self):
        self.cart_window.show()
        self.close()



# Coupon Window
class CouponsUI(QWidget):
    def __init__(self, homepage_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Coupons")
        self.setGeometry(100, 100, 360, 640)
        self.homepage_window = homepage_window
        self.setStyleSheet("background-color: white;")
        self.coupons_setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))
        

    def coupons_setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

    # Top Bar with Back Button and Title
        top_bar = QHBoxLayout()

        back_btn = QPushButton("←")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("color: white; font-size: 18px; background: red; border: none;")
        back_btn.clicked.connect(self.go_back)

        title = QLabel("Coupons")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: black;")

        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        top_bar.addWidget(title)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)

    # Voucher Code Redemption
        redemption_label = QLabel("Voucher Code Redemption:")
        redemption_label.setFont(QFont("Arial", 12))
        redemption_label.setStyleSheet("color: black;")
        main_layout.addWidget(redemption_label)

        self.redemption_input = QLineEdit()
        self.redemption_input.setPlaceholderText("Enter Code")
        self.redemption_input.setFixedHeight(35)
        self.redemption_input.setStyleSheet("""
        QLineEdit {
            border: 2px solid red;
            border-radius: 10px;
            padding-left: 10px;
            font-size: 14px;
        }
    """)
        main_layout.addWidget(self.redemption_input)

        redeem_row = QHBoxLayout()

        redeem_btn = QPushButton("Redeem")
        redeem_btn.setStyleSheet("background-color: red; color: white; border-radius: 8px;")
        redeem_btn.setCursor(QCursor(Qt.PointingHandCursor))
        redeem_btn.setFixedHeight(35)
        redeem_btn.setFixedWidth(80)
        redeem_btn.clicked.connect(self.redeem_coupon)

        redeem_row.addStretch()
        redeem_row.addWidget(redeem_btn)
        main_layout.addLayout(redeem_row)

    # Coupons List
        coupons_data = [
            {"code": "10OFF", "title": "10% OFF", "min_spend": "$0", "expiring": "23 hours left"},
            {"code": "15OFF", "title": "15% off Capped at $150", "min_spend": "$200", "expiring": "23 hours left"},
            {"code": "20OFF", "title": "20% off Capped at $100", "min_spend": "$300", "expiring": "23 hours left"},
            {"code": "50OFF", "title": "50% off Capped at $50", "min_spend": "$0", "expiring": "23 hours left"},
            {"code": "FREESHIP", "title": "Free Shipping", "min_spend": "$0", "expiring": "23 hours left"},
]

    # Create coupon cards
        for coupon in coupons_data:
            coupon_frame = QFrame()
            coupon_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid red;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)

        coupon_layout = QVBoxLayout()
        title_label = QLabel(coupon["title"])
        title_label.setFont(QFont("Arial", 14, QFont.Bold))

        code_label = QLabel(f"Code: {coupon['code']}")
        code_label.setStyleSheet("color: red; font-weight: bold;")
        coupon_layout.addWidget(code_label)

        min_spend_label = QLabel(f"Min. Spend {coupon['min_spend']}")
        expiring_label = QLabel(f"Expiring: {coupon['expiring']}")

        use_btn = QPushButton("Use")
        use_btn.setFixedSize(70, 30)
        use_btn.setCursor(QCursor(Qt.PointingHandCursor))
        use_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #D32F2F;
                border-radius: 5px;
                color: #D32F2F;
                background-color: #FFEBEE;
                font-weight: bold;
                font-size: 13px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
                color: white;
                border: 2px solid #B71C1C;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        use_btn.clicked.connect(lambda _, code=coupon["code"]: QApplication.clipboard().setText(code))    

        top_row = QHBoxLayout()
        top_row.addWidget(title_label)
        top_row.addStretch()
        top_row.addWidget(use_btn)

        coupon_layout.addLayout(top_row)
        coupon_layout.addWidget(min_spend_label)
        coupon_layout.addWidget(expiring_label)

        coupon_frame.setLayout(coupon_layout)
        main_layout.addWidget(coupon_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)



# Redeem Coupon Logic
    def redeem_coupon(self):
        code = self.redemption_input.text().strip().upper()
        if code in COUPONS:
            QApplication.clipboard().setText(code)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Coupon Redeemed")
            msg.setText(f"Coupon '{code}' is valid!\nCopied to clipboard. Use it at checkout.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Invalid Coupon")
            msg.setText("This coupon code is not valid.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            msg.exec_()


    def go_back(self):
        self.homepage_window.show()
        self.close()


class NotificationUI(QWidget):
    def __init__(self, notifications, previous_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Notifications")
        self.setGeometry(100, 100, 360, 600)
        self.setStyleSheet("""
            background-color: white;
            border: 3px solid red;
            border-radius: 12px;
        """)
        self.setWindowIcon(QIcon("KKK2.png"))
        

        main_layout = QVBoxLayout()

        
        header_layout = QHBoxLayout()
        back_btn = QPushButton("<- Back")
        back_btn.setFont(QFont("Arial", 11))
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            background-color: red;
            color: white;
            border-radius: 8px;
            padding: 6px 16px;
        """)
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        header_layout.addStretch() 
        main_layout.addLayout(header_layout)

        for note in notifications:
            label = QLabel(note)
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("color: #333; padding: 8px;")
            main_layout.addWidget(label)

        self.setLayout(main_layout)
        self.previous_window = previous_window

        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("background-color: red; color: white; border-radius: 8px;")
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        main_layout.addWidget(clear_btn, alignment=Qt.AlignRight)
        clear_btn.clicked.connect(self.clear_refresh)
        main_layout.addStretch()
        

    def clear_refresh(self):
        clear_notifications()
        self.previous_window.update_notification()
        layout = self.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        layout.addWidget(QLabel("No notifications"))

    def go_back(self):
        self.previous_window.show()
        self.close()
 


#Account Settings
class AccountSettingsUI(QWidget):
    def __init__(self, login_window, homepage_window, accounts, current_user):
        super().__init__()
        self.login_window = login_window  
        self.homepage_window = homepage_window
        self.accounts = accounts
        self.current_user = current_user
        self.setWindowTitle("Account Settings")
        self.setGeometry(100, 100, 350, 600)
        self.setStyleSheet("background-color: white;")
        self.settings_setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))

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
                QPushButton:hover {
                    background-color: #8B0000;
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

        # Create buttons for My Account section and connect signals
        account_security_btn = self.single_button("Account | Security")
        account_security_btn.clicked.connect(self.open_account_security)
        account_security_btn.setCursor(QCursor(Qt.PointingHandCursor))
        account_security_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        bank_accounts_btn = self.single_button("Bank Accounts")
        bank_accounts_btn.setCursor(QCursor(Qt.PointingHandCursor))
        bank_accounts_btn.clicked.connect(self.open_bank_accounts)
        bank_accounts_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        layout.addLayout(self.button_row_widgets(account_security_btn, bank_accounts_btn))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: red; background-color: red; height: 2px;")
        line.setFixedHeight(2)
        layout.addWidget(line)

        layout.addWidget(section_label("Settings"))

        notification_settings_btn = self.single_button("Notification Settings")
        notification_settings_btn.clicked.connect(self.open_notification_settings)
        notification_settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        notification_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        layout.addWidget(notification_settings_btn)

        privacy_settings_btn = self.single_button("Privacy Settings")
        privacy_settings_btn.clicked.connect(self.open_privacy_settings)
        privacy_settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        privacy_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        language_btn = self.single_button("Language")
        language_btn.setCursor(QCursor(Qt.PointingHandCursor))
        language_btn.clicked.connect(self.open_language_settings)
        language_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
                        
                    
        layout.addLayout(self.button_row_widgets(privacy_settings_btn, language_btn))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: red; background-color: red; height: 2px;")
        line.setFixedHeight(2)
        layout.addWidget(line)

        layout.addWidget(section_label("Support"))

        help_centre_btn = self.single_button("Help Centre")
        help_centre_btn.clicked.connect(self.open_help_centre)
        help_centre_btn.setCursor(QCursor(Qt.PointingHandCursor))
        help_centre_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
""")   

        community_rules_btn = self.single_button("Community Rules")
        community_rules_btn.clicked.connect(self.open_community_rules)
        community_rules_btn.setCursor(QCursor(Qt.PointingHandCursor))
        community_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        layout.addLayout(self.button_row_widgets(help_centre_btn, community_rules_btn))

        about_btn = self.single_button("About")
        about_btn.clicked.connect(self.open_about)
        about_btn.setCursor(QCursor(Qt.PointingHandCursor))
        about_btn.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    font-size: 14px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #8B0000;
                    color: white;
                    font-size: 14px;
                    border-radius: 10px;
                }
            """)
        kkkmart_policies_btn = self.single_button("KKKMart Policies")
        kkkmart_policies_btn.setCursor(QCursor(Qt.PointingHandCursor))
        kkkmart_policies_btn.clicked.connect(self.open_kkkmart_policies)
        kkkmart_policies_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
}
        """)
        layout.addLayout(self.button_row_widgets(about_btn, kkkmart_policies_btn))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: red; background-color: red; height: 2px;")
        line.setFixedHeight(2)
        layout.addWidget(line)

        #Switch Button
        switch_btn = QPushButton("Switch Account")
        switch_btn.clicked.connect(self.switch_account)
        switch_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
        """)
        switch_btn.setCursor(QCursor(Qt.PointingHandCursor))
        #Log Out Button
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(QCursor(Qt.PointingHandCursor))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)

        for btn in (switch_btn, logout_btn):
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    font-size: 14px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #8B0000;
                    color: white;
                    font-size: 14px;
                    border-radius: 10px;
                }
            """)

        logout_btn.clicked.connect(self.logout)

        layout.addSpacing(20)
        layout.addWidget(switch_btn)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    # Helper method to create a horizontal layout from two buttons
    def button_row_widgets(self, left_btn, right_btn):
        hbox = QHBoxLayout()
        hbox.addWidget(left_btn)
        hbox.addWidget(right_btn)
        return hbox

    # Stub methods for button click handlers
    def open_account_security(self):
        QMessageBox.information(self, "Account | Security", "Account | Security feature is not implemented yet.")

    def open_bank_accounts(self):
        QMessageBox.information(self, "Bank Accounts", "Bank Accounts feature is not implemented yet.")

    def open_notification_settings(self):
        QMessageBox.information(self, "Notification Settings", "Notification Settings feature is not implemented yet.")

    def open_privacy_settings(self):
        QMessageBox.information(self, "Privacy Settings", "Privacy Settings feature is not implemented yet.")

    def open_language_settings(self):
        QMessageBox.information(self, "Language", "Language feature is not implemented yet.")

    def open_help_centre(self):
        QMessageBox.information(self, "Help Centre", "Help Centre feature is not implemented yet.")

    def open_community_rules(self):
        QMessageBox.information(self, "Community Rules", "Community Rules feature is not implemented yet.")

    def open_about(self):
        self.about_window = AboutUI(self)
        self.about_window.show()
        self.hide()

    def open_kkkmart_policies(self):
        QMessageBox.information(self, "KKKMart Policies", "KKKMart Policies feature is not implemented yet.")

    
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
        return btn

    #Going back to Home Page
    def homepage_again(self):
        self.homepage_window.show()  
        self.close()

    #Switching Account
    def switch_account(self):
        dialog = SwitchAccountDialog(self.accounts, self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_user:
            self.current_user = dialog.selected_user
            self.accounts[self.current_user]["cart"] = []
            self.homepage_window = HomePageUI(username=self.current_user, login_window=self.login_window, accounts=self.accounts)
            self.homepage_window.show()
            self.close()

        
    #Log out and going back to login interface
    def logout(self):
        self.login_window.show()
        self.close()



class SwitchAccountDialog(QDialog):
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Switch Account")
        self.setWindowIcon(QIcon("KKK2.png"))
        self.selected_user = None
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Select an Account")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Account buttons container
        accounts_layout = QVBoxLayout()
        accounts_layout.setSpacing(15)
        
        for username in accounts:
            btn = QPushButton(username)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #D32F2F;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 30px;
                }
                QPushButton:hover {
                    background-color: #B71C1C;
                }
            """)
            btn.clicked.connect(lambda checked, u=username: self.select_user(u))
            accounts_layout.addWidget(btn)
        
        # Add stretch to push buttons to the top
        accounts_layout.addStretch()
        
        # Add cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Add layouts to main layout
        main_layout.addLayout(accounts_layout)
        main_layout.addWidget(cancel_btn)
        
        self.setLayout(main_layout)
        # Set fixed size for the dialog
        self.setMinimumSize(300, 300)

    def select_user(self, user):
        self.selected_user = user
        self.accept()


class AboutUI(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.settings_window = settings_window
        self.setWindowTitle("About KKKMART")
        self.setGeometry(100, 100, 360, 500)
        self.setStyleSheet("background-color: white;")
        self.setWindowIcon(QIcon("KKK2.png"))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Header
        title = QLabel("About KKKMART")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: red;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        about_text = QLabel("""
            KKKMART is a desktop-based shopping app designed to provide users with a smooth and fun shopping experience.

            🛒 Browse and buy a variety of products  
            🔔 Get real-time notifications  
            🧾 Track your purchases  
            🎁 Apply discount coupons  
            🔐 Manage your account securely

            Created with ❤️ by Team KKKMART — PUP Parañaque BSIT Batch 2024-2025
        """)
        about_text.setWordWrap(True)
        about_text.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(about_text)

        back_btn = QPushButton("Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("background-color: red; color: white; border-radius: 8px;")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        layout.addStretch()
        

        self.setLayout(layout)

    def go_back(self):
        self.settings_window.show()
        self.close()


def apply_global_styles(app):
    """Apply global styles to the entire application"""
    app.setStyle('Fusion')  # Use Fusion style for a more modern look
    
    # Set the application-wide font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    # Apply the base style sheet
    style_sheet = f"""
        /* Additional global styles */
        QToolTip {{
            background-color: #333333;
            color: white;
            border: none;
            padding: 6px 10px;
            border-radius: 3px;
            font-size: 12px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 0px;
        }}
        
        QTabBar::tab {{
            background: #F5F5F5;
            border: 1px solid #E0E0E0;
            border-bottom: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background: white;
            border-bottom: 2px solid {PRIMARY_COLOR};
        }}
        
        QHeaderView::section {{
            background-color: #F5F5F5;
            padding: 8px;
            border: none;
            border-right: 1px solid #E0E0E0;
            font-weight: 600;
        }}
        
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: 1px solid {PRIMARY_COLOR};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            min-height: {BUTTON_HEIGHT};
        }}
        
        QPushButton:hover {{
            background-color: {ACCENT_COLOR};
            border-color: {ACCENT_COLOR};
        }}
        
        QPushButton:disabled {{
            background-color: #E0E0E0;
            color: #9E9E9E;
            border: 1px solid #E0E0E0;
        }}
        
        QLabel {{
            font-size: 14px;
            color: {TEXT_COLOR};
        }}
        
        QLabel[required="true"] {{
            color: {ERROR_COLOR};
        }}
        
        QWidget {{
            background-color: {BACKGROUND_COLOR};
        }}
    """
    
    # Apply the combined styles
    app.setStyleSheet(BASE_STYLE + style_sheet)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_global_styles(app)
    
    # Set the application name and organization for settings
    app.setApplicationName("KKKMART")
    app.setOrganizationName("KKKMART")
    
    # Create and show the login window
    window = LoginUI()
    window.show()
    
    sys.exit(app.exec_())
