import os

def is_duplicate(output_file, entry):
    """
    Fungsi untuk memeriksa apakah hasil sudah ada di file.
    Membaca seluruh file ke dalam memori untuk efisiensi jika file tidak terlalu besar.
    """
    try:
        with open(output_file, 'r', encoding='utf-8') as output:
            # Read all lines into a set for faster lookup
            existing_entries = set(line.strip() for line in output)
            return entry in existing_entries
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking duplicate in {output_file}: {e}")
        return False

def write_to_file(filepath, content):
    """Menulis konten ke file."""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"{content}\n")
        return True
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")
        return False

def read_lines_from_file(filepath):
    """Membaca semua baris dari file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []
