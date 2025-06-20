import datetime
import tkinter.ttk as ttk
import customtkinter
import tkinter.filedialog
import webbrowser
import os
import time # Import time for delays
from CTkMessagebox import CTkMessagebox # Import CTkMessagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
def center_window(window):
    """Memposisikan window di tengah layar"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_treeview(parent_frame, columns):
    tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
    
    # Set column widths
    if "No" in columns:
        tree.column("No", anchor="center", width=40, stretch=False)
    if "URL" in columns:
        tree.column("URL", anchor="w", width=220, stretch=True)
    if "Username" in columns:
        tree.column("Username", anchor="w", width=120, stretch=False)
    if "Password" in columns:
        tree.column("Password", anchor="w", width=120, stretch=False)
    if "Status" in columns:
        tree.column("Status", anchor="center", width=100, stretch=False)
    if "Action" in columns:
        tree.column("Action", anchor="center", width=100, stretch=False)

    for col in columns:
        tree.heading(col, text=col, anchor="center")
        if tree.column(col, 'width') == 0:
            tree.column(col, anchor="center", width=100)

    # Add scrollbar
    scrollbar_y = customtkinter.CTkScrollbar(parent_frame, command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)


    # Apply styling
    style = ttk.Style()
    style.configure("Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=25,
                   fieldbackground="white",
                   borderwidth=1)
    style.configure("Treeview.Heading",
                   background="#f0f0f0",
                   foreground="black",
                   relief="flat")
    style.map("Treeview.Heading",
             background=[('active', '#e0e0e0')])
    style.layout("Treeview", [
        ('Treeview.treearea', {'sticky': 'nswe', 'border': '1'})
    ])
    tree['show'] = 'headings'
    tree['style'] = 'Treeview'
    style.map('Treeview',
             background=[('selected', '#007bff')],
             foreground=[('selected', 'white')])

    tree.tag_configure('VALID', background='#d4edda', foreground='#155724')
    tree.tag_configure('FAILED', background='#f8d7da', foreground='#721c24')
    tree.tag_configure('TIMEOUT', background='#fff3cd', foreground='#856404')
    tree.tag_configure('DUPLICATE', background='#e2e3e5', foreground='#383d41')
    tree.tag_configure('ERROR', background='#fffbe6', foreground='#856404')
    tree.tag_configure('cell', background='white')

    return tree

def calculate_eta(start_time, processed_lines, total_lines):
    if processed_lines == 0 or total_lines == 0:
        return "N/A"
    
    elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
    if elapsed_time == 0:
        return "N/A"
    
    time_per_line = elapsed_time / processed_lines
    remaining_lines = total_lines - processed_lines
    eta_seconds = remaining_lines * time_per_line
    
    hours, remainder = divmod(int(eta_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def calculate_duration(start_time, end_time):
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def open_web_login(driver, url, username, password):
    # Asumsi URL halaman login Plesk
    login_url = f"{url}/login/"
    
    try:
        CTkMessagebox(title="Info", message=f"Membuka browser untuk login ke {url}...", icon="info")
        driver.get(login_url)

        # Wait for the username field to be present
        wait = WebDriverWait(driver, 10) # Wait up to 10 seconds
        
        # Try to find username and password fields by common names/ids
        username_field = wait.until(EC.presence_of_element_located((By.NAME, 'login_name')))
        password_field = driver.find_element(By.NAME, 'passwd')
        
        # Fill in the credentials
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Find and click the login button
        # Common names/ids for login button: 'login_submit', 'submit', 'button', 'log_in'
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //a[contains(@class, 'button') and contains(text(), 'Log In')]")))
        login_button.click()
        
        # Wait for page to load after login (e.g., wait for dashboard element or URL change)
        # This is a heuristic, adjust as needed for Plesk dashboard
        time.sleep(5) # Give some time for the page to redirect and load

        # Check if login was successful (e.g., URL changed from login page)
        if "/login/" not in driver.current_url:
            CTkMessagebox(title="Sukses", message="Login otomatis berhasil! Browser akan tetap terbuka.", icon="check")
        else:
            CTkMessagebox(title="Gagal", message="Login otomatis gagal. Kredensial mungkin salah atau halaman login berubah.", icon="cancel")

    except TimeoutException:
        CTkMessagebox(title="Error", message=f"Timeout saat memuat halaman atau menemukan elemen di {url}. Pastikan URL benar dan koneksi stabil.", icon="warning")
    except NoSuchElementException:
        CTkMessagebox(title="Error", message=f"Elemen login (username/password/tombol) tidak ditemukan di {url}. Halaman login mungkin berubah.", icon="warning")
    except Exception as e:
        CTkMessagebox(title="Error", message=f"Terjadi kesalahan tidak terduga saat login otomatis: {e}", icon="warning")
