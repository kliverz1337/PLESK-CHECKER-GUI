import os
import queue
import customtkinter
import tkinter.filedialog
import datetime
import threading # Import threading module
from CTkMessagebox import CTkMessagebox

from config import APP_TITLE, APP_GEOMETRY, APP_MINSIZE, APPEARANCE_MODE, COLOR_THEME
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import center_window, create_treeview, calculate_eta, calculate_duration, open_web_login
from handlers.file_handler import read_lines_from_file
from core.checker_logic import PleskCheckerLogic

class PleskCheckerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(*APP_MINSIZE)
        self.resizable(True, True)
        self.update_idletasks()
        center_window(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        customtkinter.set_appearance_mode(APPEARANCE_MODE)
        customtkinter.set_default_color_theme(COLOR_THEME)

        self.driver = None # Initialize driver to None

        # Initialize the queue for UI updates
        self.ui_queue = queue.Queue()
        self.checker_logic = PleskCheckerLogic(self.ui_queue)
        self._after_id = self.after(100, self.process_ui_queue) # Start processing UI updates and store ID

        # Title Label
        self.title_label = customtkinter.CTkLabel(self, text='PLESK CHECKER GUI', font=customtkinter.CTkFont(size=28, weight='bold'))
        self.title_label.pack(pady=(18, 5))

        # Help Button
        self.help_button = customtkinter.CTkButton(self, text='Bantuan', command=self.show_help_menu, width=100)
        self.help_button.place(relx=1.0, rely=0.0, anchor='ne', x=-15, y=15)

        # Top Frame (Input and Buttons)
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.pack(pady=8, padx=15, fill='x')
        
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=0)
        self.top_frame.grid_columnconfigure(2, weight=0)
        self.top_frame.grid_columnconfigure(3, weight=0)
        self.top_frame.grid_columnconfigure(4, weight=0)
        self.top_frame.grid_columnconfigure(5, weight=1)

        self.file_path_entry = customtkinter.CTkEntry(self.top_frame, textvariable=customtkinter.StringVar(), width=400)
        self.file_path_entry.grid(row=0, column=1, padx=(0, 5), pady=10)

        self.browse_button = customtkinter.CTkButton(self.top_frame, text='Browse', command=self.browse_file, width=100)
        self.browse_button.grid(row=0, column=2, padx=5, pady=10)

        self.start_button = customtkinter.CTkButton(self.top_frame, text='▶ Start', command=self.start_checking, width=100, fg_color="#28a745", hover_color="#218838")
        self.start_button.grid(row=0, column=3, padx=5, pady=10)

        self.stop_button = customtkinter.CTkButton(self.top_frame, text='⏹ Stop', command=self.stop_checking, width=100, state='disabled', fg_color="#dc3545", hover_color="#c82333")
        self.stop_button.grid(row=0, column=4, padx=5, pady=10)

        # Progress Frame (Progress Bar and Counts)
        self.progress_frame = customtkinter.CTkFrame(self)
        self.progress_frame.pack(pady=(5, 0), padx=15, fill='x')
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=1)
        self.progress_frame.grid_columnconfigure(2, weight=1)
        self.progress_frame.grid_columnconfigure(3, weight=1)

        self.progress_bar = customtkinter.CTkProgressBar(self.progress_frame, width=600, height=18, corner_radius=8)
        self.progress_bar.grid(row=0, column=0, columnspan=4, padx=10, pady=8, sticky="ew")
        self.progress_bar.set(0)

        self.progress_percentage_label = customtkinter.CTkLabel(self.progress_frame, text='0%', font=customtkinter.CTkFont(size=13, weight='bold'))
        self.progress_percentage_label.place(in_=self.progress_bar, relx=0.5, rely=0.5, anchor='center')

        self.berhasil_label = customtkinter.CTkLabel(self.progress_frame, text='Berhasil: 0', text_color='#218838', font=customtkinter.CTkFont(size=14, weight='bold'))
        self.berhasil_label.grid(row=1, column=0, padx=10, sticky='ew')

        self.gagal_label = customtkinter.CTkLabel(self.progress_frame, text='Gagal: 0', text_color='#c82333', font=customtkinter.CTkFont(size=14, weight='bold'))
        self.gagal_label.grid(row=1, column=1, padx=10, sticky='ew')

        self.timeout_label = customtkinter.CTkLabel(self.progress_frame, text='Timeout: 0', text_color='#ff8800', font=customtkinter.CTkFont(size=14, weight='bold'))
        self.timeout_label.grid(row=1, column=2, padx=10, sticky='ew')

        self.duplikat_label = customtkinter.CTkLabel(self.progress_frame, text='Duplikat: 0', text_color='#6c757d', font=customtkinter.CTkFont(size=14, weight='bold'))
        self.duplikat_label.grid(row=1, column=3, padx=10, sticky='ew')

        # Tabview for results
        self.tabview = customtkinter.CTkTabview(self, width=800, height=400)
        self.tabview.pack(pady=15, padx=15, fill='both', expand=True)
        self.tab_all = self.tabview.add('All Results')
        self.tab_valid = self.tabview.add('List Valid Plesk')
        self.tabview.set('All Results')

        # Treeview for All Results
        columns_all = ('No', 'URL', 'Username', 'Password', 'Status')
        self.all_results_treeview = create_treeview(self.tab_all, columns_all)
        self.all_results_treeview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure tags for coloring in All Results Treeview
        self.all_results_treeview.tag_configure('ACTIVE', foreground='#000000', background='#D4EDDA')
        self.all_results_treeview.tag_configure('SUSPENDED', foreground='#000000', background='#D4EDDA')
        self.all_results_treeview.tag_configure('NO SUBSCRIPTIONS', foreground='#000000', background='#D4EDDA')
        self.all_results_treeview.tag_configure('FAILED', foreground='#000000', background='#F8D7DA')
        self.all_results_treeview.tag_configure('TIMEOUT', foreground='#000000', background='#FFF3CD')
        self.all_results_treeview.tag_configure('INVALID_FORMAT', foreground='#000000', background='#E2E3E5')

        # Treeview for List Valid Plesk
        columns_valid = ('No', 'URL', 'Username', 'Password', 'Status', 'Login')
        self.valid_plesk_treeview = create_treeview(self.tab_valid, columns_valid)
        self.valid_plesk_treeview.pack(fill="both", expand=True, padx=5, pady=5)

        # Pagination Frame for List Valid Plesk
        self.pagination_frame = customtkinter.CTkFrame(self.tab_valid)
        self.pagination_frame.pack(side='bottom', fill='x', padx=5, pady=5)
        
        self.pagination_frame.grid_columnconfigure(0, weight=1)
        self.pagination_frame.grid_columnconfigure(1, weight=0)
        self.pagination_frame.grid_columnconfigure(2, weight=0)
        self.pagination_frame.grid_columnconfigure(3, weight=0)
        self.pagination_frame.grid_columnconfigure(4, weight=1)
        
        self.total_items_label = customtkinter.CTkLabel(self.pagination_frame, text="Total: 0 item")
        self.total_items_label.grid(row=0, column=0, padx=10, sticky='w')
        
        self.prev_page_btn = customtkinter.CTkButton(self.pagination_frame, text="←", width=40, command=self.prev_page)
        self.prev_page_btn.grid(row=0, column=1, padx=5)
        
        self.page_info = customtkinter.CTkLabel(self.pagination_frame, text="Halaman 1 dari 1")
        self.page_info.grid(row=0, column=2, padx=10)
        
        self.next_page_btn = customtkinter.CTkButton(self.pagination_frame, text="→", width=40, command=self.next_page)
        self.next_page_btn.grid(row=0, column=3, padx=5)
        
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.total_items = 0
        self.all_items = []
        self.login_buttons = {}

        self.valid_plesk_treeview.bind('<Configure>', self.update_login_buttons_placement)

        # Status Bar
        self.status_frame = customtkinter.CTkFrame(self, height=30, corner_radius=0, fg_color="#E0E0E0")
        self.status_frame.pack(side="bottom", fill="x")
        
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(1, weight=0)
        self.status_frame.grid_columnconfigure(2, weight=0)
        self.status_frame.grid_columnconfigure(3, weight=0)
        
        self.status_label = customtkinter.CTkLabel(self.status_frame, text='Status: Menunggu input file...', 
                                       font=customtkinter.CTkFont(size=11, weight='bold'), 
                                       text_color='#0056b3',
                                       anchor='w')
        self.status_label.grid(row=0, column=0, padx=5, sticky='w')
        
        self.time_frame = customtkinter.CTkFrame(self.status_frame, fg_color="transparent")
        self.time_frame.grid(row=0, column=2, padx=5, sticky='e')
        
        self.start_time_label = customtkinter.CTkLabel(self.time_frame, text='Mulai: -', font=customtkinter.CTkFont(size=11))
        self.start_time_label.pack(side='left', padx=5)
        
        self.eta_label = customtkinter.CTkLabel(self.time_frame, text='ETA: -', font=customtkinter.CTkFont(size=11))
        self.eta_label.pack(side='left', padx=5)
        
        self.finish_time_label = customtkinter.CTkLabel(self.time_frame, text='Selesai: -', font=customtkinter.CTkFont(size=11))
        self.finish_time_label.pack(side='left', padx=5)

        # Load existing valid Plesk entries on startup via checker_logic
        self.checker_logic.load_valid_plesk_from_file()
        # Ensure buttons are placed correctly after initial load
        self.update_idletasks()
        self.after(1, self.update_login_buttons_placement)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def browse_file(self):
        file_path = tkinter.filedialog.askopenfilename(title='Pilih File List', filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.file_path_entry.delete(0, customtkinter.END)
            self.file_path_entry.insert(0, file_path)
            self.update_status("File dipilih.")
            self.clear_results() # Clear UI results
            try:
                lines = read_lines_from_file(file_path)
                line_count = len(lines)
                file_name = os.path.basename(file_path)
                self.update_status(f'File: {file_name} (Total baris: {line_count})')
            except Exception as e:
                self.update_status('File: (Gagal membaca jumlah baris)')

    def update_status(self, message):
        self.status_label.configure(text=f'Status: {message}')

    def clear_results(self):
        for item in self.all_results_treeview.get_children():
            self.all_results_treeview.delete(item)
        for item in self.valid_plesk_treeview.get_children():
            self.valid_plesk_treeview.delete(item)
        
        # Clear all login buttons
        for item_id in list(self.login_buttons.keys()):
            if item_id in self.login_buttons:
                self.login_buttons[item_id]['button'].destroy() # Access the button object
                del self.login_buttons[item_id]

        # Reset UI counts and progress
        self.berhasil_label.configure(text=f"Berhasil: 0")
        self.gagal_label.configure(text=f"Gagal: 0")
        self.timeout_label.configure(text=f"Timeout: 0")
        self.duplikat_label.configure(text=f"Duplikat: 0")
        self.progress_bar.set(0)
        self.progress_percentage_label.configure(text="0%")
        self.start_time_label.configure(text="Mulai: -")
        self.eta_label.configure(text="ETA: -")
        self.finish_time_label.configure(text="Selesai: -")

        # Reset pagination and all_items for UI
        self.current_page = 1
        self.total_pages = 1
        self.total_items = 0
        self.all_items = []
        self.update_pagination()

    def start_checking(self):
        file_path = self.file_path_entry.get()
        if not file_path:
            CTkMessagebox(title="Error", message="Mohon pilih file list terlebih dahulu.", icon="warning", option_1="OK")
            return

        self.clear_results()
        self.checker_logic.start_checking(file_path)
        self.update_status("Memulai pengecekan...")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_checking(self):
        msg_box = CTkMessagebox(title="Konfirmasi", message="Apakah Anda yakin ingin menghentikan proses pengecekan?", icon="question", option_1="Tidak", option_2="Ya")
        response = msg_box.get()
        if response == "Ya":
            self.checker_logic.stop_checking()
            self.update_status("Pengecekan dihentikan.")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.progress_percentage_label.configure(text="Dihentikan!")

    def process_ui_queue(self):
        try:
            while True:
                task = self.ui_queue.get_nowait()
                if task["type"] == "update_progress":
                    processed = task["processed"]
                    total = self.checker_logic.total_lines # Get total_lines from logic
                    if total > 0:
                        progress_value = processed / total
                        self.progress_bar.set(progress_value)
                        self.progress_percentage_label.configure(text=f"{int(progress_value * 100)}%")
                        if self.checker_logic.start_time:
                            self.eta_label.configure(text=f'ETA: {calculate_eta(self.checker_logic.start_time, processed, total)}')
                        self.update_status(f"Memproses baris {processed} dari {total}...")
                    else:
                        self.progress_percentage_label.configure(text="0%")
                        self.eta_label.configure(text="ETA: -")
                        self.update_status("Memproses...")
                elif task["type"] == "update_counts":
                    counts = task["counts"]
                    self.berhasil_label.configure(text=f"Berhasil: {counts['valid']}")
                    self.gagal_label.configure(text=f"Gagal: {counts['failed']}")
                    self.timeout_label.configure(text=f"Timeout: {counts['timeout']}")
                    self.duplikat_label.configure(text=f"Duplikat: {counts['duplicate']}")
                elif task["type"] == "add_all_results":
                    self.all_results_treeview.insert("", "end", values=task["data"], tags=(task["status"],))
                    self.all_results_treeview.yview_moveto(1.0)
                elif task["type"] == "add_valid_plesk":
                    # This message comes with a single new valid item
                    self.all_items.append(task["data"])
                    self.total_items = len(self.all_items)
                    self.total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
                    self.display_current_page()
                elif task["type"] == "load_valid_plesk_data":
                    # This message comes with all loaded items from file
                    self.all_items = task["items"]
                    self.total_items = len(self.all_items)
                    self.total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
                    self.current_page = 1
                    self.display_current_page()
                elif task["type"] == "update_status":
                    self.update_status(task["message"])
                elif task["type"] == "update_time":
                    if task["key"] == "start":
                        self.start_time_label.configure(text=f"Mulai: {task['value']}")
                    elif task["key"] == "eta":
                        self.eta_label.configure(text=f"ETA: {task['value']}")
                    elif task["key"] == "finish":
                        self.finish_time_label.configure(text=f"Selesai: {task['value']}")
                        if self.checker_logic.start_time:
                            self.eta_label.configure(text=f'Durasi: {calculate_duration(self.checker_logic.start_time, datetime.datetime.now())}')
                elif task["type"] == "finished":
                    self.update_status("Pengecekan selesai!")
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.progress_percentage_label.configure(text="Selesai!")
                elif task["type"] == "start_button_state":
                    self.start_button.configure(state=task["state"])
                elif task["type"] == "stop_button_state":
                    self.stop_button.configure(state=task["state"])
                elif task["type"] == "progress_text":
                    self.progress_percentage_label.configure(text=task["text"])
                elif task["type"] == "progress_bar_value":
                    self.progress_bar.set(task["value"])
                elif task["type"] == "show_messagebox":
                    CTkMessagebox(title=task["title"], message=task["message"], icon=task["icon"], option_1="OK")
                self.ui_queue.task_done()
        except queue.Empty:
            pass
        self.after(100, self.process_ui_queue)

    def show_help_menu(self):
        help_window = customtkinter.CTkToplevel(self)
        help_window.title("Bantuan")
        help_window.geometry("600x400")
        help_window.resizable(False, False)
        
        help_window.transient(self)
        help_window.grab_set()
        
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f'{width}x{height}+{x}+{y}')
        
        help_tabview = customtkinter.CTkTabview(help_window)
        help_tabview.pack(fill='both', expand=True, padx=10, pady=10)
        
        tutorial_tab = help_tabview.add("Tutorial")
        tutorial_text = """
1. Pilih File List:
   • Klik tombol 'Browse' untuk memilih file list Plesk
   • Format file: URL|username|password (satu baris per akun)

2. Mulai Pengecekan:
   • Klik tombol 'Start' untuk memulai proses
   • Progress akan ditampilkan di progress bar
   • Hasil akan muncul di tabel secara real-time

3. Hasil Pengecekan:
   • Tab 'All Results': Menampilkan semua hasil pengecekan
   • Tab 'List Valid Plesk': Menampilkan akun yang valid
   • Klik tombol 'Masuk' untuk login otomatis ke Plesk

4. Menghentikan Proses:
   • Klik tombol 'Stop' untuk menghentikan pengecekan
   • Konfirmasi akan diminta sebelum menghentikan
"""
        tutorial_label = customtkinter.CTkLabel(tutorial_tab, text=tutorial_text, justify='left', font=customtkinter.CTkFont(size=12))
        tutorial_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        faq_tab = help_tabview.add("FAQ")
        faq_text = """
Q: Format file list yang didukung?
A: Format: URL|username|password (satu baris per akun)

Q: Berapa lama proses pengecekan?
A: Tergantung jumlah akun dan kecepatan internet

Q: Apa arti status di tabel hasil?
A: • Berhasil: Login berhasil
   • Gagal: Login gagal
   • Timeout: Koneksi timeout
   • Duplikat: Akun sudah ada di list valid

Q: Bagaimana cara login otomatis?
A: Klik tombol 'Masuk' di kolom Action pada list valid

Q: Apakah data login aman?
A: Ya, password ditampilkan dalam bentuk asterisk (*)
"""
        faq_label = customtkinter.CTkLabel(faq_tab, text=faq_text, justify='left', font=customtkinter.CTkFont(size=12))
        faq_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        version_tab = help_tabview.add("Versi")
        version_text = """
PLESK Checker GUI v1.0.0

Fitur Terbaru:
• Login otomatis ke Plesk
• Estimasi waktu selesai
• Tooltip untuk setiap tombol
• Konfirmasi sebelum menghentikan proses

Pembaruan Terakhir:
• Perbaikan tampilan tabel
• Penambahan fitur bantuan
• Optimasi performa
"""
        version_label = customtkinter.CTkLabel(version_tab, text=version_text, justify='left', font=customtkinter.CTkFont(size=12))
        version_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        support_tab = help_tabview.add("Support")
        support_text = """
Untuk bantuan dan dukungan:

Email: kliverz1337@gmail.com
Telegram: @kliverz1337

Laporkan Bug:
• Screenshot error
• Langkah-langkah yang dilakukan
• File list yang digunakan (opsional)
"""
        support_label = customtkinter.CTkLabel(support_tab, text=support_text, justify='left', font=customtkinter.CTkFont(size=12))
        support_label.pack(padx=10, pady=10, fill='both', expand=True)

    def display_current_page(self):
        for row in self.valid_plesk_treeview.get_children():
            self.valid_plesk_treeview.delete(row)
        
        # Clear all login buttons
        for item_id in list(self.login_buttons.keys()):
            if item_id in self.login_buttons:
                self.login_buttons[item_id]['button'].destroy()
                del self.login_buttons[item_id]

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, self.total_items)
        
        # Collect current visible item_ids
        visible_item_ids = set()
        for idx, item_data in enumerate(self.all_items[start_idx:end_idx], start=start_idx + 1):
            # item_data is (line_num, url, username, password_masked, status, password_original)
            line_num, url, username, password_masked, status, password_original = item_data
            
            # Mask password for display in Treeview
            display_password = '*' * len(password_original) if password_original else ''
            
            # Check if item already exists in treeview
            # This is a simplified check; a more robust solution might involve a unique ID for each item
            existing_item_id = None
            for child_id in self.valid_plesk_treeview.get_children():
                values = self.valid_plesk_treeview.item(child_id, 'values')
                if values and values[1] == url and values[2] == username: # Compare URL and Username
                    existing_item_id = child_id
                    break

            if existing_item_id:
                item_id = existing_item_id
                self.valid_plesk_treeview.item(item_id, values=(idx, url, username, display_password, status, ''))
            else:
                item_id = self.valid_plesk_treeview.insert('', 'end', values=(idx, url, username, display_password, status, ''), tags=('VALID', 'cell'))
            
            visible_item_ids.add(item_id)
            self.create_login_button(item_id, item_data)
        
        # Remove buttons for items no longer visible
        for item_id in list(self.login_buttons.keys()):
            if item_id not in visible_item_ids:
                if item_id in self.login_buttons:
                    self.login_buttons[item_id]['button'].destroy()
                    del self.login_buttons[item_id]

        self.update_pagination()
        self.update_login_buttons_placement() # Call a new function for placement

    def update_pagination(self):
        self.page_info.configure(text=f"Halaman {self.current_page} dari {self.total_pages}")
        self.total_items_label.configure(text=f"Total: {self.total_items} item")
        
        self.prev_page_btn.configure(state='normal' if self.current_page > 1 else 'disabled')
        self.next_page_btn.configure(state='normal' if self.current_page < self.total_pages else 'disabled')

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()

    def create_login_button(self, item_id, item_data):
        # item_data is (line_num, url, username, password_masked, status, password_original)
        original_url = item_data[1].strip()
        original_username = item_data[2].strip()
        original_password = item_data[5]
        
        # Hanya buat tombol jika data login lengkap dan tombol belum ada
        if original_url and original_username and original_password.strip() and item_id not in self.login_buttons:
            btn = customtkinter.CTkButton(
                self.tab_valid,
                text="Login", # Change button text back to "Login"
                width=70,
                height=22,
                fg_color="#007bff",
                hover_color="#0056b3",
                command=lambda u=original_url, un=original_username, p=original_password: self.login_single_plesk(u, un, p)
            )
            self.login_buttons[item_id] = {'button': btn, 'data': item_data}
            self.place_login_button(item_id)
        elif item_id in self.login_buttons:
            # If button already exists, just ensure it's placed correctly
            self.place_login_button(item_id)
        else:
            # Logika untuk kasus di mana data login tidak lengkap
            pass

    def place_login_button(self, item_id):
        if item_id in self.login_buttons:
            btn = self.login_buttons[item_id]['button']
            bbox = self.valid_plesk_treeview.bbox(item_id, column='Login')
            if bbox:
                x_center = bbox[0] + (bbox[2] / 2) - (70 / 2) # 70 is the button width
                y_center = bbox[1] + (bbox[3] / 2) - (22 / 2) # 22 is the button height
                btn.place(x=x_center, y=y_center)
            else:
                # If bbox not found (e.g., item not visible), hide the button
                btn.place_forget()

    def update_login_buttons_placement(self, event=None):
        # Pastikan treeview diperbarui sebelum mendapatkan bbox
        self.valid_plesk_treeview.update_idletasks()
        
        # Perbarui posisi tombol yang sudah ada
        for item_id in self.valid_plesk_treeview.get_children():
            self.place_login_button(item_id)
        
        # Hapus tombol yang tidak lagi ada di treeview (misalnya, karena paginasi)
        current_treeview_items = set(self.valid_plesk_treeview.get_children())
        for item_id in list(self.login_buttons.keys()):
            if item_id not in current_treeview_items:
                if item_id in self.login_buttons:
                    self.login_buttons[item_id]['button'].destroy()
                    del self.login_buttons[item_id]

    def initialize_driver(self):
        if self.driver is None:
            try:
                options = webdriver.ChromeOptions()
                # options.add_argument('--headless') # Uncomment this line to run Chrome in headless mode
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--ignore-certificate-errors') # Tambahkan opsi ini untuk mengatasi masalah SSL
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.set_page_load_timeout(15) # Set page load timeout
                CTkMessagebox(title="Info", message="Browser siap digunakan.", icon="info")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Gagal menginisialisasi browser: {e}", icon="warning")
                self.driver = None # Ensure driver is None if initialization fails

    def on_closing(self):
        """Handler for window closing event"""
        self.update_idletasks()
        msg_box = CTkMessagebox(title="Konfirmasi", message="Apakah Anda yakin ingin menutup aplikasi?", icon="question", option_1="Tidak", option_2="Ya")
        response = msg_box.get()
        if response == "Ya":
            # Stop the checker logic thread if it's running
            if self.checker_logic.checking_thread and self.checker_logic.checking_thread.is_alive():
                self.checker_logic.stop_event.set()
                self.checker_logic.checking_thread.join(timeout=1) # Give it a moment to stop
            
            # Cancel the UI queue processing loop
            if self._after_id:
                self.after_cancel(self._after_id)

            # Quit the Selenium driver if it's active
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    print(f"Error saat menutup driver: {e}")
            
            self.destroy() # Destroy the main window directly

    def login_single_plesk(self, url, username, password):
        # This function will be called by each individual "Login" button
        self.update_status(f"Mencoba login ke: {url}")
        
        # Initialize driver if not already initialized
        self.initialize_driver()

        if self.driver:
            open_web_login(self.driver, url, username, password)
        else:
            CTkMessagebox(title="Error", message="Browser tidak dapat diinisialisasi. Tidak dapat melanjutkan login.", icon="warning")

if __name__ == "__main__":
    app = PleskCheckerApp()
    app.mainloop()
