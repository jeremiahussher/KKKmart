
import sqlite3




def ensure_tables():
    create_users_table()
    # Guarantee new columns on legacy DBs
    add_columns_if_missing(
        "users",
        [
            ("email", "TEXT"),
            ("phone", "TEXT"),
            ("user_type", "TEXT DEFAULT 'buyer'")
        ]
    )
    create_products_table()
    create_cart_table()



def connect():
    """Create and return a database connection."""
    conn = sqlite3.connect("kkkmart.db")
    conn.row_factory = sqlite3.Row  # This enables name-based access to columns
    return conn


def add_columns_if_missing(table, columns):
    """Ensure each (name, type) in columns exists in table; add if missing."""
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    for name, col_type in columns:
        if name not in existing:
            try:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")
            except sqlite3.OperationalError:
                pass
    conn.commit()
    conn.close()

    return sqlite3.connect("kkkmart.db")

def create_users_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            user_type TEXT DEFAULT 'buyer'
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password, email=None, phone=None, user_type='buyer'):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, email, phone, user_type) 
            VALUES (?, ?, ?, ?, ?)
        """, (username, password, email, phone, user_type))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_type(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_type FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'buyer'

def update_user_info(username, email=None, phone=None, password=None):
    """Update user fields that are not None."""
    conn = connect()
    cursor = conn.cursor()
    fields=[]; values=[]
    if email is not None:
        fields.append("email=?"); values.append(email)
    if phone is not None:
        fields.append("phone=?"); values.append(phone)
    if password is not None:
        fields.append("password=?"); values.append(password)
    if not fields:
        conn.close(); return False
    values.append(username)
    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE username=?", values)
    conn.commit(); conn.close(); return True

def update_password(username, new_password):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()
    return True

def create_products_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            description TEXT,
            image_path TEXT,
            seller_username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_username) REFERENCES users(username)
        )
    """)
    conn.commit()
    conn.close()

def add_product(name, price, stock, description, image_path, seller_username):
    """Add a new product to the database."""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, price, stock, description, image_path, seller_username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, price, stock, description, image_path, seller_username))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding product: {e}")
        return None
    finally:
        conn.close()

def get_products_by_seller(seller_username):
    """Get all products listed by a specific seller."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products 
        WHERE seller_username = ?
        ORDER BY created_at DESC
    """, (seller_username,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_all_products():
    """Get all available products."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products 
        WHERE stock > 0
        ORDER BY created_at DESC
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def get_product(product_id):
    """Get a single product by ID."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def update_product_stock(product_id, quantity_change):
    """Update the stock level of a product."""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE products 
            SET stock = stock + ? 
            WHERE id = ? AND (stock + ?) >= 0
        """, (quantity_change, product_id, quantity_change))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating product stock: {e}")
        return False
    finally:
        conn.close()

# This function is kept for backward compatibility
# Use get_all_products() instead for new code
def fetch_products():
    return get_all_products()

def total_users():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def total_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def top_product_by_price():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products ORDER BY price DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None)


def create_cart_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()