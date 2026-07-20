"""
view.py - Lapisan Antarmuka (View Layer)
=========================================
Modul ini HANYA berisi komponen visual Tkinter.
DILARANG KERAS memuat fungsi SQL (sqlite3) di file ini.

Pilar OOP yang diterapkan:
- INHERITANCE  : Semua halaman mewarisi class BasePage(tk.Frame).
- POLYMORPHISM : Method setup_ui() dan on_page_show() di-override
                 oleh setiap halaman dengan implementasi berbeda.
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# KONSTANTA DESAIN (Warna, Font, Kategori Default)
# ============================================================

COLORS = {
    'primary':        '#1e3a5f',
    'primary_light':  '#2c5282',
    'primary_dark':   '#152a45',
    'accent':         '#38a169',
    'accent_hover':   '#2f855a',
    'warning':        '#dd6b20',
    'danger':         '#e53e3e',
    'danger_hover':   '#c53030',
    'info':           '#3182ce',
    'bg':             '#edf2f7',
    'card':           '#ffffff',
    'text':           '#2d3748',
    'text_secondary': '#718096',
    'text_light':     '#a0aec0',
    'border':         '#e2e8f0',
    'entry_bg':       '#f7fafc',
    'tree_odd':       '#ffffff',
    'tree_even':      '#f7fafc',
    'tree_select':    '#bee3f8',
}

FONTS = {
    'title':       ('Segoe UI', 18, 'bold'),
    'subtitle':    ('Segoe UI', 14, 'bold'),
    'heading':     ('Segoe UI', 12, 'bold'),
    'body':        ('Segoe UI', 10),
    'body_bold':   ('Segoe UI', 10, 'bold'),
    'small':       ('Segoe UI', 9),
    'small_bold':  ('Segoe UI', 9, 'bold'),
    'stat_number': ('Segoe UI', 26, 'bold'),
    'stat_label':  ('Segoe UI', 10),
    'price_big':   ('Segoe UI', 16, 'bold'),
    'menu':        ('Segoe UI', 10),
}

DEFAULT_CATEGORIES = [
    "Makanan", "Minuman", "Snack", "Rokok",
    "Alat Tulis", "Elektronik", "Obat-obatan",
    "Sabun & Deterjen", "Bumbu Dapur", "Lainnya"
]


# ============================================================
# FUNGSI HELPER
# ============================================================

def format_rupiah(amount):
    """Format angka menjadi format Rupiah Indonesia (Rp 1.000.000)."""
    try:
        return f"Rp {int(amount):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


# ============================================================
# CLASS: BasePage (Inheritance Base + Polymorphism)
# ============================================================

class BasePage(tk.Frame):
    """
    Kelas induk (parent class) untuk semua halaman aplikasi.
    
    INHERITANCE: DashboardPage, ProductPage, CashierPage, TransactionPage
    semuanya mewarisi class BasePage ini.
    
    POLYMORPHISM: Method setup_ui() dan on_page_show() dipanggil secara
    polimorfik — setiap subclass memiliki implementasi yang berbeda-beda
    sesuai kebutuhan halaman masing-masing.
    """

    def __init__(self, parent, controller):
        """
        Inisialisasi BasePage.
        
        Args:
            parent     : Widget induk (container frame)
            controller : Referensi ke App (main.py) untuk pemanggilan method controller
        """
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        """
        Override method ini di subclass untuk membangun UI halaman.
        Menerapkan POLYMORPHISM: setiap halaman punya layout berbeda.
        """
        raise NotImplementedError("Subclass harus mengimplementasikan setup_ui()")

    def on_page_show(self):
        """
        Dipanggil setiap kali halaman ditampilkan (tkraise).
        Override di subclass untuk refresh/reload data.
        Menerapkan POLYMORPHISM: setiap halaman refresh data berbeda.
        """
        pass

    def _create_title_bar(self, icon, title):
        """Buat title bar berwarna di atas halaman (reusable component)."""
        title_frame = tk.Frame(self, bg=COLORS['primary'], height=50)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text=f"  {icon}  {title}",
            font=FONTS['subtitle'],
            bg=COLORS['primary'],
            fg='white',
            anchor='w'
        ).pack(fill=tk.X, padx=15, expand=True)

        return title_frame

    def _create_separator(self, parent, color=None):
        """Buat garis pemisah horizontal."""
        sep = tk.Frame(parent, bg=color or COLORS['border'], height=1)
        sep.pack(fill=tk.X, pady=8)
        return sep

    def _configure_tree_tags(self, tree):
        """Konfigurasi warna baris genap/ganjil pada Treeview."""
        tree.tag_configure('oddrow', background=COLORS['tree_odd'])
        tree.tag_configure('evenrow', background=COLORS['tree_even'])


# ============================================================
# CLASS: DashboardPage (Mewarisi BasePage)
# ============================================================

class DashboardPage(BasePage):
    """
    Halaman Dashboard — Menampilkan ringkasan statistik toko.
    
    INHERITANCE  : Mewarisi BasePage.
    POLYMORPHISM : Override setup_ui() dan on_page_show().
    """

    def setup_ui(self):
        """Bangun UI dashboard: kartu statistik + tabel transaksi terbaru."""
        self._create_title_bar("🏠", "DASHBOARD")

        # Scrollable content area
        content = tk.Frame(self, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # ── Row 1: Stat Cards ──
        cards_frame = tk.Frame(content, bg=COLORS['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 15))
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        self.lbl_total_products = self._create_stat_card(
            cards_frame, "📦", "Total Produk", "0", COLORS['info'], 0
        )
        self.lbl_total_stock = self._create_stat_card(
            cards_frame, "📊", "Total Stok", "0", COLORS['accent'], 1
        )
        self.lbl_today_transactions = self._create_stat_card(
            cards_frame, "🛒", "Transaksi Hari Ini", "0", COLORS['warning'], 2
        )
        self.lbl_today_revenue = self._create_stat_card(
            cards_frame, "💰", "Pendapatan Hari Ini", "Rp 0", COLORS['primary'], 3
        )

        # ── Row 2: Two columns ──
        bottom_frame = tk.Frame(content, bg=COLORS['bg'])
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        bottom_frame.columnconfigure(0, weight=3)
        bottom_frame.columnconfigure(1, weight=2)

        # Left: Recent Transactions
        recent_card = tk.LabelFrame(
            bottom_frame, text="  📋 Transaksi Terbaru  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        recent_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        cols_recent = ('no', 'invoice', 'tanggal', 'total')
        self.tree_recent = ttk.Treeview(
            recent_card, columns=cols_recent, show='headings', height=8
        )
        self.tree_recent.heading('no', text='No')
        self.tree_recent.heading('invoice', text='No. Invoice')
        self.tree_recent.heading('tanggal', text='Tanggal')
        self.tree_recent.heading('total', text='Total')

        self.tree_recent.column('no', width=40, anchor='center')
        self.tree_recent.column('invoice', width=170, anchor='w')
        self.tree_recent.column('tanggal', width=150, anchor='center')
        self.tree_recent.column('total', width=130, anchor='e')

        self._configure_tree_tags(self.tree_recent)
        self.tree_recent.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Right: Summary Card
        summary_card = tk.LabelFrame(
            bottom_frame, text="  📈 Ringkasan  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        summary_card.grid(row=0, column=1, sticky="nsew")

        summary_inner = tk.Frame(summary_card, bg=COLORS['card'])
        summary_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Total Revenue
        tk.Label(summary_inner, text="Total Pendapatan Keseluruhan",
                 font=FONTS['small'], bg=COLORS['card'],
                 fg=COLORS['text_secondary']).pack(anchor='w')
        self.lbl_total_revenue = tk.Label(
            summary_inner, text="Rp 0",
            font=('Segoe UI', 20, 'bold'), bg=COLORS['card'],
            fg=COLORS['accent']
        )
        self.lbl_total_revenue.pack(anchor='w', pady=(2, 15))

        self._create_separator(summary_inner)

        # Total Transactions
        tk.Label(summary_inner, text="Total Seluruh Transaksi",
                 font=FONTS['small'], bg=COLORS['card'],
                 fg=COLORS['text_secondary']).pack(anchor='w', pady=(5, 0))
        self.lbl_total_transactions = tk.Label(
            summary_inner, text="0 transaksi",
            font=FONTS['subtitle'], bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.lbl_total_transactions.pack(anchor='w', pady=(2, 15))

        self._create_separator(summary_inner)

        # Out of Stock Warning
        tk.Label(summary_inner, text="⚠️  Produk Stok Habis",
                 font=FONTS['small'], bg=COLORS['card'],
                 fg=COLORS['danger']).pack(anchor='w', pady=(5, 0))
        self.lbl_out_of_stock = tk.Label(
            summary_inner, text="0 produk",
            font=FONTS['subtitle'], bg=COLORS['card'],
            fg=COLORS['danger']
        )
        self.lbl_out_of_stock.pack(anchor='w', pady=(2, 0))

    def _create_stat_card(self, parent, icon, title, value, color, col):
        """Buat kartu statistik individual untuk dashboard."""
        card = tk.Frame(parent, bg=COLORS['card'], relief=tk.GROOVE, bd=1)
        card.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        inner = tk.Frame(card, bg=COLORS['card'])
        inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=14)

        # Colored accent bar at top
        accent = tk.Frame(card, bg=color, height=3)
        accent.place(x=0, y=0, relwidth=1)

        tk.Label(inner, text=f"{icon}  {title}", font=FONTS['stat_label'],
                 bg=COLORS['card'], fg=COLORS['text_secondary']).pack(anchor='w')

        lbl = tk.Label(inner, text=value, font=FONTS['stat_number'],
                       bg=COLORS['card'], fg=color)
        lbl.pack(anchor='w', pady=(5, 0))

        return lbl

    def on_page_show(self):
        """Refresh data dashboard setiap kali halaman ditampilkan."""
        self.controller.refresh_dashboard()


# ============================================================
# CLASS: ProductPage (Mewarisi BasePage)
# ============================================================

class ProductPage(BasePage):
    """
    Halaman Manajemen Produk — CRUD lengkap untuk data produk.
    
    INHERITANCE  : Mewarisi BasePage.
    POLYMORPHISM : Override setup_ui() dan on_page_show().
    """

    def setup_ui(self):
        """Bangun UI form input produk dan tabel Treeview."""
        self._create_title_bar("📦", "MANAJEMEN PRODUK")

        content = tk.Frame(self, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Track ID produk yang sedang di-edit
        self.selected_product_id = None

        # ── Form Input Section ──
        form_frame = tk.LabelFrame(
            content, text="  📝 Form Input Produk  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        form_frame.pack(fill=tk.X, pady=(0, 12))

        form_inner = tk.Frame(form_frame, bg=COLORS['card'])
        form_inner.pack(fill=tk.X, padx=15, pady=15)

        # Row 0: Kode Produk & Nama Produk
        tk.Label(form_inner, text="Kode Produk :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=0, column=0, sticky='w', padx=(0, 8), pady=5)
        self.entry_code = tk.Entry(form_inner, font=FONTS['body'], width=18,
                                   relief=tk.SOLID, bd=1, bg=COLORS['entry_bg'])
        self.entry_code.grid(row=0, column=1, sticky='w', padx=(0, 25), pady=5)

        tk.Label(form_inner, text="Nama Produk :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=0, column=2, sticky='w', padx=(0, 8), pady=5)
        self.entry_name = tk.Entry(form_inner, font=FONTS['body'], width=28,
                                   relief=tk.SOLID, bd=1, bg=COLORS['entry_bg'])
        self.entry_name.grid(row=0, column=3, sticky='w', pady=5)

        # Row 1: Kategori & Harga Beli
        tk.Label(form_inner, text="Kategori :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=1, column=0, sticky='w', padx=(0, 8), pady=5)
        self.cmb_category = ttk.Combobox(form_inner, font=FONTS['body'], width=16,
                                         values=DEFAULT_CATEGORIES, state='normal')
        self.cmb_category.grid(row=1, column=1, sticky='w', padx=(0, 25), pady=5)

        tk.Label(form_inner, text="Harga Beli (Rp) :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=1, column=2, sticky='w', padx=(0, 8), pady=5)
        self.entry_buy_price = tk.Entry(form_inner, font=FONTS['body'], width=18,
                                        relief=tk.SOLID, bd=1, bg=COLORS['entry_bg'])
        self.entry_buy_price.grid(row=1, column=3, sticky='w', pady=5)

        # Row 2: Harga Jual & Stok
        tk.Label(form_inner, text="Harga Jual (Rp) :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=2, column=0, sticky='w', padx=(0, 8), pady=5)
        self.entry_sell_price = tk.Entry(form_inner, font=FONTS['body'], width=18,
                                         relief=tk.SOLID, bd=1, bg=COLORS['entry_bg'])
        self.entry_sell_price.grid(row=2, column=1, sticky='w', padx=(0, 25), pady=5)

        tk.Label(form_inner, text="Stok :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=2, column=2, sticky='w', padx=(0, 8), pady=5)
        self.entry_stock = tk.Entry(form_inner, font=FONTS['body'], width=18,
                                    relief=tk.SOLID, bd=1, bg=COLORS['entry_bg'])
        self.entry_stock.grid(row=2, column=3, sticky='w', pady=5)

        # Buttons Row
        btn_frame = tk.Frame(form_inner, bg=COLORS['card'])
        btn_frame.grid(row=3, column=0, columnspan=4, sticky='w', pady=(15, 5))

        self.btn_save = tk.Button(
            btn_frame, text="💾  Simpan", font=FONTS['body_bold'],
            bg=COLORS['accent'], fg='white', activebackground=COLORS['accent_hover'],
            activeforeground='white', relief=tk.FLAT, padx=15, pady=6, cursor='hand2',
            command=lambda: self.controller.save_product()
        )
        self.btn_save.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_update = tk.Button(
            btn_frame, text="✏️  Update", font=FONTS['body_bold'],
            bg=COLORS['info'], fg='white', activebackground='#2b6cb0',
            activeforeground='white', relief=tk.FLAT, padx=15, pady=6, cursor='hand2',
            command=lambda: self.controller.update_product()
        )
        self.btn_update.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_delete = tk.Button(
            btn_frame, text="🗑️  Hapus", font=FONTS['body_bold'],
            bg=COLORS['danger'], fg='white', activebackground=COLORS['danger_hover'],
            activeforeground='white', relief=tk.FLAT, padx=15, pady=6, cursor='hand2',
            command=lambda: self.controller.delete_product()
        )
        self.btn_delete.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_reset = tk.Button(
            btn_frame, text="🔄  Reset", font=FONTS['body_bold'],
            bg=COLORS['text_secondary'], fg='white', activebackground='#4a5568',
            activeforeground='white', relief=tk.FLAT, padx=15, pady=6, cursor='hand2',
            command=lambda: self.controller.reset_product_form()
        )
        self.btn_reset.pack(side=tk.LEFT)

        # ── Search Bar ──
        search_frame = tk.Frame(content, bg=COLORS['bg'])
        search_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(search_frame, text="🔍  Cari Produk :", font=FONTS['body_bold'],
                 bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=(0, 8))
        self.entry_search = tk.Entry(search_frame, font=FONTS['body'], width=30,
                                     relief=tk.SOLID, bd=1, bg=COLORS['entry_bg'])
        self.entry_search.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_search.bind('<KeyRelease>',
                               lambda e: self.controller.search_products())

        tk.Button(
            search_frame, text="Cari", font=FONTS['body'],
            bg=COLORS['primary'], fg='white', relief=tk.FLAT,
            padx=12, pady=3, cursor='hand2',
            command=lambda: self.controller.search_products()
        ).pack(side=tk.LEFT)

        # ── Treeview Produk ──
        tree_container = tk.Frame(content, bg=COLORS['card'], relief=tk.GROOVE, bd=1)
        tree_container.pack(fill=tk.BOTH, expand=True)

        cols = ('no', 'id', 'code', 'name', 'category',
                'buy_price', 'sell_price', 'stock')
        self.tree_products = ttk.Treeview(
            tree_container, columns=cols, show='headings', height=10
        )

        headings_config = {
            'no':         ('No',          45,  'center'),
            'id':         ('ID',          0,   'center'),
            'code':       ('Kode',        90,  'w'),
            'name':       ('Nama Produk', 200, 'w'),
            'category':   ('Kategori',    120, 'w'),
            'buy_price':  ('Harga Beli',  110, 'e'),
            'sell_price': ('Harga Jual',  110, 'e'),
            'stock':      ('Stok',        65,  'center'),
        }
        for col_id, (text, width, anchor) in headings_config.items():
            self.tree_products.heading(col_id, text=text)
            stretch = False if col_id == 'id' else True
            self.tree_products.column(col_id, width=width, anchor=anchor,
                                      stretch=stretch)

        # Hide ID column
        self.tree_products.column('id', width=0, stretch=False, minwidth=0)

        self._configure_tree_tags(self.tree_products)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL,
                                  command=self.tree_products.yview)
        self.tree_products.configure(yscrollcommand=scrollbar.set)

        self.tree_products.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Bind: klik baris treeview → muat data ke form
        self.tree_products.bind('<<TreeviewSelect>>',
                                lambda e: self.controller.select_product())

    # --- View Helper Methods (dipanggil Controller) ---

    def get_form_data(self):
        """Ambil semua data dari form input sebagai dictionary."""
        return {
            'code':       self.entry_code.get(),
            'name':       self.entry_name.get(),
            'category':   self.cmb_category.get(),
            'buy_price':  self.entry_buy_price.get(),
            'sell_price': self.entry_sell_price.get(),
            'stock':      self.entry_stock.get(),
        }

    def set_form_data(self, data):
        """Isi form dengan data produk. Kunci kode produk (PK) saat mode update."""
        self.clear_form()
        self.entry_code.insert(0, data.get('code', ''))
        self.entry_code.config(state='disabled')  # Kunci Primary Key
        self.entry_name.insert(0, data.get('name', ''))
        self.cmb_category.set(data.get('category', ''))
        self.entry_buy_price.insert(0, str(int(data.get('buy_price', 0))))
        self.entry_sell_price.insert(0, str(int(data.get('sell_price', 0))))
        self.entry_stock.insert(0, str(data.get('stock', 0)))

    def clear_form(self):
        """Bersihkan semua field form dan unlock kode produk."""
        self.entry_code.config(state='normal')
        self.entry_code.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.cmb_category.set('')
        self.entry_buy_price.delete(0, tk.END)
        self.entry_sell_price.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        self.selected_product_id = None

    def get_selected_item(self):
        """Ambil values dari item yang dipilih di Treeview."""
        selected = self.tree_products.selection()
        if selected:
            return self.tree_products.item(selected[0], 'values')
        return None

    def populate_treeview(self, products):
        """Isi Treeview dengan list data produk (auto-refresh)."""
        for item in self.tree_products.get_children():
            self.tree_products.delete(item)

        for i, p in enumerate(products, 1):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree_products.insert('', 'end', values=(
                i,
                p['id'],
                p['code'],
                p['name'],
                p['category'],
                format_rupiah(p['buy_price']),
                format_rupiah(p['sell_price']),
                p['stock']
            ), tags=(tag,))

    def on_page_show(self):
        """Refresh data produk saat halaman ditampilkan."""
        self.controller.refresh_products()


# ============================================================
# CLASS: CashierPage (Mewarisi BasePage)
# ============================================================

class CashierPage(BasePage):
    """
    Halaman Kasir POS — Interface point of sale untuk transaksi.
    
    INHERITANCE  : Mewarisi BasePage.
    POLYMORPHISM : Override setup_ui() dan on_page_show().
    """

    def setup_ui(self):
        """Bangun UI kasir: pencarian produk, keranjang, dan pembayaran."""
        self._create_title_bar("💰", "KASIR POS")

        # Data keranjang belanja (state sementara UI)
        self.cart_items = []
        self.current_total = 0

        content = tk.Frame(self, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        # ════════════════════════════════════════════
        # LEFT PANEL: Cari & Pilih Produk
        # ════════════════════════════════════════════
        left_panel = tk.LabelFrame(
            content, text="  🔍 Cari & Pilih Produk  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Search bar
        search_frame = tk.Frame(left_panel, bg=COLORS['card'])
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.entry_search_product = tk.Entry(
            search_frame, font=FONTS['body'], relief=tk.SOLID, bd=1,
            bg=COLORS['entry_bg']
        )
        self.entry_search_product.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_search_product.insert(0, "Ketik kode/nama produk...")
        self.entry_search_product.config(fg=COLORS['text_light'])
        self.entry_search_product.bind('<FocusIn>', self._on_search_focus_in)
        self.entry_search_product.bind('<FocusOut>', self._on_search_focus_out)
        self.entry_search_product.bind('<KeyRelease>',
            lambda e: self.controller.search_cashier_products())

        tk.Button(
            search_frame, text="🔍", font=FONTS['body'],
            bg=COLORS['primary'], fg='white', relief=tk.FLAT,
            padx=10, cursor='hand2',
            command=lambda: self.controller.search_cashier_products()
        ).pack(side=tk.RIGHT)

        # Product Treeview
        tree_frame = tk.Frame(left_panel, bg=COLORS['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols_prod = ('id', 'code', 'name', 'price', 'stock')
        self.tree_cashier_products = ttk.Treeview(
            tree_frame, columns=cols_prod, show='headings', height=10
        )
        self.tree_cashier_products.heading('id', text='ID')
        self.tree_cashier_products.heading('code', text='Kode')
        self.tree_cashier_products.heading('name', text='Nama Produk')
        self.tree_cashier_products.heading('price', text='Harga Jual')
        self.tree_cashier_products.heading('stock', text='Stok')

        self.tree_cashier_products.column('id', width=0, stretch=False, minwidth=0)
        self.tree_cashier_products.column('code', width=70, anchor='w')
        self.tree_cashier_products.column('name', width=160, anchor='w')
        self.tree_cashier_products.column('price', width=100, anchor='e')
        self.tree_cashier_products.column('stock', width=50, anchor='center')

        self._configure_tree_tags(self.tree_cashier_products)

        prod_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                    command=self.tree_cashier_products.yview)
        self.tree_cashier_products.configure(yscrollcommand=prod_scroll.set)
        self.tree_cashier_products.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prod_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Quantity + Add to cart button
        action_frame = tk.Frame(left_panel, bg=COLORS['card'])
        action_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        tk.Label(action_frame, text="Jumlah :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).pack(side=tk.LEFT, padx=(0, 5))
        self.entry_qty = tk.Entry(action_frame, font=FONTS['body'], width=6,
                                  relief=tk.SOLID, bd=1, justify='center',
                                  bg=COLORS['entry_bg'])
        self.entry_qty.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_qty.insert(0, "1")

        tk.Button(
            action_frame, text="➕  Tambah ke Keranjang", font=FONTS['body_bold'],
            bg=COLORS['accent'], fg='white', activebackground=COLORS['accent_hover'],
            activeforeground='white', relief=tk.FLAT, padx=12, pady=5, cursor='hand2',
            command=lambda: self.controller.add_to_cart()
        ).pack(side=tk.LEFT)

        # ════════════════════════════════════════════
        # RIGHT PANEL: Keranjang + Pembayaran
        # ════════════════════════════════════════════
        right_panel = tk.Frame(content, bg=COLORS['bg'])
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=0)
        right_panel.columnconfigure(0, weight=1)

        # ── Cart Section ──
        cart_frame = tk.LabelFrame(
            right_panel, text="  🛒 Keranjang Belanja  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        cart_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        cart_tree_frame = tk.Frame(cart_frame, bg=COLORS['card'])
        cart_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        cols_cart = ('no', 'product_id', 'name', 'price', 'qty', 'subtotal')
        self.tree_cart = ttk.Treeview(
            cart_tree_frame, columns=cols_cart, show='headings', height=8
        )
        self.tree_cart.heading('no', text='No')
        self.tree_cart.heading('product_id', text='PID')
        self.tree_cart.heading('name', text='Nama Produk')
        self.tree_cart.heading('price', text='Harga')
        self.tree_cart.heading('qty', text='Qty')
        self.tree_cart.heading('subtotal', text='Subtotal')

        self.tree_cart.column('no', width=35, anchor='center')
        self.tree_cart.column('product_id', width=0, stretch=False, minwidth=0)
        self.tree_cart.column('name', width=140, anchor='w')
        self.tree_cart.column('price', width=90, anchor='e')
        self.tree_cart.column('qty', width=40, anchor='center')
        self.tree_cart.column('subtotal', width=100, anchor='e')

        self._configure_tree_tags(self.tree_cart)

        cart_scroll = ttk.Scrollbar(cart_tree_frame, orient=tk.VERTICAL,
                                    command=self.tree_cart.yview)
        self.tree_cart.configure(yscrollcommand=cart_scroll.set)
        self.tree_cart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Remove button
        cart_btn_frame = tk.Frame(cart_frame, bg=COLORS['card'])
        cart_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(
            cart_btn_frame, text="🗑️  Hapus Item Terpilih", font=FONTS['body'],
            bg=COLORS['danger'], fg='white', activebackground=COLORS['danger_hover'],
            activeforeground='white', relief=tk.FLAT, padx=10, pady=4, cursor='hand2',
            command=lambda: self.controller.remove_from_cart()
        ).pack(side=tk.LEFT)

        # ── Payment Section ──
        pay_frame = tk.LabelFrame(
            right_panel, text="  💳 Pembayaran  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        pay_frame.grid(row=1, column=0, sticky="ew")

        pay_inner = tk.Frame(pay_frame, bg=COLORS['card'])
        pay_inner.pack(fill=tk.X, padx=15, pady=15)
        pay_inner.columnconfigure(1, weight=1)

        # Invoice number
        tk.Label(pay_inner, text="No. Invoice :", font=FONTS['body'],
                 bg=COLORS['card'], fg=COLORS['text_secondary']).grid(
            row=0, column=0, sticky='w', pady=3)
        self.lbl_invoice = tk.Label(pay_inner, text="-",
                                    font=FONTS['body_bold'],
                                    bg=COLORS['card'], fg=COLORS['text'])
        self.lbl_invoice.grid(row=0, column=1, sticky='e', pady=3)

        # Separator
        sep1 = tk.Frame(pay_inner, bg=COLORS['border'], height=1)
        sep1.grid(row=1, column=0, columnspan=2, sticky='ew', pady=8)

        # Total
        tk.Label(pay_inner, text="TOTAL :", font=FONTS['price_big'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=2, column=0, sticky='w', pady=3)
        self.lbl_total = tk.Label(pay_inner, text="Rp 0",
                                  font=FONTS['price_big'],
                                  bg=COLORS['card'], fg=COLORS['danger'])
        self.lbl_total.grid(row=2, column=1, sticky='e', pady=3)

        # Payment input
        tk.Label(pay_inner, text="Bayar (Rp) :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=3, column=0, sticky='w', pady=5)
        self.entry_payment = tk.Entry(pay_inner, font=FONTS['heading'], width=15,
                                      relief=tk.SOLID, bd=1, justify='right',
                                      bg=COLORS['entry_bg'])
        self.entry_payment.grid(row=3, column=1, sticky='e', pady=5)
        self.entry_payment.bind('<KeyRelease>',
                                lambda e: self.controller.calculate_change())

        # Change
        tk.Label(pay_inner, text="Kembalian :", font=FONTS['body_bold'],
                 bg=COLORS['card'], fg=COLORS['text']).grid(
            row=4, column=0, sticky='w', pady=3)
        self.lbl_change = tk.Label(pay_inner, text="Rp 0",
                                   font=FONTS['price_big'],
                                   bg=COLORS['card'], fg=COLORS['accent'])
        self.lbl_change.grid(row=4, column=1, sticky='e', pady=3)

        # Separator
        sep2 = tk.Frame(pay_inner, bg=COLORS['border'], height=1)
        sep2.grid(row=5, column=0, columnspan=2, sticky='ew', pady=8)

        # Action buttons
        btn_pay_frame = tk.Frame(pay_inner, bg=COLORS['card'])
        btn_pay_frame.grid(row=6, column=0, columnspan=2, sticky='ew')

        self.btn_process = tk.Button(
            btn_pay_frame, text="💳  Proses Bayar", font=FONTS['body_bold'],
            bg=COLORS['accent'], fg='white', activebackground=COLORS['accent_hover'],
            activeforeground='white', relief=tk.FLAT, padx=20, pady=8, cursor='hand2',
            command=lambda: self.controller.process_payment()
        )
        self.btn_process.pack(side=tk.LEFT, padx=(0, 8), expand=True, fill=tk.X)

        self.btn_cancel = tk.Button(
            btn_pay_frame, text="❌  Batal", font=FONTS['body_bold'],
            bg=COLORS['danger'], fg='white', activebackground=COLORS['danger_hover'],
            activeforeground='white', relief=tk.FLAT, padx=20, pady=8, cursor='hand2',
            command=lambda: self.controller.clear_cashier()
        )
        self.btn_cancel.pack(side=tk.LEFT, expand=True, fill=tk.X)

    # --- Search Placeholder Handlers ---

    def _on_search_focus_in(self, event):
        """Hapus placeholder saat search field mendapat fokus."""
        if self.entry_search_product.get() == "Ketik kode/nama produk...":
            self.entry_search_product.delete(0, tk.END)
            self.entry_search_product.config(fg=COLORS['text'])

    def _on_search_focus_out(self, event):
        """Tampilkan placeholder saat search field kehilangan fokus."""
        if not self.entry_search_product.get().strip():
            self.entry_search_product.insert(0, "Ketik kode/nama produk...")
            self.entry_search_product.config(fg=COLORS['text_light'])

    # --- View Helper Methods ---

    def get_search_keyword(self):
        """Ambil keyword pencarian (abaikan placeholder)."""
        text = self.entry_search_product.get().strip()
        if text == "Ketik kode/nama produk...":
            return ""
        return text

    def populate_product_list(self, products):
        """Isi treeview daftar produk kasir."""
        for item in self.tree_cashier_products.get_children():
            self.tree_cashier_products.delete(item)

        for i, p in enumerate(products, 1):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree_cashier_products.insert('', 'end', values=(
                p['id'], p['code'], p['name'],
                format_rupiah(p['sell_price']), p['stock']
            ), tags=(tag,))

    def on_page_show(self):
        """Refresh daftar produk dan invoice saat halaman ditampilkan."""
        self.controller.refresh_cashier()


# ============================================================
# CLASS: TransactionPage (Mewarisi BasePage)
# ============================================================

class TransactionPage(BasePage):
    """
    Halaman Riwayat Transaksi — Menampilkan history dan detail transaksi.
    
    INHERITANCE  : Mewarisi BasePage.
    POLYMORPHISM : Override setup_ui() dan on_page_show().
    """

    def setup_ui(self):
        """Bangun UI riwayat transaksi: daftar + detail item."""
        self._create_title_bar("📋", "RIWAYAT TRANSAKSI")

        content = tk.Frame(self, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        content.rowconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)
        content.columnconfigure(0, weight=1)

        # ── Search & Action Bar ──
        action_frame = tk.Frame(content, bg=COLORS['bg'])
        action_frame.grid(row=0, column=0, sticky='ew', pady=(0, 8))

        tk.Label(action_frame, text="🔍  Cari Invoice :", font=FONTS['body_bold'],
                 bg=COLORS['bg'], fg=COLORS['text']).pack(side=tk.LEFT, padx=(0, 8))
        self.entry_search_transaction = tk.Entry(
            action_frame, font=FONTS['body'], width=25,
            relief=tk.SOLID, bd=1, bg=COLORS['entry_bg']
        )
        self.entry_search_transaction.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_search_transaction.bind('<KeyRelease>',
            lambda e: self.controller.search_transactions())

        tk.Button(
            action_frame, text="Cari", font=FONTS['body'],
            bg=COLORS['primary'], fg='white', relief=tk.FLAT,
            padx=12, pady=3, cursor='hand2',
            command=lambda: self.controller.search_transactions()
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Button(
            action_frame, text="🗑️  Hapus Transaksi", font=FONTS['body_bold'],
            bg=COLORS['danger'], fg='white', activebackground=COLORS['danger_hover'],
            activeforeground='white', relief=tk.FLAT, padx=12, pady=4, cursor='hand2',
            command=lambda: self.controller.delete_transaction()
        ).pack(side=tk.RIGHT)

        # ── Transaction List ──
        trans_frame = tk.LabelFrame(
            content, text="  📋 Daftar Transaksi  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        trans_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        trans_tree_frame = tk.Frame(trans_frame, bg=COLORS['card'])
        trans_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols_trans = ('no', 'id', 'invoice', 'tanggal', 'total', 'bayar', 'kembalian')
        self.tree_transactions = ttk.Treeview(
            trans_tree_frame, columns=cols_trans, show='headings', height=8
        )
        self.tree_transactions.heading('no', text='No')
        self.tree_transactions.heading('id', text='ID')
        self.tree_transactions.heading('invoice', text='No. Invoice')
        self.tree_transactions.heading('tanggal', text='Tanggal')
        self.tree_transactions.heading('total', text='Total')
        self.tree_transactions.heading('bayar', text='Bayar')
        self.tree_transactions.heading('kembalian', text='Kembalian')

        self.tree_transactions.column('no', width=40, anchor='center')
        self.tree_transactions.column('id', width=0, stretch=False, minwidth=0)
        self.tree_transactions.column('invoice', width=170, anchor='w')
        self.tree_transactions.column('tanggal', width=150, anchor='center')
        self.tree_transactions.column('total', width=120, anchor='e')
        self.tree_transactions.column('bayar', width=120, anchor='e')
        self.tree_transactions.column('kembalian', width=120, anchor='e')

        self._configure_tree_tags(self.tree_transactions)

        trans_scroll = ttk.Scrollbar(trans_tree_frame, orient=tk.VERTICAL,
                                     command=self.tree_transactions.yview)
        self.tree_transactions.configure(yscrollcommand=trans_scroll.set)
        self.tree_transactions.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind: klik transaksi → tampilkan detail
        self.tree_transactions.bind('<<TreeviewSelect>>',
            lambda e: self.controller.view_transaction_detail())

        # ── Detail Transaksi ──
        detail_frame = tk.LabelFrame(
            content, text="  📝 Detail Item Transaksi  ",
            font=FONTS['heading'], bg=COLORS['card'],
            fg=COLORS['text'], relief=tk.GROOVE, bd=1
        )
        detail_frame.grid(row=2, column=0, sticky="nsew")

        detail_tree_frame = tk.Frame(detail_frame, bg=COLORS['card'])
        detail_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols_detail = ('no', 'product_name', 'price', 'qty', 'subtotal')
        self.tree_detail = ttk.Treeview(
            detail_tree_frame, columns=cols_detail, show='headings', height=6
        )
        self.tree_detail.heading('no', text='No')
        self.tree_detail.heading('product_name', text='Nama Produk')
        self.tree_detail.heading('price', text='Harga Satuan')
        self.tree_detail.heading('qty', text='Qty')
        self.tree_detail.heading('subtotal', text='Subtotal')

        self.tree_detail.column('no', width=40, anchor='center')
        self.tree_detail.column('product_name', width=250, anchor='w')
        self.tree_detail.column('price', width=130, anchor='e')
        self.tree_detail.column('qty', width=60, anchor='center')
        self.tree_detail.column('subtotal', width=130, anchor='e')

        self._configure_tree_tags(self.tree_detail)

        detail_scroll = ttk.Scrollbar(detail_tree_frame, orient=tk.VERTICAL,
                                      command=self.tree_detail.yview)
        self.tree_detail.configure(yscrollcommand=detail_scroll.set)
        self.tree_detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # --- View Helper Methods ---

    def populate_transactions(self, transactions):
        """Isi Treeview daftar transaksi."""
        for item in self.tree_transactions.get_children():
            self.tree_transactions.delete(item)

        for i, t in enumerate(transactions, 1):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree_transactions.insert('', 'end', values=(
                i,
                t['id'],
                t['invoice_no'],
                t['date'],
                format_rupiah(t['total']),
                format_rupiah(t['payment']),
                format_rupiah(t['change_amount'])
            ), tags=(tag,))

    def on_page_show(self):
        """Refresh daftar transaksi saat halaman ditampilkan."""
        self.controller.refresh_transactions()
