import sys
import re
import os
import json
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, 
    QSizePolicy, QGridLayout, QFrame, QComboBox, QRadioButton, QListWidget,
    QListWidgetItem, QTextEdit, QCheckBox, QGraphicsOpacityEffect, QTabWidget
)
from PyQt5.QtGui import QFont, QCursor, QPixmap, QIcon, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation


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

#Set the Animation
def fade_in_animation(widget, duration=800):
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.start()
    widget.animation = animation  # Prevent garbage collection

#Proceed to Login Interface
class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KKKMART SHOPPING")
        self.setGeometry(100, 100, 350,500)
        self.setFixedSize(350,500)
        self.setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))

    
       #Existing Accounts
        self.users = {
            "admin": "admin123",
            "user": "user123"
        }

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("KKKMART")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: red;")
        fade_in_animation(title)

        subtitle = QLabel("Login to continue.")
        subtitle.setFont(QFont("Poppins", 9))
        subtitle.setAlignment(Qt.AlignCenter)
        fade_in_animation(subtitle)

        self.username_input = self.create_input("Username")
        self.password_input = self.create_input("Password", is_password=True)

        # Show/Hide password button
        self.toggle_password_btn = QPushButton(self)
        self.toggle_password_btn.setIcon(QIcon("open.png"))
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
        fade_in_animation(self.toggle_password_btn)

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
        login_btn = QPushButton("Log in")
        login_btn.setStyleSheet("background-color: red; color: white; font-size: 16px; padding: 10px; border-radius: 10px;")
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        login_btn.clicked.connect(self.login_validation)
        fade_in_animation(login_btn)

        # Register prompt
        text_label = QLabel("Don't have an account?")
        text_label.setStyleSheet("color: gray; font-size: 12px;")

        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("background: transparent; color: red; border: none; font-size: 12px;")
        register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        register_btn.clicked.connect(self.open_register)

        register_row = QHBoxLayout()
        register_row.setAlignment(Qt.AlignCenter)
        register_row.addWidget(text_label)
        register_row.addWidget(register_btn)

        # Social Media Buttons
        social_row = QHBoxLayout()
        for icon in ("F", "G"):
            btn = QPushButton(icon)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("font-size: 20px;")
            social_row.addWidget(btn)

        # Putting all widgets in the layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.username_input, alignment=Qt.AlignLeft)
        layout.addLayout(password_row)
        layout.addWidget(self.remember_checkbox)
        layout.addWidget(login_btn)
        layout.addLayout(register_row)
        layout.addLayout(social_row)

        wrapper = QVBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(layout)
        wrapper.addStretch()
        self.setLayout(wrapper)


    def create_input(self, placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(40)
        input_field.setFixedWidth(270)
        input_field.setStyleSheet("border: 1px solid #ccc; border-radius: 10px; padding: 0 10px;")
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        return input_field

    def login_validation(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in both Username and Password")
            return

        if username in self.users and self.users[username] == password:
            if self.remember_checkbox.isChecked():
                with open("remember_me.json", "w") as f:
                    json.dump({"username": username, "password": password}, f)
            else:
                if os.path.exists("remember_me.json"):
                    os.remove("remember_me.json")

            QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
            self.homepage = HomePageUI(username, self)
            self.homepage.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect Username or Password.")

    def open_register(self):
        self.register_window = RegisterUI(self)
        self.register_window.show()
        self.hide()

    def show_hide_password(self):
        if self.toggle_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setIcon(QIcon("close.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setIcon(QIcon("open.png"))

    def add_new_user(self, username, password):
        self.users[username] = password

#This is Register Window
class RegisterUI(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Create New Account")
        self.setGeometry(100, 100, 350, 500)
        self.setFixedSize(350,500)
        self.setStyleSheet("background-color: white;")
        self.register_setup_ui()
        self.setWindowIcon(QIcon("KKK2.png"))
        

    #Register Setup
    def register_setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Create new\nAccount")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: red;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        subtext = QLabel("Already Registered? Log in here")
        subtext.setFont(QFont("Arial", 10))
        subtext.setStyleSheet("color: grey;")
        layout.addWidget(subtext, alignment=Qt.AlignCenter)

        #All Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Username")
        self.setup_input(self.name_input, layout)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.setup_input(self.email_input, layout)

        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; border-radius: 10px; background-color: lightgray; font-size: 14px;")
        self.password_input.setMinimumHeight(40)

        self.toggle_register_password = QPushButton("Show")
        self.toggle_register_password.setFixedWidth(30)
        self.toggle_register_password.setCheckable(True)
        self.toggle_register_password.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_register_password.clicked.connect(self.password_visibility)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_register_password)
        layout.addLayout(password_layout)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")
        self.setup_input(self.phone_input, layout)

        #Sign Up Button
        self.sign_up_btn = QPushButton("Sign up")
        self.sign_up_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.sign_up_btn.setStyleSheet("background-color: red; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.sign_up_btn.clicked.connect(self.register_validation)
        layout.addWidget(self.sign_up_btn)

        #Back to Login button 
        back_btn = QPushButton("<- Back to Login")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("color: gray; border: none; font-size: 12px;")
        back_btn.clicked.connect(self.back_to_login)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        layout.addSpacing(10)

        social_layout = QHBoxLayout()
        fb_btn = QPushButton("f")
        fb_btn.setFixedSize(40, 40)
        google_btn = QPushButton("G")
        google_btn.setFixedSize(40, 40)
        social_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        social_layout.addWidget(fb_btn)
        social_layout.addWidget(google_btn)
        social_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        layout.addLayout(social_layout)

        wrapper = QVBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(layout)
        wrapper.addStretch()
        self.setLayout(wrapper)

    #All Input setup
    def setup_input(self, widget, layout):
        widget.setStyleSheet("padding: 10px; border-radius: 10px; background-color: lightgray; font-size: 14px;")
        widget.setMinimumHeight(40)
        layout.addWidget(widget)

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

        QMessageBox.information(self, "Registration Successful", f"Welcome, {name}!")
        self.login_window.add_new_user(name, password)
        self.login_window.show()
        self.close()

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
class HomePageUI(QWidget):
    def __init__(self, username, login_window):
        super().__init__()
        self.setWindowTitle("KKKMART - Home")
        self.setGeometry(100, 100, 360, 640)
        self.username = username
        self.login_window = login_window
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
        self.settings_window = AccountSettingsUI(self.login_window, self)
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
        add_notification(f"You purchased {self.name} for ${self.price}!")
        self.checkout_window = CheckoutUI(self.homepage_window, {
            "name": self.name,
            "price": float(self.price.replace("$", "").strip())

        })
        self.checkout_window.show()
        self.hide()
        

    def chat_to_seller(self):
        QMessageBox.information(self, "Chat", f"Starting chat with seller: {self.seller}")

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
        QMessageBox.information(self, "Added to Cart", f"{self.name} has been added to your cart!")

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
        self.product = product
        self.setLayout(layout)
        self.setStyleSheet("border: 1px solid red; border-radius: 10px; padding: 10px;")


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

        self.layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for an item")
        self.search_bar.textChanged.connect(self.filter_items)
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
    def __init__(self, cart_window, product_data=None):  
        super().__init__()
        self.cart_window = cart_window
        self.product_data = product_data or {}
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

        self.subtotal_value = 100  
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

        back_btn = QPushButton("<-- Back to Cart")
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
    
        if self.payment_radio1.isChecked():
            method = "Online"
        
        elif self.payment_radio2.isChecked():
            method = "Bank"
        
        elif self.payment_radio3.isChecked():
            method = "Cash On Delivery"
        else:
            QMessageBox.warning(self, "No Payment Method", "Please select a payment method.")
            return

        self.show_payment_confirmation(method)
    

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
            {"code": "50OFF", "title": "50% off Capped at $50", "min_spend": "$0", "expiring": "23 hours left"},
            {"code": "15OFF", "title": "15% off Capped at $150", "min_spend": "$200", "expiring": "23 hours left"},
            {"code": "20OFF", "title": "20% off Capped at $100", "min_spend": "$300", "expiring": "23 hours left"},
            {"code": "10OFF", "title": "10% OFF", "min_spend": "$0", "expiring": "23 hours left"},
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
        use_btn.setFixedSize(50, 30)
        use_btn.setCursor(QCursor(Qt.PointingHandCursor))
        use_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid red;
                border-radius: 5px;
                color: red;
                background: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B0000;
                color: white;
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
            QMessageBox.information(self, "Coupon Redeemed", f"Coupon '{code}' is valid!\nCopied to clipboard. Use it at checkout.")
        else:
            QMessageBox.warning(self, "Invalid Coupon", "This coupon code is not valid.")


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
    def __init__(self, login_window, homepage_window):
        super().__init__()
        self.login_window = login_window  
        self.homepage_window = homepage_window
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
        return btn

    #Going back to Home Page
    def homepage_again(self):
        self.homepage_window.show()  
        self.close()

    #Log out and going back to login interface
    def logout(self):
        self.login_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginUI()
    window.show()
    sys.exit(app.exec_())
