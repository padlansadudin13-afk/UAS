#!/bin/bash
cd "$(dirname "$0")"

echo "================================================"
echo "  SISTEM PEMINJAMAN SOUND SYSTEM - Launcher"
echo "================================================"
echo

# 1. Cek apakah Python terpasang
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 tidak ditemukan. Install dulu dari https://python.org"
    exit 1
fi

# 2. Buat virtual environment kalau belum ada
if [ ! -d "ENV" ]; then
    echo "Membuat virtual environment (sekali saja)..."
    python3 -m venv ENV
fi

# 3. Aktifkan virtual environment
source ENV/bin/activate

# 4. Install/update library yang dibutuhkan
echo "Menyiapkan library yang dibutuhkan..."
pip install -r requirements.txt -q

# 5. Jalankan aplikasi
echo
echo "Menjalankan aplikasi..."
echo "------------------------------------------------"
python main.py
