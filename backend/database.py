import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/stock.db")

# Ensure the /database folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db_connection():
    """Create and return a new database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """Initialize all tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # CLIENTS TABLE
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )

    # CATEGORIES TABLE
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
    """
    )

    # PRODUCTS TABLE
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            alert_threshold INTEGER DEFAULT 5,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        );
    """
    )

    # SALES TABLE
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            total REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        );
    """
    )

    # SALE ITEMS TABLE (many-to-many: sales ↔ products)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
    """
    )

    # PURCHASES TABLE
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT NOT NULL,
            total REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )

    # PURCHASE ITEMS TABLE (many-to-many: purchases ↔ products)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (purchase_id) REFERENCES purchases (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
    """
    )

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


if __name__ == "__main__":
    init_db()
