from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QMessageBox, QFileDialog,
                            QSpinBox, QDoubleSpinBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor, QPixmap
import os
import database as db

class AddProductUI(QWidget):
    def __init__(self, parent=None, product=None):
        super().__init__()
        self.parent = parent
        self.product = product
        self.setWindowTitle("Edit Product" if product else "Add New Product")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("background-color: white;")
        self.image_path = None
        self.setup_ui()
        
        # If editing an existing product, load its data
        if product:
            self.load_product_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Edit Product" if hasattr(self, 'product') and self.product else "Add New Product")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("color: red; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignCenter)
        
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
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        # Product Image
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No image selected\n(Click to add)")
        self.image_label.mousePressEvent = self.select_image
        
        # Form fields
        self.name_input = self.create_input("Product Name")
        
        price_layout = QHBoxLayout()
        price_label = QLabel("Price:")
        price_label.setStyleSheet("font-size: 14px;")
        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("₱ ")
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999999.99)
        self.price_input.setSingleStep(1.0)
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        
        stock_layout = QHBoxLayout()
        stock_label = QLabel("Stock:")
        stock_label.setStyleSheet("font-size: 14px;")
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(9999)
        stock_layout.addWidget(stock_label)
        stock_layout.addWidget(self.stock_input)
        
        description_label = QLabel("Description:")
        description_label.setStyleSheet("font-size: 14px;")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter product description...")
        self.description_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                min-height: 100px;
            }
        """)
        
        # Submit button
        submit_text = "Update Product" if hasattr(self, 'product') and self.product else "Add Product"
        submit_btn = QPushButton(submit_text)
        submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        submit_btn.clicked.connect(self.save_product)
        
        # Add widgets to layout
        layout.addWidget(back_btn)
        layout.addWidget(header)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.name_input)
        layout.addLayout(price_layout)
        layout.addLayout(stock_layout)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(submit_btn)
        
        self.setLayout(layout)
    
    def create_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        return input_field
    
    def select_image(self, event):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Select Product Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.image_label.setText("")
    
    def load_product_data(self):
        """Load existing product data into the form."""
        if not self.product:
            return
            
        self.name_input.setText(self.product.get('name', ''))
        self.price_input.setValue(float(self.product.get('price', 0)))
        self.stock_input.setValue(int(self.product.get('stock', 0)))
        self.description_input.setPlainText(self.product.get('description', ''))
        
        # Load image if exists
        image_path = self.product.get('image_path')
        if image_path and os.path.exists(image_path):
            self.image_path = image_path
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
    
    def save_product(self):
        name = self.name_input.text().strip()
        price = self.price_input.value()
        stock = self.stock_input.value()
        description = self.description_input.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a product name")
            return
            
        if price <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid price")
            return
            
        if stock < 0:
            QMessageBox.warning(self, "Error", "Stock cannot be negative")
            return
        
        # Handle image
        image_filename = self.product.get('image_path') if hasattr(self, 'product') and self.product else None
        
        if self.image_path and self.image_path != image_filename:
            # Create images directory if it doesn't exist
            if not os.path.exists("product_images"):
                os.makedirs("product_images")
                
            # Generate a unique filename
            import uuid
            ext = os.path.splitext(self.image_path)[1]
            image_filename = f"product_images/{uuid.uuid4()}{ext}"
            
            # Copy the image to the new location
            import shutil
            shutil.copy2(self.image_path, image_filename)
        
        try:
            if hasattr(self, 'product') and self.product:
                # Update existing product
                conn = db.connect()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE products 
                    SET name = ?, price = ?, stock = ?, description = ?
                    """ + (f", image_path = ?" if image_filename else "") + """
                    WHERE id = ?
                """, (
                    name, price, stock, description,
                    *((image_filename, self.product['id']) if image_filename else (self.product['id'],))
                ))
                conn.commit()
                message = "Product updated successfully!"
            else:
                # Add new product
                if not image_filename:
                    QMessageBox.warning(self, "Error", "Please select an image for the product")
                    return
                    
                db.add_product(
                    name=name,
                    price=price,
                    stock=stock,
                    description=description,
                    image_path=image_filename,
                    seller_username=self.parent.parent.username
                )
                message = "Product added successfully!"
                
            QMessageBox.information(self, "Success", message)
            self.go_back()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def go_back(self):
        if self.parent:
            self.parent.show()
        self.close()