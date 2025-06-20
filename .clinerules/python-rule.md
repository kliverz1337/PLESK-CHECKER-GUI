# 📘 Panduan Lengkap Analisis Script Python Kompleks oleh AI Assistant

## 📌 Tujuan Asisten
Asisten ini bertugas untuk:
- 🔍 Memahami alur dan struktur script Python yang kompleks
- ⚙️ Melakukan optimasi efisiensi dan keterbacaan
- 🐞 Mendeteksi dan memperbaiki error (sintaks & logika)
- 🧼 Melakukan refactor jika terlalu kompleks
- 🧪 Menambahkan pengujian otomatis
- 🔐 Menjamin keamanan dasar script
- 🚀 Menghasilkan output terbaik dan siap digunakan/produksi

---

## 🧠 1. Memahami Alur Script

### ✅ Langkah:
- Identifikasi **entry point** (`if __name__ == "__main__"`)
- Lacak semua **fungsi yang dipanggil** dalam urutan eksekusi
- Petakan struktur data penting (list, dict, objek, dll)
- Catat interaksi dengan:
  - 📂 File
  - 🌐 API
  - 🗃️ Database
- Identifikasi dependensi dan library eksternal

### 📌 Catatan:
- Entry Point: 
- Fungsi Utama: 
- Struktur Data: 
- Modul Eksternal: 

---

## 🔁 2. Melakukan Optimasi

### ✅ Fokus Optimasi:
- Penghapusan kode redundan/duplikat
- Penggunaan struktur data yang efisien
- Penggunaan loop atau generator yang lebih optimal
- Pengurangan I/O blocking atau delay
- Pemanfaatan `with`, `enumerate`, `set`, `map/filter` dengan benar
- Penataan fungsi agar modular & reusable

### 🛠️ Rekomendasi Optimasi:
- [ ] Loop diganti dengan comprehension
- [ ] Logging ditambahkan untuk debugging
- [ ] Fungsi besar dipecah
- [ ] Gunakan caching jika perlu

---

## 🐞 3. Mencari Error & Debugging

### ✅ Langkah Debug:
- Tambahkan `print()` atau `logging.debug()` pada titik rawan
- Gunakan `try-except` untuk melacak error
- Gunakan `pdb` / debugger interaktif untuk telusuri nilai variabel
- Validasi semua input & output fungsi

### 🔍 Daftar Error Ditemukan:
| Baris | Masalah | Solusi |
|------|---------|--------|
|      |         |        |

---

## 🧼 4. Refactor (Hanya Jika Benar-Benar Diperlukan)

### ✅ Indikasi Refactor Dibutuhkan:
- Fungsi > 50 baris dan punya banyak `if`, `loop`, atau nested
- Banyak variabel global atau pengulangan kode
- Sulit dibaca, tidak ada komentar/docstring
- File tunggal berisi logika campur aduk (I/O, UI, logika bisnis)

### 📦 Langkah Refactor (Lakukan Jika Tidak Ada Cara Lain):
- [ ] Pecah fungsi besar jadi beberapa fungsi kecil
- [ ] Pisahkan logika utama dari antarmuka (misal: CLI/UI vs logic)
- [ ] Pindahkan konfigurasi ke file `.env` atau `.config`
- [ ] Buat struktur folder: `/core`, `/utils`, `/handlers`, dll
- [ ] Gunakan pendekatan OOP (class) bila cocok
- [ ] Tambahkan unit test untuk setiap fungsi penting

### 💡 Contoh Refactor:
| Asli | Refactor |
|------|----------|
| Fungsi `main()` dengan 200 baris | Pecah jadi `load_data()`, `process_data()`, `save_results()` |
| Banyak `print()` acak | Ganti dengan `logging` |
| Logic bercampur dengan UI | Pisahkan di modul terpisah |

---

## 🔬 5. Evaluasi Output dan Hasil

### 📤 Output Diharapkan:
> Deskripsi ringkas dari hasil yang diinginkan (file/output API/etc)

### ✅ Cek Output:
- [ ] Format output benar
- [ ] Data lengkap & akurat
- [ ] Tidak ada error runtime
- [ ] Performanya konsisten dan cepat

---

## 🧪 6. Pengujian (Testing)

### ✅ Checklist:
- [ ] Tambahkan `unit test` (`pytest` / `unittest`)
- [ ] Uji semua fungsi utama
- [ ] Tambahkan skenario gagal (negative test)
- [ ] Struktur folder `/tests`

```bash
/tests
  └── test_main.py
  └── test_utils.py
```

---

## 🔐 7. Keamanan Dasar

### ✅ Checklist:
- [ ] Jangan hardcode API key atau password
- [ ] Validasi semua input
- [ ] Gunakan `os.path.join` untuk keamanan path
- [ ] Audit dependensi dengan `pip-audit`, `bandit`, `safety`

---

## 📊 8. Logging & Monitoring

### ✅ Checklist:
- [ ] Ganti semua `print()` dengan `logging`
- [ ] Simpan log ke file (`app.log`)
- [ ] Tambahkan `logging.INFO`, `ERROR`, dsb
- [ ] Tambahkan timestamp & traceback

```python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
```

---

## 📦 9. Deployment & Packaging

### ✅ Checklist:
- [ ] Tambahkan `requirements.txt` atau `pyproject.toml`
- [ ] Tambahkan `README.md`
- [ ] Gunakan CLI (`argparse`, `click`, `typer`)
- [ ] Gunakan virtualenv, pipenv, atau Docker jika perlu

---

## 🔁 10. Dependency & Struktur Modular

### ✅ Tools:
- [`pydeps`] untuk visualisasi dependensi
- [`pipdeptree`] untuk struktur dependensi Python

---

## 💻 11. Versi & Kompatibilitas

### ✅ Checklist:
- [ ] Minimal Python version: `>=3.8`
- [ ] Kompatibel di OS: Linux / Windows / macOS
- [ ] Periksa dependensi sistem (`apt`, `brew`, `choco`)

---

## ✅ 12. Kesimpulan dan Langkah Selanjutnya

**Status Script Saat Ini:**
> (✅ Siap Produksi | ⚠️ Tahap Debug | ❌ Perlu Refactor Total)

**Langkah Lanjutan:**
- [ ]
- [ ]
- [ ]

---

**Disusun oleh:** `kliverz1337`  
**Tanggal:** `2025-05-31`
