import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import logging

from config import OUTPUT_FILE_STATUS, OUTPUT_FILE_LOGINS
from handlers.plesk_api import check_plesk_login
from handlers.file_handler import is_duplicate, write_to_file, read_lines_from_file

# Konfigurasi logging dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PleskCheckerLogic:
    def __init__(self, ui_queue: queue.Queue):
        self.ui_queue = ui_queue
        self.result_counts = {
            "valid": 0, "failed": 0, "timeout": 0, "duplicate": 0,
            "active": 0, "suspended": 0, "no_subscriptions": 0
        }
        self.total_lines = 0
        self.processed_lines = 0
        self.start_time = None
        self.checking_thread = None
        self.stop_event = threading.Event()
        self.valid_items_set = set()
        self.all_items = [] # Menyimpan semua item valid yang ditemukan/dimuat

        self.load_valid_plesk_from_file()

    def _send_ui_update(self, task_type, **kwargs):
        """Helper to send updates to the UI queue."""
        self.ui_queue.put({"type": task_type, **kwargs})

    def is_item_in_valid_set(self, url, username, password):
        """Checks if a URL, username, password combination is already in the valid_items_set."""
        return (url, username, password) in self.valid_items_set

    def add_item_to_valid_set(self, url, username, password):
        """Adds a URL, username, password combination to the valid_items_set."""
        self.valid_items_set.add((url, username, password))

    def _parse_line(self, line):
        """Parses a single line from the input file."""
        line = line.strip()
        if '|' in line:
            parts = line.split('|')
            if len(parts) == 2 and ':' in parts[1]:
                url = parts[0].strip()
                credentials = parts[1].strip()
                username, password = credentials.split(':', 1)
                return url, username.strip(), password.strip()
            elif len(parts) == 3:
                url = parts[0].strip()
                username = parts[1].strip()
                password = parts[2].strip()
                return url, username, password
        return None, None, None

    def worker_process_line(self, line, output_file, output_file2, line_num):
        if self.stop_event.is_set():
            return

        url, username, password = self._parse_line(line)
        status_text = "INVALID_FORMAT"

        if not (url and username and password):
            self._send_ui_update("add_all_results", data=(line_num, line, "", "", status_text), status=status_text)
            self._send_ui_update("update_status", message=f"Format baris tidak sesuai, dilewati: {line}")
            self.processed_lines += 1
            self._send_ui_update("update_progress", processed=self.processed_lines)
            return

        status = check_plesk_login(url, username, password)
        
        current_counts = self.result_counts.copy()
        if status and status != "FAILED" and status != "TIMEOUT":
            current_counts["valid"] += 1
            status_text = status[3]
            entry = f"{url}|{username}:{password} | {status_text}"
            entry2 = f"{url}|{username}:{password}"
            
            is_dup1 = is_duplicate(output_file, entry)
            is_dup2 = is_duplicate(output_file2, entry2)

            if not is_dup1:
                write_to_file(output_file, entry)
            if not is_dup2:
                write_to_file(output_file2, entry2)
            
            if is_dup1 or is_dup2:
                current_counts["duplicate"] += 1

            if status_text == "ACTIVE":
                current_counts["active"] += 1
            elif status_text == "NO SUBSCRIPTIONS":
                current_counts["no_subscriptions"] += 1
            elif status_text == "SUSPENDED":
                current_counts["suspended"] += 1
            
            self._send_ui_update("add_all_results", data=(line_num, url, username, password, status_text), status=status_text)
            
            if not self.is_item_in_valid_set(url, username, password):
                self.all_items.append((line_num, url, username, '*' * len(password), status_text, password))
                self._send_ui_update("add_valid_plesk", data=(line_num, url, username, '*' * len(password), status_text, password))
                self.add_item_to_valid_set(url, username, password)

        elif status == "FAILED":
            current_counts["failed"] += 1
            status_text = "FAILED"
            self._send_ui_update("add_all_results", data=(line_num, url, username, password, status_text), status=status_text)
        elif status == "TIMEOUT":
            current_counts["timeout"] += 1
            status_text = "TIMEOUT"
            self._send_ui_update("add_all_results", data=(line_num, url, username, password, status_text), status=status_text)
        
        self.result_counts = current_counts # Update internal counts
        self._send_ui_update("update_counts", counts=self.result_counts)
        
        self.processed_lines += 1
        self._send_ui_update("update_progress", processed=self.processed_lines)

    def start_checking(self, input_file):
        if self.checking_thread and self.checking_thread.is_alive():
            logging.warning("Pengecekan sudah berjalan.")
            self._send_ui_update("update_status", message="Pengecekan sudah berjalan.")
            return

        self.reset_state()
        self._send_ui_update("update_status", message="Memulai pengecekan...")
        self._send_ui_update("start_button_state", state="disabled")
        self._send_ui_update("stop_button_state", state="normal")
        self.stop_event.clear()

        self.start_time = datetime.datetime.now()
        self._send_ui_update("update_time", key="start", value=self.start_time.strftime("%H:%M:%S"))

        def run_in_thread():
            try:
                lines = read_lines_from_file(input_file)
                self.total_lines = len(lines)
                self._send_ui_update("update_status", message=f"Total list: {self.total_lines}")
                
                output_file2 = OUTPUT_FILE_LOGINS
                output_file = OUTPUT_FILE_STATUS

                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(self.worker_process_line, line, output_file, output_file2, i + 1)
                               for i, line in enumerate(lines)]
                    
                    for future in as_completed(futures):
                        if self.stop_event.is_set():
                            logging.info("Pengecekan dihentikan oleh pengguna.")
                            break
                        future.result()

                self._send_ui_update("finished")
                self._send_ui_update("update_time", key="finish", value=datetime.datetime.now().strftime("%H:%M:%S"))

            except FileNotFoundError:
                logging.error(f"File tidak ditemukan: {input_file}")
                self._send_ui_update("update_status", message=f"File tidak ditemukan: {input_file}")
                self._send_ui_update("finished")
            except Exception as e:
                logging.exception(f"Terjadi kesalahan saat pengecekan: {e}")
                self._send_ui_update("update_status", message=f"Terjadi kesalahan: {e}")
                self._send_ui_update("finished")

        self.checking_thread = threading.Thread(target=run_in_thread)
        self.checking_thread.start()

    def stop_checking(self):
        if not self.checking_thread or not self.checking_thread.is_alive():
            logging.warning("Pengecekan tidak berjalan.")
            self._send_ui_update("update_status", message="Pengecekan tidak berjalan.")
            return

        self.stop_event.set()
        self._send_ui_update("update_status", message="Menghentikan pengecekan...")
        self._send_ui_update("progress_text", text="Menghentikan...")
        self._send_ui_update("progress_bar_value", value=0)
        self._send_ui_update("start_button_state", state="normal")
        self._send_ui_update("stop_button_state", state="disabled")
        
        if self.checking_thread and self.checking_thread.is_alive():
            self._send_ui_update("update_status", message="Menunggu thread selesai...")
            self.checking_thread.join(timeout=5)
            if self.checking_thread.is_alive():
                logging.warning("Thread tidak berhenti dalam waktu yang ditentukan.")
                self._send_ui_update("show_messagebox", title="Peringatan", message="Thread tidak berhenti dalam waktu yang ditentukan. Mungkin perlu menutup aplikasi secara manual.", icon="warning")
            else:
                self._send_ui_update("update_status", message="Thread pengecekan dihentikan.")
        
        self.reset_state()
        self._send_ui_update("update_status", message="Pengecekan dihentikan.")
        self._send_ui_update("show_messagebox", title="Proses Dihentikan", message="Pengecekan telah dihentikan dan tampilan direset.", icon="check")

    def reset_state(self):
        """Resets the internal state of the checker logic."""
        self.result_counts = {
            "valid": 0, "failed": 0, "timeout": 0, "duplicate": 0,
            "active": 0, "suspended": 0, "no_subscriptions": 0
        }
        self.total_lines = 0
        self.processed_lines = 0
        self.start_time = None
        self.valid_items_set.clear()
        self.all_items = []
        self.load_valid_plesk_from_file() # Reload existing valid Plesk entries

    def load_valid_plesk_from_file(self):
        filepath = "valid_plesk_status.txt"
        try:
            lines = read_lines_from_file(filepath)
            loaded_items = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.rsplit('|', 1)
                if len(parts) == 2:
                    url_credentials = parts[0].strip()
                    status_from_file = parts[1].strip()
                    
                    url_credentials_parts = url_credentials.split('|', 1)
                    if len(url_credentials_parts) == 2:
                        url = url_credentials_parts[0].strip()
                        credentials = url_credentials_parts[1].strip()
                        
                        username_password_parts = credentials.split(':', 1)
                        if len(username_password_parts) == 2:
                            username = username_password_parts[0].strip()
                            password = username_password_parts[1].strip()
                            
                            masked_password = '*' * len(password) if password else ''
                            
                            loaded_items.append((i + 1, url, username, masked_password, status_from_file, password))
                            self.add_item_to_valid_set(url, username, password)
                        else:
                            logging.warning(f"Format kredensial tidak sesuai di baris {i+1}: {line}")
                    else:
                        logging.warning(f"Format URL/kredensial tidak sesuai di baris {i+1}: {line}")
                else:
                    logging.warning(f"Format baris tidak sesuai di baris {i+1}: {line}")
            
            self.all_items = loaded_items
            logging.info(f"Memuat {len(self.all_items)} entri dari {filepath}.")
            self._send_ui_update("load_valid_plesk_data", items=self.all_items)
            self._send_ui_update("update_status", message=f"Memuat {len(self.all_items)} entri dari {filepath}.")
        except FileNotFoundError:
            logging.info(f"File {filepath} tidak ditemukan. Memulai dengan list kosong.")
            self._send_ui_update("update_status", message=f"File {filepath} tidak ditemukan. Memulai dengan list kosong.")
        except Exception as e:
            logging.exception(f"Gagal memuat {filepath}: {e}")
            self._send_ui_update("update_status", message=f"Gagal memuat {filepath}: {e}")
