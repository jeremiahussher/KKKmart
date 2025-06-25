from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem, QMessageBox,
                            QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor, QPixmap, QIcon
import json
import os
import database as db
from add_product import AddProductUI

class SellerHomeUI(QWidget):
    def __init__(self, username, login_window):
        super().__init__()
        self.username = username
        self.login_window = login_window
        self.setWindowTitle("KKKMART - Seller Dashboard")
        self.setGeometry(100, 100, 360, 640)
        self.setStyleSheet("background-color: white;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(f"Welcome, {self.username}")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("color: red; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignCenter)
        
        # Buttons
        add_product_btn = self.create_button("Add New Product", self.open_add_product)
        view_products_btn = self.create_button("View My Products", self.view_products)
        view_orders_btn = self.create_button("View Orders", self.view_orders)
        logout_btn = self.create_button("Logout", self.logout, "background-color: #ff4444;")
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(add_product_btn)
        layout.addWidget(view_products_btn)
        layout.addWidget(view_orders_btn)
        layout.addStretch()
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)

    def create_button(self, text, callback, style=None):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background-color: red;
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
            """ + (style or ""))
        btn.clicked.connect(callback)
        return btn

    def open_add_product(self):
        # Open the add product dialog
        self.add_product_ui = AddProductUI(self)
        self.add_product_ui.show()
        self.hide()

    def view_products(self):
        # Show the product list for this seller
        self.product_list_ui = ProductListUI(self, self.username)
        self.product_list_ui.show()
        self.hide()

    def view_orders(self):
        # This will show orders for this seller's products
        QMessageBox.information(self, "Coming Soon", "Order management will be available soon!")

    def logout(self):
        self.login_window.show()
        self.close()

class ProductListUI(QWidget):
    def __init__(self, parent, seller_username):
        super().__init__()
        self.parent = parent
        self.seller_username = seller_username
        self.setWindowTitle("My Products")
        self.setGeometry(100, 100, 500, 700)  # Slightly larger window
        self.setStyleSheet("""
            QWidget {
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                color: #333;
            }
        """)
        self.setup_ui()
        
        # Set window icon if available
        try:
            self.setWindowIcon(QIcon('icon.png'))
        except:
            pass

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: red;
                font-size: 16px;
                text-align: left;
                padding: 5px;
                min-width: 60px;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        # Title
        title = QLabel("My Products")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: red;")
        
        # Add product button
        add_btn = QPushButton("Add New")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_new_product)
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title, 1, Qt.AlignCenter)
        header_layout.addWidget(add_btn)
        
        # Stats bar
        stats_layout = QHBoxLayout()
        
        # Total products
        total_products = QLabel("Total: 0")
        total_products.setObjectName("total_products")
        total_products.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                color: #0d47a1;
            }
        """)
        
        # Out of stock
        out_of_stock = QLabel("Out of Stock: 0")
        out_of_stock.setObjectName("out_of_stock")
        out_of_stock.setStyleSheet("""
            QLabel {
                background-color: #ffebee;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                color: #c62828;
            }
        """)
        
        stats_layout.addWidget(total_products)
        stats_layout.addWidget(out_of_stock)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search products...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
            }
        """)
        search_btn = QPushButton("🔍")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        search_btn.clicked.connect(lambda: self.search_products(search_input.text()))
        search_input.returnPressed.connect(lambda: self.search_products(search_input.text()))
        
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        
        # Product list
        self.product_list = QListWidget()
        self.product_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 5px;
                background-color: #fafafa;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
            }
        """)
        self.product_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        
        # Add widgets to main layout
        layout.addLayout(header_layout)
        layout.addLayout(stats_layout)
        layout.addLayout(search_layout)
        layout.addWidget(self.product_list, 1)
        
        # Load products
        self.load_products()
        
        # Add widgets to layout
        layout.addWidget(back_btn)
        layout.addWidget(header)
        layout.addWidget(self.product_list)
        
        self.setLayout(layout)
    
    def update_stats(self, products):
        """Update the statistics display with current product data."""
        total = len(products)
        out_of_stock = sum(1 for p in products if p['stock'] <= 0)
        
        total_label = self.findChild(QLabel, "total_products")
        out_of_stock_label = self.findChild(QLabel, "out_of_stock")
        
        if total_label:
            total_label.setText(f"Total: {total}")
        if out_of_stock_label:
            out_of_stock_label.setText(f"Out of Stock: {out_of_stock}")
    
    def load_products(self, search_query=None):
        """Load products from the database for this seller, optionally filtered by search query."""
        self.product_list.clear()
        
        # Get all products for this seller
        products = db.get_products_by_seller(self.seller_username)
        
        # Apply search filter if provided
        if search_query:
            search_query = search_query.lower()
            products = [
                p for p in products 
                if (search_query in p['name'].lower() or 
                    search_query in p['description'].lower())
            ]
        
        # Update statistics
        self.update_stats(products)
        
        if not products:
            no_products = QLabel("No products found. Add your first product!" if not search_query 
                               else "No matching products found.")
            no_products.setStyleSheet("""
                color: #666; 
                font-style: italic; 
                padding: 30px;
                font-size: 14px;
                text-align: center;
            """)
            no_products.setAlignment(Qt.AlignCenter)
            
            # Create a container widget to center the message
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(no_products)
            container_layout.setAlignment(Qt.AlignCenter)
            
            # Add a button to add a new product
            if not search_query:
                add_btn = QPushButton("Add New Product")
                add_btn.setCursor(QCursor(Qt.PointingHandCursor))
                add_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-size: 14px;
                        margin-top: 15px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                add_btn.clicked.connect(self.add_new_product)
                container_layout.addWidget(add_btn, 0, Qt.AlignCenter)
            
            # Add the container to the list
            item = QListWidgetItem()
            item.setSizeHint(container.sizeHint())
            self.product_list.addItem(item)
            self.product_list.setItemWidget(item, container)
            return
        
        for product in products:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, product['id'])
            
            # Create the main container widget
            container = QWidget()
            container.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 8px;
                }
                QLabel#stock {
                    color: #e53935;
                    font-weight: bold;
                }
                QLabel#stock.in-stock {
                    color: #388e3c;
                }
            """)
            
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 15, 10, 15)
            layout.setSpacing(15)
            
            # Product image (left side)
            image_label = QLabel()
            image_label.setFixedSize(80, 80)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: #f5f5f5;
                }
            """)
            
            # Try to load product image, fallback to placeholder
            if product.get('image_path') and os.path.exists(product['image_path']):
                pixmap = QPixmap(product['image_path'])
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(pixmap)
                else:
                    image_label.setText("No Image")
            else:
                image_label.setText("No Image")
            
            # Product info (middle)
            info_layout = QVBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(5)
            
            # Product name
            name_label = QLabel(product['name'])
            name_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 14px;
                    color: #212121;
                }
            """)
            
            # Price and stock
            price_stock_layout = QHBoxLayout()
            
            price_label = QLabel(f"₱{float(product['price']):.2f}")
            price_label.setStyleSheet("""
                QLabel {
                    color: #e53935;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            
            stock = int(product['stock'])
            stock_label = QLabel(f"Stock: {stock}")
            stock_label.setObjectName("stock")
            stock_label.setProperty("class", "in-stock" if stock > 0 else "out-of-stock")
            stock_label.setStyleSheet("""
                QLabel#stock {
                    font-size: 12px;
                    padding: 2px 8px;
                    border-radius: 8px;
                    background-color: #e8f5e9;
                }
                QLabel#stock.out-of-stock {
                    background-color: #ffebee;
                }
            """)
            
            price_stock_layout.addWidget(price_label)
            price_stock_layout.addWidget(stock_label)
            price_stock_layout.addStretch()
            
            # Description (truncated)
            description = product.get('description', '')
            if len(description) > 80:
                description = description[:77] + '...'
                
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #616161;
                    font-size: 12px;
                }
            """)
            desc_label.setWordWrap(True)
            
            # Add to info layout
            info_layout.addWidget(name_label)
            info_layout.addLayout(price_stock_layout)
            info_layout.addWidget(desc_label)
            info_layout.addStretch()
            
            # Action buttons (right side)
            btn_layout = QVBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
            edit_btn.setProperty('product', product)
            edit_btn.setFixedWidth(80)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 6px 0;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #BBDEFB;
                }
            """)
            edit_btn.clicked.connect(lambda _, p=product: self.edit_product(p))
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setProperty('product', product)
            delete_btn.setFixedWidth(80)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 6px 0;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
                QPushButton:disabled {
                    background-color: #FFCDD2;
                }
            """)
            delete_btn.clicked.connect(lambda _, p=product: self.delete_product(p))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            
            # Add all to main layout
            layout.addWidget(image_label)
            layout.addLayout(info_layout, 1)
            layout.addLayout(btn_layout)
            
            # Set the item widget
            item.setSizeHint(container.sizeHint())
            self.product_list.addItem(item)
            self.product_list.setItemWidget(item, container)
    
    def edit_product(self, product):
        # Open the edit product dialog with existing product data
        self.add_product_ui = AddProductUI(self, product)
        self.add_product_ui.show()
        self.hide()
    
    def delete_product(self, product):
        # Confirm before deleting
        reply = QMessageBox.question(
            self, 'Delete Product',
            f'Are you sure you want to delete "{product["name"]}"?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete the product from the database
            conn = db.connect()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM products WHERE id = ?", (product['id'],))
                conn.commit()
                QMessageBox.information(self, 'Success', 'Product deleted successfully!')
                self.load_products()  # Refresh the product list
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to delete product: {str(e)}')
            finally:
                conn.close()
    
    def go_back(self):
        """Return to the seller dashboard."""
        self.parent.show()
        self.close()
        
    def add_new_product(self):
        """Open the add product dialog."""
        self.add_product_ui = AddProductUI(self)
        self.add_product_ui.show()
        self.hide()
        
    def search_products(self, query):
        """Filter products based on search query."""
        self.load_products(query.strip())
        
    def refresh_products(self):
        """Refresh the product list."""
        self.load_products()
        
    def edit_product(self, product):
        """Open the edit product dialog for the selected product."""
        self.add_product_ui = AddProductUI(self, product)
        self.add_product_ui.show()
        self.hide()
        
    def delete_product(self, product):
        """Delete the selected product after confirmation."""
        reply = QMessageBox.question(
            self, 'Delete Product',
            f'Are you sure you want to delete "{product["name"]}"?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = db.connect()
            cursor = conn.cursor()
            try:
                # Delete product images if they exist
                if product.get('image_path') and os.path.exists(product['image_path']):
                    try:
                        os.remove(product['image_path'])
                    except Exception as e:
                        print(f"Error deleting image: {e}")
                
                # Delete from database
                cursor.execute("DELETE FROM products WHERE id = ?", (product['id'],))
                conn.commit()
                
                # Show success message and refresh
                QMessageBox.information(self, 'Success', 'Product deleted successfully!')
                self.load_products()
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to delete product: {str(e)}')
                conn.rollback()
            finally:
                conn.close()