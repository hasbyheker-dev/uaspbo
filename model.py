"""
model.py - Lapisan Data (Model Layer)
======================================
Modul ini mengurus:
- Skema tabel SQLite dan koneksi database
- Query SQL untuk operasi CRUD
- Validasi integritas data sebelum disimpan

Pilar OOP yang diterapkan:
- ENCAPSULATION: Atribut koneksi database bersifat private (__connection, __db_path)
  sehingga tidak dapat diakses/dimodifikasi langsung dari luar class.

Prinsip DRY (Don't Repeat Yourself):
- Semua query database terpusat di modul ini.
- Tidak ada duplikasi koneksi atau query di file lain.
"""

import sqlite3
import os
from datetime import datetime, date


# ============================================================
# CLASS: Database (Singleton Pattern + Encapsulation)
# ============================================================

class Database:
    """
    Singleton class untuk manajemen koneksi database SQLite.
    
    ENCAPSULATION diterapkan pada:
    - __db_path     : path ke file database (private)
    - __connection  : objek koneksi SQLite (private)
    - __initialized : flag inisialisasi singleton (private)
    
    Akses ke database hanya melalui method publik:
    execute(), fetch_all(), fetch_one(), close()
    """

    _instance = None

    def __new__(cls):
        """Implementasi Singleton: hanya satu instance Database."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._Database__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.__db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "pos_kasir.db"
        )
        self.__connection = None
        self.__connect()
        self.__create_tables()

    # --- Private Methods (Encapsulation) ---

    def __connect(self):
        """Membuka koneksi ke database SQLite (private method)."""
        try:
            self.__connection = sqlite3.connect(self.__db_path)
            self.__connection.execute("PRAGMA foreign_keys = ON")
            self.__connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"Gagal koneksi ke database: {e}")

    def __create_tables(self):
        """Membuat tabel-tabel yang diperlukan jika belum ada (private method)."""
        cursor = self.__connection.cursor()
        try:
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    code        TEXT    UNIQUE NOT NULL,
                    name        TEXT    NOT NULL,
                    category    TEXT    NOT NULL,
                    buy_price   REAL    NOT NULL,
                    sell_price  REAL    NOT NULL,
                    stock       INTEGER NOT NULL DEFAULT 0,
                    created_at  TEXT    DEFAULT (datetime('now', 'localtime'))
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_no    TEXT    UNIQUE NOT NULL,
                    date          TEXT    DEFAULT (datetime('now', 'localtime')),
                    total         REAL    NOT NULL,
                    payment       REAL    NOT NULL,
                    change_amount REAL    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS transaction_items (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id  INTEGER NOT NULL,
                    product_id      INTEGER NOT NULL,
                    product_name    TEXT    NOT NULL,
                    price           REAL    NOT NULL,
                    quantity        INTEGER NOT NULL,
                    subtotal        REAL    NOT NULL,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
            """)
            self.__connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Gagal membuat tabel: {e}")

    # --- Public Methods ---

    def execute(self, query, params=None):
        """
        Eksekusi query INSERT/UPDATE/DELETE dengan commit otomatis.
        Rollback otomatis jika terjadi error.
        """
        cursor = self.__connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.__connection.commit()
            return cursor
        except sqlite3.Error:
            self.__connection.rollback()
            raise

    def fetch_all(self, query, params=None):
        """Ambil semua baris dari query SELECT. Return: list of dict."""
        cursor = self.__connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetch_one(self, query, params=None):
        """Ambil satu baris dari query SELECT. Return: dict atau None."""
        cursor = self.__connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        """Tutup koneksi database dengan aman."""
        if self.__connection:
            self.__connection.close()
            self.__connection = None


# ============================================================
# CLASS: ProductModel (CRUD + Validasi)
# ============================================================

class ProductModel:
    """
    Model untuk operasi CRUD pada tabel products.
    
    ENCAPSULATION: Atribut __db bersifat private.
    Menyediakan validasi data sebelum setiap operasi database.
    """

    def __init__(self):
        self.__db = Database()

    def validate(self, data):
        """
        Validasi data produk sebelum disimpan ke database.
        Return: list of error messages (kosong jika valid).
        """
        errors = []

        if not data.get('code', '').strip():
            errors.append("Kode produk tidak boleh kosong.")
        if not data.get('name', '').strip():
            errors.append("Nama produk tidak boleh kosong.")
        if not data.get('category', '').strip():
            errors.append("Kategori tidak boleh kosong.")

        # Validasi harga beli (harus angka, tidak negatif)
        try:
            buy_price = float(data.get('buy_price', ''))
            if buy_price < 0:
                errors.append("Harga beli tidak boleh negatif.")
        except (ValueError, TypeError):
            errors.append("Harga beli harus berupa angka.")

        # Validasi harga jual (harus angka, tidak negatif)
        try:
            sell_price = float(data.get('sell_price', ''))
            if sell_price < 0:
                errors.append("Harga jual tidak boleh negatif.")
        except (ValueError, TypeError):
            errors.append("Harga jual harus berupa angka.")

        # Validasi stok (harus integer, tidak negatif)
        try:
            stock = int(data.get('stock', ''))
            if stock < 0:
                errors.append("Stok tidak boleh negatif.")
        except (ValueError, TypeError):
            errors.append("Stok harus berupa angka bulat.")

        return errors

    def create(self, data):
        """
        Tambah produk baru ke database.
        Return: (success: bool, message: str | list)
        """
        errors = self.validate(data)
        if errors:
            return False, errors

        try:
            self.__db.execute(
                """INSERT INTO products (code, name, category, buy_price, sell_price, stock)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    data['code'].strip().upper(),
                    data['name'].strip(),
                    data['category'].strip(),
                    float(data['buy_price']),
                    float(data['sell_price']),
                    int(data['stock'])
                )
            )
            return True, "Produk berhasil ditambahkan!"
        except sqlite3.IntegrityError:
            return False, ["Kode produk sudah digunakan."]
        except sqlite3.Error as e:
            return False, [f"Gagal menyimpan produk: {e}"]

    def read_all(self):
        """Ambil semua produk, urut berdasarkan ID terbaru."""
        try:
            return self.__db.fetch_all(
                "SELECT * FROM products ORDER BY id DESC"
            )
        except sqlite3.Error:
            return []

    def search(self, keyword):
        """Cari produk berdasarkan kode, nama, atau kategori."""
        try:
            kw = f"%{keyword}%"
            return self.__db.fetch_all(
                """SELECT * FROM products 
                   WHERE code LIKE ? OR name LIKE ? OR category LIKE ?
                   ORDER BY name ASC""",
                (kw, kw, kw)
            )
        except sqlite3.Error:
            return []

    def read_by_id(self, product_id):
        """Ambil satu produk berdasarkan ID."""
        try:
            return self.__db.fetch_one(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            )
        except sqlite3.Error:
            return None

    def update(self, product_id, data):
        """
        Perbarui data produk berdasarkan ID.
        Kode produk (Primary Key) tidak diubah.
        """
        errors = self.validate(data)
        if errors:
            return False, errors

        try:
            self.__db.execute(
                """UPDATE products 
                   SET name=?, category=?, buy_price=?, sell_price=?, stock=?
                   WHERE id=?""",
                (
                    data['name'].strip(),
                    data['category'].strip(),
                    float(data['buy_price']),
                    float(data['sell_price']),
                    int(data['stock']),
                    product_id
                )
            )
            return True, "Produk berhasil diperbarui!"
        except sqlite3.Error as e:
            return False, [f"Gagal memperbarui produk: {e}"]

    def delete(self, product_id):
        """Hapus produk berdasarkan ID."""
        try:
            self.__db.execute(
                "DELETE FROM products WHERE id=?", (product_id,)
            )
            return True, "Produk berhasil dihapus!"
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                return False, "Produk tidak bisa dihapus karena sudah ada di riwayat transaksi.\n\nTips: Jika produk tidak dijual lagi, cukup ubah stoknya menjadi 0 alih-alih menghapusnya."
            return False, f"Gagal menghapus produk (Integritas data): {e}"
        except sqlite3.Error as e:
            return False, f"Gagal menghapus produk: {e}"

    def update_stock(self, product_id, quantity_sold):
        """Kurangi stok produk setelah penjualan (atau tambah jika negatif)."""
        try:
            self.__db.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity_sold, product_id)
            )
            return True
        except sqlite3.Error:
            return False

    def get_categories(self):
        """Ambil daftar kategori unik yang sudah ada di database."""
        try:
            rows = self.__db.fetch_all(
                "SELECT DISTINCT category FROM products ORDER BY category"
            )
            return [row['category'] for row in rows]
        except sqlite3.Error:
            return []

    def get_available_products(self):
        """Ambil semua produk yang stoknya > 0 (untuk kasir)."""
        try:
            return self.__db.fetch_all(
                "SELECT * FROM products WHERE stock > 0 ORDER BY name"
            )
        except sqlite3.Error:
            return []

    def search_available(self, keyword):
        """Cari produk tersedia (stok > 0) berdasarkan kode atau nama."""
        try:
            kw = f"%{keyword}%"
            return self.__db.fetch_all(
                """SELECT * FROM products 
                   WHERE stock > 0 AND (code LIKE ? OR name LIKE ?)
                   ORDER BY name ASC""",
                (kw, kw)
            )
        except sqlite3.Error:
            return []


# ============================================================
# CLASS: TransactionModel
# ============================================================

class TransactionModel:
    """
    Model untuk operasi transaksi penjualan.
    Menangani pembuatan invoice, penyimpanan transaksi + detail item,
    dan pembacaan riwayat transaksi.
    """

    def __init__(self):
        self.__db = Database()

    def generate_invoice(self):
        """Generate nomor invoice unik: INV-YYYYMMDD-XXXX."""
        today = date.today().strftime("%Y%m%d")
        try:
            result = self.__db.fetch_one(
                """SELECT COUNT(*) as count FROM transactions 
                   WHERE invoice_no LIKE ?""",
                (f"INV-{today}-%",)
            )
            count = (result['count'] + 1) if result else 1
            return f"INV-{today}-{count:04d}"
        except sqlite3.Error:
            return f"INV-{today}-{datetime.now().strftime('%H%M%S')}"

    def create(self, invoice_no, total, payment, change_amount, items):
        """
        Buat transaksi baru beserta detail item dan update stok.
        
        Parameters:
            invoice_no  : Nomor invoice unik
            total       : Total belanja
            payment     : Jumlah pembayaran
            change_amount: Kembalian
            items       : list of dict {product_id, product_name, price, quantity, subtotal}
        
        Return: (success: bool, message: str)
        """
        try:
            # 1. Insert header transaksi
            cursor = self.__db.execute(
                """INSERT INTO transactions (invoice_no, total, payment, change_amount)
                   VALUES (?, ?, ?, ?)""",
                (invoice_no, total, payment, change_amount)
            )
            transaction_id = cursor.lastrowid

            # 2. Insert detail item transaksi
            for item in items:
                self.__db.execute(
                    """INSERT INTO transaction_items 
                       (transaction_id, product_id, product_name, price, quantity, subtotal)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        transaction_id,
                        item['product_id'],
                        item['product_name'],
                        item['price'],
                        item['quantity'],
                        item['subtotal']
                    )
                )

            # 3. Update stok produk (kurangi sesuai quantity terjual)
            product_model = ProductModel()
            for item in items:
                product_model.update_stock(item['product_id'], item['quantity'])

            return True, f"Transaksi {invoice_no} berhasil disimpan!"
        except sqlite3.Error as e:
            return False, f"Gagal menyimpan transaksi: {e}"

    def read_all(self):
        """Ambil semua riwayat transaksi, urut terbaru."""
        try:
            return self.__db.fetch_all(
                "SELECT * FROM transactions ORDER BY id DESC"
            )
        except sqlite3.Error:
            return []

    def read_items(self, transaction_id):
        """Ambil detail item dari sebuah transaksi."""
        try:
            return self.__db.fetch_all(
                """SELECT * FROM transaction_items 
                   WHERE transaction_id = ? ORDER BY id""",
                (transaction_id,)
            )
        except sqlite3.Error:
            return []

    def delete(self, transaction_id):
        """Hapus transaksi dan kembalikan stok produk yang terjual."""
        try:
            # Kembalikan stok (kurangi dengan nilai negatif = menambah)
            items = self.read_items(transaction_id)
            product_model = ProductModel()
            for item in items:
                product_model.update_stock(item['product_id'], -item['quantity'])

            self.__db.execute(
                "DELETE FROM transactions WHERE id=?", (transaction_id,)
            )
            return True, "Transaksi berhasil dihapus dan stok dikembalikan!"
        except sqlite3.Error as e:
            return False, f"Gagal menghapus transaksi: {e}"

    def search_by_invoice(self, keyword):
        """Cari transaksi berdasarkan nomor invoice."""
        try:
            return self.__db.fetch_all(
                """SELECT * FROM transactions 
                   WHERE invoice_no LIKE ?
                   ORDER BY id DESC""",
                (f"%{keyword}%",)
            )
        except sqlite3.Error:
            return []


# ============================================================
# CLASS: DashboardModel (Statistik Agregat)
# ============================================================

class DashboardModel:
    """
    Model untuk data statistik dan ringkasan dashboard.
    Menyediakan query agregat (COUNT, SUM) untuk tampilan dashboard.
    """

    def __init__(self):
        self.__db = Database()

    def get_total_products(self):
        """Hitung jumlah total produk terdaftar."""
        try:
            result = self.__db.fetch_one("SELECT COUNT(*) as total FROM products")
            return result['total'] if result else 0
        except sqlite3.Error:
            return 0

    def get_total_stock(self):
        """Hitung total stok keseluruhan dari semua produk."""
        try:
            result = self.__db.fetch_one(
                "SELECT COALESCE(SUM(stock), 0) as total FROM products"
            )
            return result['total'] if result else 0
        except sqlite3.Error:
            return 0

    def get_out_of_stock_count(self):
        """Hitung jumlah produk yang stoknya habis (= 0)."""
        try:
            result = self.__db.fetch_one(
                "SELECT COUNT(*) as total FROM products WHERE stock = 0"
            )
            return result['total'] if result else 0
        except sqlite3.Error:
            return 0

    def get_low_stock_products(self, threshold=5):
        """Ambil daftar produk dengan stok rendah (≤ threshold)."""
        try:
            return self.__db.fetch_all(
                """SELECT code, name, stock FROM products 
                   WHERE stock <= ? AND stock > 0 
                   ORDER BY stock ASC""",
                (threshold,)
            )
        except sqlite3.Error:
            return []

    def get_today_transactions(self):
        """Hitung jumlah transaksi hari ini."""
        try:
            result = self.__db.fetch_one(
                """SELECT COUNT(*) as total FROM transactions 
                   WHERE date(date) = date('now', 'localtime')"""
            )
            return result['total'] if result else 0
        except sqlite3.Error:
            return 0

    def get_today_revenue(self):
        """Hitung total pendapatan (revenue) hari ini."""
        try:
            result = self.__db.fetch_one(
                """SELECT COALESCE(SUM(total), 0) as revenue FROM transactions 
                   WHERE date(date) = date('now', 'localtime')"""
            )
            return result['revenue'] if result else 0
        except sqlite3.Error:
            return 0

    def get_total_revenue(self):
        """Hitung total pendapatan keseluruhan (semua waktu)."""
        try:
            result = self.__db.fetch_one(
                "SELECT COALESCE(SUM(total), 0) as revenue FROM transactions"
            )
            return result['revenue'] if result else 0
        except sqlite3.Error:
            return 0

    def get_total_transactions(self):
        """Hitung jumlah total semua transaksi."""
        try:
            result = self.__db.fetch_one(
                "SELECT COUNT(*) as total FROM transactions"
            )
            return result['total'] if result else 0
        except sqlite3.Error:
            return 0

    def get_recent_transactions(self, limit=5):
        """Ambil transaksi terbaru (default: 5 terakhir)."""
        try:
            return self.__db.fetch_all(
                "SELECT * FROM transactions ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        except sqlite3.Error:
            return []
