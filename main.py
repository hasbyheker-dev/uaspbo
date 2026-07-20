"""
main.py - Lapisan Controller / App (Controller Layer)
======================================================
Modul ini bertindak sebagai pengatur lalu lintas data (Router & Bridge)
antara Lapisan Data (model.py) dan Lapisan Antarmuka (view.py).

Kriteria yang dipenuhi:
- STRICT MVC: Menghubungkan View dan Model tanpa saling import langsung
  di antara keduanya. Semua logika bisnis (CRUD, perhitungan) dipicu dari sini.
- FRAME SWITCHING: Semua halaman dimuat di dalam satu jendela utama (tk.Tk)
  menggunakan .tkraise(), tanpa popup Toplevel.
- EXCEPTION HANDLING: Semua proses krusial dibungkus try-except
  dan memberikan feedback visual via tkinter.messagebox.
"""

import tkinter as tk
from tkinter import messagebox

# Import layer model dan view
from model import ProductModel, TransactionModel, DashboardModel
from view import DashboardPage, ProductPage, CashierPage, TransactionPage, format_rupiah


class App(tk.Tk):
    """
    Class utama aplikasi (Controller).
    Menyiapkan jendela utama, menu bar, dan mengelola navigasi antar frame.
    """

    def __init__(self):
        super().__init__()

        self.title("POS Kasir Pro - Point of Sale & Stok Gudang")
        self.geometry("1100x700")
        self.minsize(1000, 600)
        self.configure(bg="#edf2f7")

        # Inisialisasi Models
        self.product_model = ProductModel()
        self.transaction_model = TransactionModel()
        self.dashboard_model = DashboardModel()

        # Konfigurasi container untuk Frame Switching
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary untuk menyimpan instance halaman
        self.frames = {}

        # Inisialisasi UI
        self._create_menu_bar()
        self._init_frames()

        # Tampilkan halaman awal
        self.show_frame(DashboardPage)

    def _create_menu_bar(self):
        """Membangun Menu Bar di bagian atas aplikasi."""
        menu_bar = tk.Menu(self)

        # Menu File
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Keluar", command=self.quit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Menu Navigasi
        nav_menu = tk.Menu(menu_bar, tearoff=0)
        nav_menu.add_command(label="🏠 Dashboard",
                             command=lambda: self.show_frame(DashboardPage))
        nav_menu.add_command(label="📦 Manajemen Produk",
                             command=lambda: self.show_frame(ProductPage))
        nav_menu.add_command(label="💰 Kasir POS",
                             command=lambda: self.show_frame(CashierPage))
        nav_menu.add_command(label="📋 Riwayat Transaksi",
                             command=lambda: self.show_frame(TransactionPage))
        menu_bar.add_cascade(label="Navigasi", menu=nav_menu)

        # Menu Bantuan
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Info Aplikasi", command=self.show_info)
        menu_bar.add_cascade(label="Bantuan", menu=help_menu)

        self.config(menu=menu_bar)

    def _init_frames(self):
        """Inisialisasi semua halaman dan tumpuk di container."""
        # Menumpuk frame di koordinat grid yang sama (row=0, column=0)
        for F in (DashboardPage, ProductPage, CashierPage, TransactionPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_class):
        """Menampilkan halaman tertentu (Frame Switching dengan tkraise)."""
        frame = self.frames[page_class]
        frame.tkraise()       # Bawa frame ke paling atas
        frame.on_page_show()  # Trigger refresh data (Polymorphism)

    def quit_app(self):
        """Konfirmasi sebelum keluar aplikasi."""
        if messagebox.askyesno("Konfirmasi Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            self.quit()

    def show_info(self):
        """Tampilkan informasi aplikasi."""
        info_text = (
            "POS Kasir Pro v1.0\n\n"
            "Aplikasi Point of Sale & Manajemen Stok Gudang.\n"
            "Dibuat untuk memenuhi Tugas Akhir Mata Kuliah PBO.\n\n"
            "Fitur:\n"
            "- Arsitektur Strict MVC\n"
            "- OOP (Encapsulation, Inheritance, Polymorphism)\n"
            "- Database SQLite Terintegrasi\n"
            "- Navigasi Single Page Application"
        )
        messagebox.showinfo("Info Aplikasi", info_text)


    # ============================================================
    # CONTROLLER METHODS: Dashboard
    # ============================================================

    def refresh_dashboard(self):
        """Ambil data dari model dan update view dashboard."""
        try:
            page = self.frames[DashboardPage]
            
            # Update statistik atas
            total_prod = self.dashboard_model.get_total_products()
            total_stock = self.dashboard_model.get_total_stock()
            today_trans = self.dashboard_model.get_today_transactions()
            today_rev = self.dashboard_model.get_today_revenue()
            
            page.lbl_total_products.config(text=str(total_prod))
            page.lbl_total_stock.config(text=str(total_stock))
            page.lbl_today_transactions.config(text=str(today_trans))
            page.lbl_today_revenue.config(text=format_rupiah(today_rev))
            
            # Update ringkasan
            tot_rev = self.dashboard_model.get_total_revenue()
            tot_trans = self.dashboard_model.get_total_transactions()
            out_of_stock = self.dashboard_model.get_out_of_stock_count()
            
            page.lbl_total_revenue.config(text=format_rupiah(tot_rev))
            page.lbl_total_transactions.config(text=f"{tot_trans} transaksi")
            page.lbl_out_of_stock.config(text=f"{out_of_stock} produk")
            
            # Update tabel riwayat terbaru
            recent = self.dashboard_model.get_recent_transactions(5)
            
            # Bersihkan treeview
            for item in page.tree_recent.get_children():
                page.tree_recent.delete(item)
                
            # Isi ulang
            for i, t in enumerate(recent, 1):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                page.tree_recent.insert('', 'end', values=(
                    i, t['invoice_no'], t['date'][:16], format_rupiah(t['total'])
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error Dashboard", f"Gagal memuat data dashboard:\n{str(e)}")


    # ============================================================
    # CONTROLLER METHODS: Manajemen Produk
    # ============================================================

    def refresh_products(self):
        """Refresh daftar produk dan kategori di halaman Manajemen Produk."""
        try:
            page = self.frames[ProductPage]
            # Reload treeview
            products = self.product_model.read_all()
            page.populate_treeview(products)
            
            # Reload kategori unik ke combobox
            categories = self.product_model.get_categories()
            # Gabungkan dengan default, hilangkan duplikat
            from view import DEFAULT_CATEGORIES
            all_cat = list(dict.fromkeys(DEFAULT_CATEGORIES + categories))
            page.cmb_category.config(values=all_cat)
            
            page.clear_form()
        except Exception as e:
            messagebox.showerror("Error Produk", f"Gagal memuat data produk:\n{str(e)}")

    def search_products(self):
        """Cari produk berdasarkan input pengguna."""
        try:
            page = self.frames[ProductPage]
            keyword = page.entry_search.get().strip()
            
            if keyword:
                products = self.product_model.search(keyword)
            else:
                products = self.product_model.read_all()
                
            page.populate_treeview(products)
        except Exception as e:
            pass # Abaikan error pencarian real-time

    def save_product(self):
        """Ambil data dari form View, kirim ke Model untuk disimpan."""
        page = self.frames[ProductPage]
        
        # Validasi UI-state (apakah sedang update?)
        if page.selected_product_id:
            messagebox.showwarning("Peringatan", "Anda sedang dalam mode Edit.\nGunakan tombol Update, atau Reset form terlebih dahulu.")
            return

        data = page.get_form_data()
        
        # Panggil operasi simpan (dibungkus try-except di model, kita terima return value)
        success, message = self.product_model.create(data)
        
        if success:
            messagebox.showinfo("Sukses", message)
            self.refresh_products()
        else:
            # message berupa list of errors
            err_text = "\n".join(message)
            messagebox.showerror("Gagal Menyimpan", f"Perbaiki kesalahan berikut:\n{err_text}")

    def select_product(self):
        """Triggered saat user klik baris di Treeview Produk."""
        page = self.frames[ProductPage]
        selected_values = page.get_selected_item()
        
        if not selected_values:
            return
            
        try:
            # values[1] adalah ID produk (kolom hidden)
            product_id = selected_values[1]
            # Ambil data lengkap dari database
            product = self.product_model.read_by_id(product_id)
            
            if product:
                # Isi ke form dan set state ID
                page.set_form_data(product)
                page.selected_product_id = product_id
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat detail produk:\n{str(e)}")

    def update_product(self):
        """Proses update produk yang sedang dipilih."""
        page = self.frames[ProductPage]
        product_id = page.selected_product_id
        
        if not product_id:
            messagebox.showwarning("Peringatan", "Pilih produk dari tabel terlebih dahulu untuk di-update.")
            return
            
        data = page.get_form_data()
        success, message = self.product_model.update(product_id, data)
        
        if success:
            messagebox.showinfo("Sukses", message)
            self.refresh_products()
        else:
            err_text = "\n".join(message)
            messagebox.showerror("Gagal Update", f"Perbaiki kesalahan berikut:\n{err_text}")

    def delete_product(self):
        """Proses hapus produk yang sedang dipilih."""
        page = self.frames[ProductPage]
        product_id = page.selected_product_id
        
        if not product_id:
            messagebox.showwarning("Peringatan", "Pilih produk dari tabel terlebih dahulu untuk dihapus.")
            return
            
        product_code = page.entry_code.get()
        product_name = page.entry_name.get()
        
        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus produk:\n[{product_code}] {product_name}?"):
            success, message = self.product_model.delete(product_id)
            if success:
                messagebox.showinfo("Sukses", message)
                self.refresh_products()
            else:
                messagebox.showerror("Gagal", message)

    def reset_product_form(self):
        """Bersihkan form input produk."""
        self.frames[ProductPage].clear_form()


    # ============================================================
    # CONTROLLER METHODS: Kasir POS
    # ============================================================

    def refresh_cashier(self):
        """Refresh halaman kasir (daftar produk tersedia)."""
        try:
            page = self.frames[CashierPage]
            # Hanya tampilkan produk dengan stok > 0
            products = self.product_model.get_available_products()
            page.populate_product_list(products)
            
            # Generate invoice baru jika keranjang kosong
            if not page.cart_items:
                self.generate_new_invoice()
                
            self.update_cart_display()
        except Exception as e:
            messagebox.showerror("Error Kasir", f"Gagal memuat daftar produk:\n{str(e)}")

    def search_cashier_products(self):
        """Cari produk untuk kasir (hanya yang stok > 0)."""
        try:
            page = self.frames[CashierPage]
            keyword = page.get_search_keyword()
            
            if keyword:
                products = self.product_model.search_available(keyword)
            else:
                products = self.product_model.get_available_products()
                
            page.populate_product_list(products)
        except Exception as e:
            pass

    def generate_new_invoice(self):
        """Buat nomor invoice baru dan tampilkan di UI."""
        invoice_no = self.transaction_model.generate_invoice()
        self.frames[CashierPage].lbl_invoice.config(text=invoice_no)

    def add_to_cart(self):
        """Tambahkan produk terpilih ke keranjang belanja."""
        page = self.frames[CashierPage]
        
        # Ambil produk terpilih
        selected = page.tree_cashier_products.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih produk dari daftar terlebih dahulu.")
            return
            
        try:
            qty = int(page.entry_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Jumlah (Qty) harus berupa angka lebih besar dari 0.")
            return
            
        # Parse data dari treeview kasir ('id', 'code', 'name', 'price', 'stock')
        item_values = page.tree_cashier_products.item(selected[0], 'values')
        product_id = int(item_values[0])
        product_name = item_values[2]
        
        # Ambil harga numerik (hilangkan 'Rp ' dan titik)
        price_str = str(item_values[3]).replace('Rp ', '').replace('.', '')
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error", "Format harga tidak valid.")
            return
            
        stock = int(item_values[4])
        
        # Cek apakah qty melebihi stok yang ada
        # (Juga perhitungkan jika barang sudah ada di keranjang)
        existing_qty = sum(item['qty'] for item in page.cart_items if item['product_id'] == product_id)
        
        if (existing_qty + qty) > stock:
            messagebox.showwarning("Stok Kurang", f"Stok tidak mencukupi.\nSisa stok: {stock}\nSudah di keranjang: {existing_qty}")
            return
            
        # Cek apakah sudah ada di keranjang, jika ya tambah qty nya
        found = False
        for item in page.cart_items:
            if item['product_id'] == product_id:
                item['qty'] += qty
                item['subtotal'] = item['qty'] * item['price']
                found = True
                break
                
        if not found:
            # Tambahkan item baru
            page.cart_items.append({
                'product_id': product_id,
                'name': product_name,
                'price': price,
                'qty': qty,
                'subtotal': price * qty
            })
            
        # Reset input qty ke 1
        page.entry_qty.delete(0, tk.END)
        page.entry_qty.insert(0, "1")
        
        self.update_cart_display()

    def remove_from_cart(self):
        """Hapus item terpilih dari keranjang."""
        page = self.frames[CashierPage]
        selected = page.tree_cart.selection()
        
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih item di keranjang yang ingin dihapus.")
            return
            
        # Ambil indeks (dari kolom 'no', dikurang 1)
        try:
            item_no = int(page.tree_cart.item(selected[0], 'values')[0])
            index = item_no - 1
            
            # Konfirmasi
            item_name = page.cart_items[index]['name']
            if messagebox.askyesno("Hapus Item", f"Hapus '{item_name}' dari keranjang?"):
                page.cart_items.pop(index)
                self.update_cart_display()
                
        except (IndexError, ValueError):
            pass

    def update_cart_display(self):
        """Perbarui UI keranjang dan total harga."""
        page = self.frames[CashierPage]
        
        # Bersihkan treeview
        for item in page.tree_cart.get_children():
            page.tree_cart.delete(item)
            
        page.current_total = 0
        
        # Isi ulang dengan data terbaru
        for i, item in enumerate(page.cart_items, 1):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            page.tree_cart.insert('', 'end', values=(
                i,
                item['product_id'],
                item['name'],
                format_rupiah(item['price']),
                item['qty'],
                format_rupiah(item['subtotal'])
            ), tags=(tag,))
            
            page.current_total += item['subtotal']
            
        # Update label total
        page.lbl_total.config(text=format_rupiah(page.current_total))
        
        # Hitung ulang kembalian jika ada input bayar
        self.calculate_change()

    def calculate_change(self):
        """Hitung dan tampilkan uang kembalian secara real-time."""
        page = self.frames[CashierPage]
        
        if page.current_total == 0:
            page.lbl_change.config(text="Rp 0")
            return
            
        payment_str = page.entry_payment.get().strip()
        if not payment_str:
            page.lbl_change.config(text="Rp 0")
            return
            
        try:
            payment = float(payment_str)
            change = payment - page.current_total
            
            if change < 0:
                page.lbl_change.config(text="Kurang " + format_rupiah(abs(change)), fg=page.COLORS['danger'])
            else:
                page.lbl_change.config(text=format_rupiah(change), fg=page.COLORS['accent'])
        except ValueError:
            page.lbl_change.config(text="Input tidak valid", fg=page.COLORS['danger'])

    def process_payment(self):
        """Proses transaksi pembayaran ke database."""
        page = self.frames[CashierPage]
        
        if not page.cart_items:
            messagebox.showwarning("Peringatan", "Keranjang belanja kosong.")
            return
            
        try:
            payment_str = page.entry_payment.get().strip()
            if not payment_str:
                raise ValueError("Masukkan jumlah pembayaran.")
                
            payment = float(payment_str)
            if payment < page.current_total:
                raise ValueError("Uang pembayaran kurang dari total belanja.")
                
        except ValueError as e:
            messagebox.showerror("Pembayaran Gagal", str(e))
            return
            
        change_amount = payment - page.current_total
        invoice_no = page.lbl_invoice.cget("text")
        
        # Konfirmasi akhir
        msg = f"Total Belanja:\t{format_rupiah(page.current_total)}\nPembayaran:\t{format_rupiah(payment)}\nKembalian:\t{format_rupiah(change_amount)}\n\nLanjutkan transaksi?"
        if not messagebox.askyesno("Konfirmasi Pembayaran", msg):
            return
            
        # Eksekusi simpan ke database (Model)
        success, message = self.transaction_model.create(
            invoice_no=invoice_no,
            total=page.current_total,
            payment=payment,
            change_amount=change_amount,
            items=page.cart_items
        )
        
        if success:
            messagebox.showinfo("Transaksi Berhasil", message)
            self.clear_cashier()
            # Refresh list produk kasir karena stok pasti berkurang
            self.refresh_cashier()
        else:
            messagebox.showerror("Transaksi Gagal", message)

    def clear_cashier(self):
        """Bersihkan keranjang dan form pembayaran."""
        page = self.frames[CashierPage]
        page.cart_items.clear()
        page.entry_payment.delete(0, tk.END)
        self.generate_new_invoice()
        self.update_cart_display()


    # ============================================================
    # CONTROLLER METHODS: Riwayat Transaksi
    # ============================================================

    def refresh_transactions(self):
        """Ambil data riwayat transaksi dan tampilkan di Treeview."""
        try:
            page = self.frames[TransactionPage]
            transactions = self.transaction_model.read_all()
            page.populate_transactions(transactions)
            
            # Bersihkan detail
            for item in page.tree_detail.get_children():
                page.tree_detail.delete(item)
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat riwayat transaksi:\n{str(e)}")

    def search_transactions(self):
        """Cari transaksi berdasarkan invoice."""
        try:
            page = self.frames[TransactionPage]
            keyword = page.entry_search_transaction.get().strip()
            
            if keyword:
                transactions = self.transaction_model.search_by_invoice(keyword)
            else:
                transactions = self.transaction_model.read_all()
                
            page.populate_transactions(transactions)
            
            # Bersihkan detail saat hasil pencarian berubah
            for item in page.tree_detail.get_children():
                page.tree_detail.delete(item)
                
        except Exception as e:
            pass

    def view_transaction_detail(self):
        """Tampilkan detail item dari transaksi yang dipilih."""
        page = self.frames[TransactionPage]
        selected = page.tree_transactions.selection()
        
        if not selected:
            return
            
        try:
            # Ambil ID transaksi dari kolom hidden
            trans_id = int(page.tree_transactions.item(selected[0], 'values')[1])
            items = self.transaction_model.read_items(trans_id)
            
            # Bersihkan treeview detail
            for item in page.tree_detail.get_children():
                page.tree_detail.delete(item)
                
            # Isi ulang
            for i, item in enumerate(items, 1):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                page.tree_detail.insert('', 'end', values=(
                    i,
                    item['product_name'],
                    format_rupiah(item['price']),
                    item['quantity'],
                    format_rupiah(item['subtotal'])
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error Detail", f"Gagal memuat detail transaksi:\n{str(e)}")

    def delete_transaction(self):
        """Hapus riwayat transaksi beserta detailnya, kembalikan stok."""
        page = self.frames[TransactionPage]
        selected = page.tree_transactions.selection()
        
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin dihapus.")
            return
            
        values = page.tree_transactions.item(selected[0], 'values')
        trans_id = int(values[1])
        invoice_no = values[2]
        
        msg = f"Anda yakin ingin menghapus transaksi {invoice_no}?\n\nPerhatian: Stok produk dari transaksi ini akan dikembalikan (ditambah)."
        if messagebox.askyesno("Konfirmasi Hapus Transaksi", msg, icon='warning'):
            success, message = self.transaction_model.delete(trans_id)
            if success:
                messagebox.showinfo("Sukses", message)
                self.refresh_transactions()
            else:
                messagebox.showerror("Gagal", message)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = App()
    app.mainloop()
