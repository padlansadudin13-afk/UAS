@echo off
setlocal
cd /d "%~dp0"

echo ================================================
echo   SISTEM PEMINJAMAN SOUND SYSTEM - Launcher
echo ================================================
echo.

REM 1. Cek apakah Python terpasang
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan di komputer ini.
    echo         Install Python dulu dari https://python.org
    echo         Saat install, centang "Add python.exe to PATH".
    pause
    exit /b 1
)

REM 2. Buat virtual environment kalau belum ada
if not exist "ENV\" (
    echo Membuat virtual environment ^(sekali saja^)...
    python -m venv ENV
    if errorlevel 1 (
        echo [ERROR] Gagal membuat virtual environment.
        pause
        exit /b 1
    )
)

REM 3. Aktifkan virtual environment
call ENV\Scripts\activate.bat

REM 4. Install/update library yang dibutuhkan
echo Menyiapkan library yang dibutuhkan...
pip install -r requirements.txt -q

REM 5. Jalankan aplikasi
echo.
echo Menjalankan aplikasi...
echo ------------------------------------------------
python main.py

echo.
pause
