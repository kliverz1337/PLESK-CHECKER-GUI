import datetime
import tkinter.ttk as ttk
import customtkinter
import tkinter.filedialog
import webbrowser
import os
from CTkMessagebox import CTkMessagebox # Import CTkMessagebox

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
