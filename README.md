# Sistem Peminjaman Sound System

Aplikasi CLI untuk mengelola peminjaman alat sound system (speaker, mixer,
mikrofon, kabel), dibuat dengan konsep OOP (Encapsulation, Inheritance,
Polymorphism, Abstraction) dan tersimpan otomatis ke database MySQL/MariaDB.

## 🚀 Cara Tercepat Menjalankan (disarankan)

**Syarat**: MySQL/MariaDB (XAMPP) sudah di-Start, dan Python sudah terinstall.

- **Windows** → double-click file **`jalankan.bat`**
- **Mac/Linux** → buka terminal di folder ini, jalankan: `./jalankan.sh`

Launcher ini otomatis akan:
1. Membuat virtual environment (`ENV`) kalau belum ada
2. Mengaktifkannya
3. Menginstall semua library yang dibutuhkan
4. Menjalankan aplikasinya

Kamu tidak perlu mengetik perintah `venv`, `activate`, atau `pip install` manual sama sekali.

## Cara Manual (kalau launcher tidak berhasil)

### 1. Pastikan MySQL/MariaDB sudah berjalan
Kalau pakai XAMPP: buka **XAMPP Control Panel**, klik **Start** di baris **MySQL**.

### 2. Buat virtual environment (sekali saja)
```bash
python -m venv ENV
```

### 3. Aktifkan virtual environment
- Windows (PowerShell):
  ```powershell
  ENV\Scripts\Activate.ps1
  ```
- Windows (CMD):
  ```cmd
  ENV\Scripts\activate.bat
  ```
- Mac/Linux:
  ```bash
  source ENV/bin/activate
  ```
Pastikan muncul `(ENV)` di depan prompt terminal.

### 4. Install library yang dibutuhkan
```bash
pip install -r requirements.txt
```

### 5. Jalankan aplikasi
```bash
python main.py
```

Tabel database akan **dibuat otomatis** saat pertama kali dijalankan.

## Konfigurasi Database
Buka file **`config.ini`** kalau perlu mengubah host/user/password MySQL —
tidak perlu mengedit file `main.py` sama sekali.

## Akun contoh
| Role      | Username | Password  |
|-----------|----------|-----------|
| Admin     | admin    | admin123  |
| Pelanggan | budi     | budi123   |

## Tips Pemakaian
- Saat program minta input, ketik **`x`** untuk membatalkan proses dan
  kembali ke menu.
- Menu Admin bisa: kelola alat, ubah status alat, lihat & selesaikan transaksi.
- Menu Pelanggan bisa: lihat alat tersedia, buat peminjaman, lihat transaksi sendiri.

## Struktur Kode (konsep OOP)
| Pilar OOP     | Implementasi |
|---------------|--------------|
| Encapsulation | Atribut `__status`, `__harga_sewa` di `AlatSound` bersifat private, diakses lewat getter/setter |
| Inheritance   | `AlatSound` (superclass) -> `KelasSpeaker`, `KelasMixer`, `KelasMikrofon`, `KelasKabel` |
| Polymorphism  | `hitung_biaya_perawatan()` di-override berbeda di tiap subclass alat |
| Abstraction   | `Transaksi` (abstract class) -> `PeminjamanReguler`, `PeminjamanPaketEvent` |

## Isi Folder
```
main.py            -> kode utama aplikasi
config.ini          -> konfigurasi koneksi database (edit ini kalau perlu)
requirements.txt    -> daftar library yang dibutuhkan
jalankan.bat        -> launcher otomatis untuk Windows (double-click)
jalankan.sh         -> launcher otomatis untuk Mac/Linux
README.md           -> panduan ini
```
