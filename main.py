# -*- coding: utf-8 -*-
"""
=====================================================================
SISTEM INFORMASI MANAJEMEN PEMINJAMAN AUDIO (SOUND SYSTEM)
Berbasis Object-Oriented Programming (OOP) + Database MySQL/MariaDB
=====================================================================
Pilar OOP yang diimplementasikan:
  1. ENCAPSULATION  -> atribut private/protected + getter/setter
  2. INHERITANCE    -> AlatSound (superclass) -> KelasSpeaker, KelasMixer,
                       KelasMikrofon, KelasKabel (subclass)
  3. POLYMORPHISM   -> hitung_biaya_perawatan() di-override tiap subclass
  4. ABSTRACTION    -> Transaksi (abstract class) -> PeminjamanReguler,
                       PeminjamanPaketEvent

CARA MENJALANKAN (lihat juga README.md):
  1. Pastikan MySQL/MariaDB sedang running.
  2. Edit file config.ini kalau perlu (host/user/password).
  3. Install library:  pip install -r requirements.txt
  4. Jalankan        :  python main.py
=====================================================================
"""

import configparser
import os
import sys
from abc import ABC, abstractmethod
from datetime import date

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ Library 'mysql-connector-python' belum terinstall.")
    print("   Jalankan dulu: pip install -r requirements.txt")
    sys.exit(1)


# =====================================================================
# KONFIGURASI -> dibaca dari config.ini (tidak perlu edit kode)
# =====================================================================
def muat_konfigurasi():
    config = configparser.ConfigParser()
    lokasi_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")

    if not os.path.exists(lokasi_file):
        print(f"❌ File config.ini tidak ditemukan di: {lokasi_file}")
        print("   Pastikan config.ini ada di folder yang sama dengan main.py")
        sys.exit(1)

    config.read(lokasi_file)
    try:
        db = config["database"]
        return {
            "host": db.get("host", "localhost"),
            "user": db.get("user", "root"),
            "password": db.get("password", ""),
            "database_name": db.get("database_name", "sound_rental_system"),
        }
    except KeyError:
        print("❌ config.ini tidak lengkap. Pastikan ada bagian [database].")
        sys.exit(1)


def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def tekan_enter_lanjut():
    input("\nTekan ENTER untuk melanjutkan...")


# =====================================================================
# KONEKSI & SETUP DATABASE
# =====================================================================
def buat_koneksi(cfg, dengan_database=True):
    try:
        params = {
            "host": cfg["host"],
            "user": cfg["user"],
            "password": cfg["password"],
        }
        if dengan_database:
            params["database"] = cfg["database_name"]
        conn = mysql.connector.connect(**params)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"\n❌ Gagal konek ke database.\n   Detail: {e}")
        print("\n   Kemungkinan sebab:")
        print("   - MySQL/MariaDB (XAMPP) belum di-Start")
        print("   - host/user/password di config.ini salah")
        sys.exit(1)


def siapkan_database(cfg):
    conn = buat_koneksi(cfg, dengan_database=False)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {cfg['database_name']}")
    conn.commit()
    cursor.close()
    conn.close()

    conn = buat_koneksi(cfg)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(100) NOT NULL,
            nama VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alat (
            id_alat VARCHAR(20) PRIMARY KEY,
            jenis VARCHAR(20) NOT NULL,
            merk VARCHAR(50) NOT NULL,
            harga_sewa INT NOT NULL,
            status VARCHAR(20) NOT NULL,
            daya_watt INT NULL,
            jam_pakai INT NULL,
            jumlah_channel INT NULL,
            tipe_mikrofon VARCHAR(20) NULL,
            panjang_meter INT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id_transaksi VARCHAR(20) PRIMARY KEY,
            jenis VARCHAR(20) NOT NULL,
            nama_pelanggan VARCHAR(100) NOT NULL,
            tanggal_pinjam DATE NOT NULL,
            tanggal_kembali_rencana DATE NOT NULL,
            tanggal_kembali_aktual DATE NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi_alat (
            id_transaksi VARCHAR(20),
            id_alat VARCHAR(20),
            PRIMARY KEY (id_transaksi, id_alat),
            FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi),
            FOREIGN KEY (id_alat) REFERENCES alat(id_alat)
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, nama, role) VALUES (%s,%s,%s,%s)",
            ("admin", "admin123", "Admin Vendor", "Admin")
        )
        cursor.execute(
            "INSERT INTO users (username, password, nama, role) VALUES (%s,%s,%s,%s)",
            ("budi", "budi123", "Budi Santoso", "Pelanggan")
        )

    cursor.execute("SELECT COUNT(*) FROM alat")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """INSERT INTO alat (id_alat, jenis, merk, harga_sewa, status, daya_watt, jam_pakai)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            ("A001", "Speaker", "JBL", 150000, "Tersedia", 500, 12)
        )
        cursor.execute(
            """INSERT INTO alat (id_alat, jenis, merk, harga_sewa, status, jumlah_channel)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            ("A002", "Mixer", "Yamaha", 200000, "Tersedia", 16)
        )
        cursor.execute(
            """INSERT INTO alat (id_alat, jenis, merk, harga_sewa, status, tipe_mikrofon)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            ("A003", "Mikrofon", "Shure", 50000, "Tersedia", "Wireless")
        )
        cursor.execute(
            """INSERT INTO alat (id_alat, jenis, merk, harga_sewa, status, panjang_meter)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            ("A004", "Kabel", "Canare", 10000, "Tersedia", 20)
        )

    conn.commit()
    cursor.close()
    conn.close()


# =====================================================================
# 1. ENCAPSULATION + 2. INHERITANCE + 3. POLYMORPHISM
# =====================================================================
class AlatSound:
    STATUS_VALID = ("Tersedia", "Disewa", "Rusak/Perbaikan")
    JENIS = "AlatSound"

    def __init__(self, id_alat, merk, harga_sewa, status="Tersedia"):
        self._id_alat = id_alat
        self._merk = merk
        self.__status = None
        self.__harga_sewa = None
        self.set_status(status)
        self.set_harga_sewa(harga_sewa)

    def get_id(self):
        return self._id_alat

    def get_merk(self):
        return self._merk

    def get_status(self):
        return self.__status

    def set_status(self, status_baru):
        if status_baru not in self.STATUS_VALID:
            raise ValueError(f"Status tidak valid. Pilih salah satu: {self.STATUS_VALID}")
        self.__status = status_baru

    def get_harga_sewa(self):
        return self.__harga_sewa

    def set_harga_sewa(self, harga):
        if harga < 0:
            raise ValueError("Harga sewa tidak boleh bernilai negatif!")
        self.__harga_sewa = harga

    def hitung_biaya_perawatan(self):
        raise NotImplementedError("Subclass harus mengimplementasikan method ini")

    def detail_khusus(self):
        return "-"

    def kolom_db_khusus(self):
        return {}

    def info(self):
        return (f"{self._id_alat:<6}{self.__class__.__name__:<15}{self._merk:<15}"
                f"{self.get_status():<18}Rp{self.get_harga_sewa():<12,}{self.detail_khusus()}")


class KelasSpeaker(AlatSound):
    JENIS = "Speaker"

    def __init__(self, id_alat, merk, harga_sewa, daya_watt, jam_pakai=0, status="Tersedia"):
        super().__init__(id_alat, merk, harga_sewa, status)
        self.daya_watt = daya_watt
        self.jam_pakai = jam_pakai

    def hitung_biaya_perawatan(self):
        return self.jam_pakai * 5000

    def detail_khusus(self):
        return f"{self.daya_watt}W | {self.jam_pakai} jam pakai"

    def kolom_db_khusus(self):
        return {"daya_watt": self.daya_watt, "jam_pakai": self.jam_pakai}


class KelasMixer(AlatSound):
    JENIS = "Mixer"

    def __init__(self, id_alat, merk, harga_sewa, jumlah_channel, status="Tersedia"):
        super().__init__(id_alat, merk, harga_sewa, status)
        self.jumlah_channel = jumlah_channel

    def hitung_biaya_perawatan(self):
        return self.jumlah_channel * 20000

    def detail_khusus(self):
        return f"{self.jumlah_channel} channel"

    def kolom_db_khusus(self):
        return {"jumlah_channel": self.jumlah_channel}


class KelasMikrofon(AlatSound):
    JENIS = "Mikrofon"

    def __init__(self, id_alat, merk, harga_sewa, tipe="Kabel", status="Tersedia"):
        super().__init__(id_alat, merk, harga_sewa, status)
        self.tipe = tipe

    def hitung_biaya_perawatan(self):
        return 15000 if self.tipe.lower() == "wireless" else 7500

    def detail_khusus(self):
        return f"Tipe: {self.tipe}"

    def kolom_db_khusus(self):
        return {"tipe_mikrofon": self.tipe}


class KelasKabel(AlatSound):
    JENIS = "Kabel"

    def __init__(self, id_alat, merk, harga_sewa, panjang_meter, status="Tersedia"):
        super().__init__(id_alat, merk, harga_sewa, status)
        self.panjang_meter = panjang_meter

    def hitung_biaya_perawatan(self):
        return self.panjang_meter * 1000

    def detail_khusus(self):
        return f"{self.panjang_meter}m"

    def kolom_db_khusus(self):
        return {"panjang_meter": self.panjang_meter}


def alat_dari_row(row):
    (id_alat, jenis, merk, harga_sewa, status,
     daya_watt, jam_pakai, jumlah_channel, tipe_mikrofon, panjang_meter) = row

    if jenis == "Speaker":
        return KelasSpeaker(id_alat, merk, harga_sewa, daya_watt or 0, jam_pakai or 0, status)
    elif jenis == "Mixer":
        return KelasMixer(id_alat, merk, harga_sewa, jumlah_channel or 0, status)
    elif jenis == "Mikrofon":
        return KelasMikrofon(id_alat, merk, harga_sewa, tipe_mikrofon or "Kabel", status)
    elif jenis == "Kabel":
        return KelasKabel(id_alat, merk, harga_sewa, panjang_meter or 0, status)
    else:
        raise ValueError(f"Jenis alat tidak dikenali: {jenis}")


# =====================================================================
# 4. ABSTRACTION
# =====================================================================
class Transaksi(ABC):
    DENDA_PER_HARI = 50_000
    JENIS = "Transaksi"

    def __init__(self, id_transaksi, nama_pelanggan, tanggal_pinjam, tanggal_kembali_rencana,
                 tanggal_kembali_aktual=None):
        self.id_transaksi = id_transaksi
        self.nama_pelanggan = nama_pelanggan
        self.tanggal_pinjam = tanggal_pinjam
        self.tanggal_kembali_rencana = tanggal_kembali_rencana
        self.tanggal_kembali_aktual = tanggal_kembali_aktual
        self.daftar_alat = []

    def tambah_alat(self, alat: AlatSound):
        self.daftar_alat.append(alat)
        alat.set_status("Disewa")

    def selesaikan(self, tanggal_kembali_aktual):
        self.tanggal_kembali_aktual = tanggal_kembali_aktual
        for alat in self.daftar_alat:
            alat.set_status("Tersedia")

    def hitung_denda(self):
        if self.tanggal_kembali_aktual is None:
            return 0
        selisih = (self.tanggal_kembali_aktual - self.tanggal_kembali_rencana).days
        return max(0, selisih) * self.DENDA_PER_HARI

    @abstractmethod
    def hitung_biaya_sewa(self):
        pass

    @abstractmethod
    def jenis_transaksi(self):
        pass

    def cetak_nota(self):
        durasi = max(1, (self.tanggal_kembali_rencana - self.tanggal_pinjam).days)
        biaya_sewa = self.hitung_biaya_sewa()
        denda = self.hitung_denda()
        total = biaya_sewa + denda

        garis = "=" * 50
        lines = [
            garis,
            f"NOTA TRANSAKSI - {self.jenis_transaksi()}".center(50),
            garis,
            f"ID Transaksi   : {self.id_transaksi}",
            f"Pelanggan      : {self.nama_pelanggan}",
            f"Tgl Pinjam     : {self.tanggal_pinjam}",
            f"Tgl Kembali    : {self.tanggal_kembali_rencana} (rencana)",
            f"Durasi Sewa    : {durasi} hari",
            "-" * 50,
            "Daftar Alat:",
        ]
        for alat in self.daftar_alat:
            lines.append(f"  - [{alat.get_id()}] {alat.get_merk()} "
                         f"(Rp{alat.get_harga_sewa():,}/hari)")
        lines += [
            "-" * 50,
            f"Biaya Sewa     : Rp{biaya_sewa:,}",
            f"Denda Telat    : Rp{denda:,}",
            f"TOTAL BAYAR    : Rp{total:,}",
            garis,
        ]
        return "\n".join(lines)


class PeminjamanReguler(Transaksi):
    JENIS = "reguler"

    def hitung_biaya_sewa(self):
        durasi = max(1, (self.tanggal_kembali_rencana - self.tanggal_pinjam).days)
        subtotal_per_hari = sum(alat.get_harga_sewa() for alat in self.daftar_alat)
        return subtotal_per_hari * durasi

    def jenis_transaksi(self):
        return "Peminjaman Reguler"


class PeminjamanPaketEvent(Transaksi):
    JENIS = "event"
    DISKON = 0.10

    def hitung_biaya_sewa(self):
        durasi = max(1, (self.tanggal_kembali_rencana - self.tanggal_pinjam).days)
        subtotal_per_hari = sum(alat.get_harga_sewa() for alat in self.daftar_alat)
        subtotal = subtotal_per_hari * durasi
        return int(subtotal * (1 - self.DISKON))

    def jenis_transaksi(self):
        return "Peminjaman Paket Event"


class User:
    def __init__(self, username, password, nama, role):
        self.username = username
        self.__password = password
        self.nama = nama
        self.role = role

    def cek_password(self, password_input):
        return self.__password == password_input


# =====================================================================
# SISTEM UTAMA
# =====================================================================
class SistemPeminjaman:
    def __init__(self, conn):
        self.conn = conn
        self._counter_transaksi = self._hitung_counter_transaksi_awal()

    def _hitung_counter_transaksi_awal(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transaksi")
        jumlah = cursor.fetchone()[0]
        cursor.close()
        return jumlah

    def id_alat_sudah_ada(self, id_alat):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM alat WHERE id_alat = %s", (id_alat,))
        ada = cursor.fetchone() is not None
        cursor.close()
        return ada

    def tambah_alat(self, alat: AlatSound):
        if self.id_alat_sudah_ada(alat.get_id()):
            return False, f"ID Alat '{alat.get_id()}' sudah dipakai, gunakan ID lain."
        cursor = self.conn.cursor()
        kolom_khusus = alat.kolom_db_khusus()
        kolom_semua = ["id_alat", "jenis", "merk", "harga_sewa", "status"] + list(kolom_khusus.keys())
        nilai_semua = [alat.get_id(), alat.JENIS, alat.get_merk(),
                       alat.get_harga_sewa(), alat.get_status()] + list(kolom_khusus.values())
        placeholder = ", ".join(["%s"] * len(nilai_semua))
        sql = f"INSERT INTO alat ({', '.join(kolom_semua)}) VALUES ({placeholder})"
        cursor.execute(sql, nilai_semua)
        self.conn.commit()
        cursor.close()
        return True, None

    def ambil_semua_alat(self):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT id_alat, jenis, merk, harga_sewa, status,
                                  daya_watt, jam_pakai, jumlah_channel,
                                  tipe_mikrofon, panjang_meter
                           FROM alat ORDER BY id_alat""")
        rows = cursor.fetchall()
        cursor.close()
        return {row[0]: alat_dari_row(row) for row in rows}

    def tampilkan_alat(self):
        daftar_alat = self.ambil_semua_alat()
        if not daftar_alat:
            print("⚠️  Belum ada data alat.")
            return
        print(f"\n{'ID':<6}{'Jenis':<15}{'Merk':<15}{'Status':<18}{'Harga/hari':<14}{'Detail'}")
        print("-" * 90)
        for alat in daftar_alat.values():
            print(alat.info())

    def ubah_status_alat(self, id_alat, status_baru):
        if status_baru not in AlatSound.STATUS_VALID:
            return False, f"Status tidak valid. Pilih salah satu: {AlatSound.STATUS_VALID}"
        if not self.id_alat_sudah_ada(id_alat):
            return False, "Alat tidak ditemukan."
        cursor = self.conn.cursor()
        cursor.execute("UPDATE alat SET status = %s WHERE id_alat = %s", (status_baru, id_alat))
        self.conn.commit()
        cursor.close()
        return True, None

    def cek_bentrok_jadwal(self, id_alat, tgl_pinjam, tgl_kembali):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id_transaksi
            FROM transaksi t
            JOIN transaksi_alat ta ON t.id_transaksi = ta.id_transaksi
            WHERE ta.id_alat = %s
              AND t.tanggal_kembali_aktual IS NULL
              AND %s <= t.tanggal_kembali_rencana
              AND %s >= t.tanggal_pinjam
        """, (id_alat, tgl_pinjam, tgl_kembali))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return True, row[0]
        return False, None

    def buat_transaksi(self, jenis, nama_pelanggan, id_alat_list, tgl_pinjam, tgl_kembali):
        if tgl_kembali < tgl_pinjam:
            return None, "Tanggal kembali tidak boleh sebelum tanggal pinjam."
        if not id_alat_list:
            return None, "Minimal pilih 1 alat untuk disewa."

        daftar_alat = self.ambil_semua_alat()
        alat_objs = []

        for id_alat in id_alat_list:
            alat = daftar_alat.get(id_alat)
            if alat is None:
                return None, f"Alat dengan ID '{id_alat}' tidak ditemukan."
            if alat.get_status() == "Rusak/Perbaikan":
                return None, f"Alat '{id_alat}' sedang dalam perbaikan, tidak bisa disewa."

            bentrok, id_trx_bentrok = self.cek_bentrok_jadwal(id_alat, tgl_pinjam, tgl_kembali)
            if bentrok:
                return None, (f"Alat '{id_alat}' sudah dibooking pada rentang tanggal "
                              f"tersebut (bentrok dengan transaksi {id_trx_bentrok}).")
            alat_objs.append(alat)

        self._counter_transaksi += 1
        id_transaksi = f"TRX{self._counter_transaksi:04d}"

        if jenis == "reguler":
            trx = PeminjamanReguler(id_transaksi, nama_pelanggan, tgl_pinjam, tgl_kembali)
        elif jenis == "event":
            trx = PeminjamanPaketEvent(id_transaksi, nama_pelanggan, tgl_pinjam, tgl_kembali)
        else:
            return None, "Jenis transaksi tidak dikenali."

        for alat in alat_objs:
            trx.tambah_alat(alat)

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transaksi (id_transaksi, jenis, nama_pelanggan,
                                    tanggal_pinjam, tanggal_kembali_rencana)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_transaksi, trx.JENIS, nama_pelanggan, tgl_pinjam, tgl_kembali))

        for alat in alat_objs:
            cursor.execute(
                "INSERT INTO transaksi_alat (id_transaksi, id_alat) VALUES (%s, %s)",
                (id_transaksi, alat.get_id())
            )
            cursor.execute(
                "UPDATE alat SET status = 'Disewa' WHERE id_alat = %s", (alat.get_id(),)
            )
        self.conn.commit()
        cursor.close()

        return trx, None

    def ambil_semua_transaksi(self):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT id_transaksi, jenis, nama_pelanggan, tanggal_pinjam,
                                  tanggal_kembali_rencana, tanggal_kembali_aktual
                           FROM transaksi ORDER BY id_transaksi""")
        rows = cursor.fetchall()
        cursor.close()

        daftar_alat = self.ambil_semua_alat()
        hasil = {}
        for row in rows:
            (id_trx, jenis, nama_pelanggan, tgl_pinjam, tgl_kembali_rencana,
             tgl_kembali_aktual) = row

            cls = PeminjamanReguler if jenis == "reguler" else PeminjamanPaketEvent
            trx = cls(id_trx, nama_pelanggan, tgl_pinjam, tgl_kembali_rencana, tgl_kembali_aktual)

            cursor2 = self.conn.cursor()
            cursor2.execute("SELECT id_alat FROM transaksi_alat WHERE id_transaksi = %s", (id_trx,))
            for (id_alat,) in cursor2.fetchall():
                if id_alat in daftar_alat:
                    trx.daftar_alat.append(daftar_alat[id_alat])
            cursor2.close()

            hasil[id_trx] = trx
        return hasil

    def tampilkan_transaksi(self, hanya_pelanggan=None):
        daftar_transaksi = self.ambil_semua_transaksi()
        if hanya_pelanggan:
            daftar_transaksi = {k: v for k, v in daftar_transaksi.items()
                               if v.nama_pelanggan == hanya_pelanggan}
        if not daftar_transaksi:
            print("⚠️  Belum ada transaksi.")
            return
        print(f"\n{'ID Transaksi':<14}{'Jenis':<24}{'Pelanggan':<18}{'Status'}")
        print("-" * 70)
        for trx in daftar_transaksi.values():
            status = "Selesai" if trx.tanggal_kembali_aktual else "Berjalan"
            print(f"{trx.id_transaksi:<14}{trx.jenis_transaksi():<24}"
                  f"{trx.nama_pelanggan:<18}{status}")

    def kembalikan_alat(self, id_transaksi, tanggal_kembali_aktual):
        daftar_transaksi = self.ambil_semua_transaksi()
        trx = daftar_transaksi.get(id_transaksi)
        if trx is None:
            return None, "Transaksi tidak ditemukan."
        if trx.tanggal_kembali_aktual is not None:
            return None, "Transaksi ini sudah diselesaikan sebelumnya."

        trx.selesaikan(tanggal_kembali_aktual)

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE transaksi SET tanggal_kembali_aktual = %s WHERE id_transaksi = %s",
            (tanggal_kembali_aktual, id_transaksi)
        )
        for alat in trx.daftar_alat:
            cursor.execute(
                "UPDATE alat SET status = 'Tersedia' WHERE id_alat = %s", (alat.get_id(),)
            )
        self.conn.commit()
        cursor.close()

        return trx, None

    def login(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username, password, nama, role FROM users WHERE username = %s",
                      (username,))
        row = cursor.fetchone()
        cursor.close()
        if row and row[1] == password:
            return User(row[0], row[1], row[2], row[3])
        return None

    def daftar_user_baru(self, username, password, nama):
        if not username or not password or not nama:
            return False, "Semua kolom wajib diisi."
        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            return False, "Username sudah dipakai, coba username lain."
        cursor.execute(
            "INSERT INTO users (username, password, nama, role) VALUES (%s,%s,%s,%s)",
            (username, password, nama, "Pelanggan")
        )
        self.conn.commit()
        cursor.close()
        return True, None


# =====================================================================
# HELPER INPUT (dengan validasi & bisa dibatalkan dengan mengetik 'x')
# =====================================================================
class BatalInput(Exception):
    """Dilempar saat pengguna mengetik 'x' untuk batal di tengah input."""
    pass


def input_teks(prompt, wajib=True):
    while True:
        teks = input(f"{prompt} (ketik x untuk batal): ").strip()
        if teks.lower() == "x":
            raise BatalInput()
        if wajib and teks == "":
            print("⚠️  Kolom ini wajib diisi.")
            continue
        return teks


def input_tanggal(prompt):
    while True:
        teks = input(f"{prompt} [YYYY-MM-DD] (ketik x untuk batal): ").strip()
        if teks.lower() == "x":
            raise BatalInput()
        try:
            tahun, bulan, hari = map(int, teks.split("-"))
            return date(tahun, bulan, hari)
        except Exception:
            print("⚠️  Format tanggal salah. Contoh yang benar: 2026-08-20")


def input_angka(prompt, boleh_negatif=False):
    while True:
        teks = input(f"{prompt} (ketik x untuk batal): ").strip()
        if teks.lower() == "x":
            raise BatalInput()
        try:
            nilai = int(teks)
            if not boleh_negatif and nilai < 0:
                print("⚠️  Nilai tidak boleh negatif.")
                continue
            return nilai
        except ValueError:
            print("⚠️  Masukkan angka yang valid.")


# =====================================================================
# MENU CLI
# =====================================================================
def menu_admin(sistem: SistemPeminjaman):
    while True:
        bersihkan_layar()
        print("=" * 50)
        print("MENU ADMIN VENDOR".center(50))
        print("=" * 50)
        print("1. Tampilkan semua alat")
        print("2. Tambah alat baru")
        print("3. Ubah status alat")
        print("4. Tampilkan semua transaksi")
        print("5. Proses pengembalian alat")
        print("6. Logout")
        pilihan = input("\nPilih menu (1-6): ").strip()

        try:
            if pilihan == "1":
                sistem.tampilkan_alat()

            elif pilihan == "2":
                print("\nJenis alat: 1=Speaker  2=Mixer  3=Mikrofon  4=Kabel")
                jenis = input_teks("Pilih jenis alat (1-4)")
                id_alat = input_teks("ID Alat baru (unik)")
                merk = input_teks("Merk")
                harga = input_angka("Harga sewa per hari")

                if jenis == "1":
                    daya = input_angka("Daya (Watt)")
                    alat = KelasSpeaker(id_alat, merk, harga, daya_watt=daya)
                elif jenis == "2":
                    channel = input_angka("Jumlah channel")
                    alat = KelasMixer(id_alat, merk, harga, jumlah_channel=channel)
                elif jenis == "3":
                    tipe = input_teks("Tipe (Kabel/Wireless)")
                    alat = KelasMikrofon(id_alat, merk, harga, tipe=tipe)
                elif jenis == "4":
                    panjang = input_angka("Panjang (meter)")
                    alat = KelasKabel(id_alat, merk, harga, panjang_meter=panjang)
                else:
                    print("⚠️  Jenis tidak valid.")
                    tekan_enter_lanjut()
                    continue

                berhasil, err = sistem.tambah_alat(alat)
                print("✅ Alat berhasil ditambahkan!" if berhasil else f"❌ {err}")

            elif pilihan == "3":
                sistem.tampilkan_alat()
                id_alat = input_teks("\nID Alat yang mau diubah statusnya")
                print(f"Status valid: {AlatSound.STATUS_VALID}")
                status_baru = input_teks("Status baru")
                berhasil, err = sistem.ubah_status_alat(id_alat, status_baru)
                print("✅ Status alat berhasil diperbarui!" if berhasil else f"❌ {err}")

            elif pilihan == "4":
                sistem.tampilkan_transaksi()

            elif pilihan == "5":
                sistem.tampilkan_transaksi()
                id_trx = input_teks("\nID Transaksi yang mau diselesaikan")
                tgl_kembali_aktual = input_tanggal("Tanggal pengembalian aktual")
                trx, err = sistem.kembalikan_alat(id_trx, tgl_kembali_aktual)
                if err:
                    print(f"❌ {err}")
                else:
                    print("\n" + trx.cetak_nota())

            elif pilihan == "6":
                print("Logout dari akun Admin.")
                break
            else:
                print("⚠️  Pilihan tidak valid.")

        except BatalInput:
            print("↩️  Dibatalkan.")
        except (ValueError, Error) as e:
            print(f"❌ Terjadi kesalahan: {e}")

        tekan_enter_lanjut()


def menu_pelanggan(sistem: SistemPeminjaman, user: User):
    while True:
        bersihkan_layar()
        print("=" * 50)
        print(f"MENU PELANGGAN - {user.nama}".center(50))
        print("=" * 50)
        print("1. Lihat alat yang tersedia")
        print("2. Buat peminjaman baru")
        print("3. Lihat transaksi saya")
        print("4. Logout")
        pilihan = input("\nPilih menu (1-4): ").strip()

        try:
            if pilihan == "1":
                sistem.tampilkan_alat()

            elif pilihan == "2":
                sistem.tampilkan_alat()
                print("\nJenis transaksi: 1=Reguler  2=Paket Event (diskon 10%)")
                jenis_input = input_teks("Pilih jenis (1-2)")
                jenis = "reguler" if jenis_input == "1" else "event"

                ids_teks = input_teks("ID alat yang mau disewa (pisahkan koma, mis. A001,A003)")
                id_alat_list = [x.strip() for x in ids_teks.split(",") if x.strip()]

                tgl_pinjam = input_tanggal("Tanggal pinjam")
                tgl_kembali = input_tanggal("Tanggal kembali (rencana)")

                trx, err = sistem.buat_transaksi(
                    jenis, user.nama, id_alat_list, tgl_pinjam, tgl_kembali
                )
                if err:
                    print(f"❌ {err}")
                else:
                    print("✅ Transaksi berhasil dibuat!\n")
                    print(trx.cetak_nota())

            elif pilihan == "3":
                sistem.tampilkan_transaksi(hanya_pelanggan=user.nama)

            elif pilihan == "4":
                print("Logout dari akun Pelanggan.")
                break
            else:
                print("⚠️  Pilihan tidak valid.")

        except BatalInput:
            print("↩️  Dibatalkan.")
        except (ValueError, Error) as e:
            print(f"❌ Terjadi kesalahan: {e}")

        tekan_enter_lanjut()


def menu_login(sistem: SistemPeminjaman):
    while True:
        bersihkan_layar()
        print("=" * 50)
        print("SISTEM PEMINJAMAN SOUND SYSTEM".center(50))
        print("=" * 50)
        print("1. Login")
        print("2. Daftar akun pelanggan baru")
        print("3. Keluar")
        pilihan = input("\nPilih menu (1-3): ").strip()

        if pilihan == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user = sistem.login(username, password)
            if user is None:
                print("❌ Username atau password salah.")
                tekan_enter_lanjut()
                continue
            if user.role == "Admin":
                menu_admin(sistem)
            else:
                menu_pelanggan(sistem, user)

        elif pilihan == "2":
            try:
                username = input_teks("Buat username")
                password = input_teks("Buat password")
                nama = input_teks("Nama lengkap")
                berhasil, err = sistem.daftar_user_baru(username, password, nama)
                print("✅ Akun berhasil dibuat, silakan login." if berhasil else f"❌ {err}")
            except BatalInput:
                print("↩️  Dibatalkan.")
            tekan_enter_lanjut()

        elif pilihan == "3":
            print("Terima kasih telah menggunakan sistem ini!")
            break
        else:
            print("⚠️  Pilihan tidak valid.")
            tekan_enter_lanjut()


def main():
    cfg = muat_konfigurasi()
    print("🔧 Menyiapkan database...")
    siapkan_database(cfg)
    conn = buat_koneksi(cfg)
    sistem = SistemPeminjaman(conn)

    try:
        menu_login(sistem)
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh pengguna.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
