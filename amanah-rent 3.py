import psycopg2
from datetime import datetime, timedelta, date
import re

DB_HOST = "localhost"
DB_NAME = "Amanah_Rent__Bike_Bali"
DB_USER = "postgres"
DB_PASSWORD = "001"
DB_PORT = "5432"

conn = None
cursor = None

STATUS_PEMBAYARAN = ['Belum Bayar', 'Sudah Dikonfirmasi', 'Dikonfirmasi', 'Ditolak']

def connect_db():
    global conn, cursor
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("✅ Berhasil terhubung ke database PostgreSQL.")
    except psycopg2.Error as e:
        print(f"❌ Gagal terhubung ke database PostgreSQL: {e}")
        exit()

def close_db():
    global conn, cursor
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("👋 Koneksi database ditutup.")

def create_tables():
    # Perhatikan bahwa setiap pernyataan CREATE TABLE sekarang dijalankan secara terpisah
    # dan tidak lagi menggunakan executescript
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pelanggan (
        pelanggan_id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        nomor_telp TEXT NOT NULL,
        nama TEXT NOT NULL,
        password TEXT NOT NULL,
        asal_kota TEXT NOT NULL
    );""")
    conn.commit() # Commit setiap tabel dibuat

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        admin_id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipe_motor (
        tipe_motor_id TEXT PRIMARY KEY,
        tipe_merek TEXT NOT NULL
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS motor (
        motor_id TEXT PRIMARY KEY,
        nomor_polisi TEXT NOT NULL,
        tipe_motor_id TEXT NOT NULL,
        tahun INTEGER NOT NULL,
        harga_sewa INTEGER NOT NULL,
        status_ketersediaan BOOLEAN NOT NULL,
        FOREIGN KEY (tipe_motor_id) REFERENCES tipe_motor(tipe_motor_id)
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metode_pembayaran (
        metode_pembayaran_id SERIAL PRIMARY KEY,
        jenis_pembayaran TEXT NOT NULL,
        no_rekening_ewallet TEXT
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pesanan (
        pesanan_id SERIAL PRIMARY KEY,
        tanggal_pesan TEXT NOT NULL,
        lama_penyewaan INTEGER NOT NULL,
        tanggal_pengambilan TEXT NOT NULL,
        total INTEGER NOT NULL,
        nama_pemilik_rekening TEXT NOT NULL,
        status_pembayaran TEXT NOT NULL,
        motor_id TEXT NOT NULL,
        admin_id INTEGER NOT NULL,
        metode_pembayaran_id INTEGER NOT NULL,
        pelanggan_id INTEGER NOT NULL,
        FOREIGN KEY (motor_id) REFERENCES motor(motor_id),
        FOREIGN KEY (admin_id) REFERENCES admin(admin_id),
        FOREIGN KEY (metode_pembayaran_id) REFERENCES metode_pembayaran(metode_pembayaran_id),
        FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(pelanggan_id)
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fasilitas (
        fasilitas_id TEXT PRIMARY KEY,
        nama_barang TEXT NOT NULL,
        harga INTEGER NOT NULL
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detail_pesanan (
        detail_pesanan_id SERIAL PRIMARY KEY,
        pesanan_id INTEGER NOT NULL,
        fasilitas_id TEXT NOT NULL,
        FOREIGN KEY (pesanan_id) REFERENCES pesanan(pesanan_id),
        FOREIGN KEY (fasilitas_id) REFERENCES fasilitas(fasilitas_id)
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ulasan (
        ulasan_id SERIAL PRIMARY KEY,
        tanggal TEXT NOT NULL,
        ulasan TEXT NOT NULL,
        pesanan_id INTEGER NOT NULL,
        FOREIGN KEY (pesanan_id) REFERENCES pesanan(pesanan_id)
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pengembalian (
        pengembalian_id SERIAL PRIMARY KEY,
        tanggal_pengembalian TEXT NOT NULL,
        denda INTEGER,
        pesanan_id INTEGER NOT NULL,
        admin_id INTEGER NOT NULL,
        FOREIGN KEY (pesanan_id) REFERENCES pesanan(pesanan_id),
        FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
    );""")
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pengeluaran (
        pengeluaran_id SERIAL PRIMARY KEY,
        tanggal TEXT NOT NULL,
        jumlah INTEGER NOT NULL,
        deskripsi TEXT NOT NULL,
        motor_id TEXT,
        admin_id INTEGER NOT NULL,
        FOREIGN KEY (motor_id) REFERENCES motor(motor_id),
        FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
    );""")
    conn.commit()
    print("✅ Tabel berhasil dibuat atau sudah ada.")

def register_pelanggan():
    while True:
        username = input("Username: ")
        cursor.execute("SELECT username FROM pelanggan WHERE username = %s", (username,))
        if cursor.fetchone():
            print("❌ Username sudah ada. Gunakan username lain.")
        else:
            break
    email = input("Email: ")
    nomor_telp = input("Nomor Telepon: ")
    nama = input("Nama Lengkap: ")
    password = input("Password: ")
    asal_kota = input("Asal Kota: ")
    try:
        cursor.execute("""
        INSERT INTO pelanggan (username, email, nomor_telp, nama, password, asal_kota)
        VALUES (%s, %s, %s, %s, %s, %s)""", (username, email, nomor_telp, nama, password, asal_kota))
        conn.commit()
        print("✅ Pendaftaran berhasil! Silakan login.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Pendaftaran gagal: {e}")

def login_pelanggan():
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT * FROM pelanggan WHERE username = %s AND password = %s", (username, password))
    pelanggan = cursor.fetchone()
    if pelanggan:
        print("✅ Login pelanggan berhasil!")
        return pelanggan
    else:
        print("❌ Username atau password salah.")
        return None

def login_admin():
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
    admin = cursor.fetchone()
    if admin:
        print("✅ Login admin berhasil!")
        return admin
    else:
        print("❌ Username atau password salah.")
        return None

def tampilkan_motor():
    print("\n== Motor Tersedia ==")
    cursor.execute("""
    SELECT m.motor_id, t.tipe_merek, m.nomor_polisi, m.tahun, m.harga_sewa
    FROM motor m JOIN tipe_motor t ON m.tipe_motor_id = t.tipe_motor_id
    WHERE m.status_ketersediaan = TRUE
    ORDER BY m.motor_id ASC
    """)
    motors = cursor.fetchall()
    if not motors:
        print("Tidak ada motor yang tersedia saat ini.")
    else:
        for motor in motors:
            print(f"ID: {motor[0]} | Tipe: {motor[1]} | Nopol: {motor[2]} | Tahun: {motor[3]} | Harga Sewa/hari: Rp{motor[4]:,}")
    input("\nTekan Enter untuk melanjutkan...")

def pesan_motor(pelanggan_id):
    tampilkan_motor()
    motor_id = input("Masukkan ID Motor yang ingin disewa: ").upper().strip()
    
    cursor.execute("SELECT motor_id, harga_sewa, status_ketersediaan FROM motor WHERE motor_id = %s", (motor_id,))
    motor = cursor.fetchone()
    
    if not motor or not motor[2]:
        print("❌ Motor tidak ditemukan atau tidak tersedia.")
        return
    
    harga_sewa_per_hari = motor[1]

    while True:
        try:
            lama_penyewaan = int(input("Lama penyewaan (hari): "))
            if lama_penyewaan <= 0:
                print("❌ Lama penyewaan harus lebih dari 0 hari.")
            else:
                break
        except ValueError:
            print("❌ Input tidak valid. Masukkan angka untuk lama penyewaan.")
    
    while True:
        tanggal_pengambilan_str = input("Tanggal pengambilan (YYYY-MM-DD): ")
        try:
            tanggal_pengambilan = datetime.strptime(tanggal_pengambilan_str, "%Y-%m-%d").date()
            if tanggal_pengambilan < date.today():
                print("❌ Tanggal pengambilan tidak bisa di masa lalu.")
            else:
                break
        except ValueError:
            print("❌ Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
    
    total = harga_sewa_per_hari * lama_penyewaan

    selected_fasilitas = []
    cursor.execute("SELECT fasilitas_id, nama_barang, harga FROM fasilitas")
    fasilitas_list = cursor.fetchall()

    if fasilitas_list:
        print("\n== Fasilitas Tambahan (opsional) ==")
        for f_id, f_nama, f_harga in fasilitas_list:
            print(f"{f_id}. {f_nama} (Rp{f_harga:,} per pesanan)")
        
        while True:
            choice = input("Masukkan ID Fasilitas yang ingin ditambahkan (ketik 'selesai' jika sudah): ").strip().upper()
            if choice == 'SELESAI':
                break
            
            found_fasilitas = next((f for f in fasilitas_list if f[0].strip() == choice), None)
            
            if found_fasilitas:
                selected_fasilitas.append(found_fasilitas)
                total += found_fasilitas[2]
                print(f"✅ Fasilitas '{found_fasilitas[1]}' ditambahkan. Total sementara: Rp{total:,}")
            else:
                print("❌ ID Fasilitas tidak valid.")
    else:
        print("Tidak ada fasilitas tambahan yang tersedia.")

    print("\n== Pilih Metode Pembayaran ==")
    cursor.execute("SELECT metode_pembayaran_id, jenis_pembayaran, no_rekening_ewallet FROM metode_pembayaran")
    metode_pembayaran_list = cursor.fetchall()
    if not metode_pembayaran_list:
        print("❌ Belum ada metode pembayaran yang terdaftar.")
        return

    for metode in metode_pembayaran_list:
        rek_info = f" ({metode[2]})" if metode[2] else ""
        print(f"ID: {metode[0]} | Jenis: {metode[1]}{rek_info}")

    metode_pembayaran_id = input("Masukkan ID Metode Pembayaran: ").strip().upper()
    cursor.execute("SELECT 1 FROM metode_pembayaran WHERE metode_pembayaran_id = %s", (metode_pembayaran_id,))
    if not cursor.fetchone():
        print("❌ Metode pembayaran tidak valid.")
        return

    catatan = input("Catatan tambahan (opsional): ")
    
    tanggal_pesan = date.today()
    status_pembayaran = "Belum Bayar"

    try:
        cursor.execute("""
        INSERT INTO pesanan (pelanggan_id, motor_id, metode_pembayaran_id, tanggal_pesan, lama_penyewaan, tanggal_pengambilan, total, catatan, status_pembayaran)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING pesanan_id
        """, (pelanggan_id, motor_id, metode_pembayaran_id, tanggal_pesan, lama_penyewaan, tanggal_pengambilan, total, catatan, status_pembayaran))
        pesanan_id = cursor.fetchone()[0]
        
        for fas in selected_fasilitas:
            cursor.execute("""
            INSERT INTO detail_pesanan (pesanan_id, fasilitas_id)
            VALUES (%s, %s)
            """, (pesanan_id, fas[0]))
        
        cursor.execute("UPDATE motor SET status_ketersediaan = FALSE WHERE motor_id = %s", (motor_id,))
        
        conn.commit()
        print(f"✅ Pesanan berhasil dibuat! ID Pesanan Anda: {pesanan_id}. Total yang harus dibayar: Rp{total:,}. Silakan lakukan pembayaran.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Gagal membuat pesanan: {e}")

def lihat_pesanan_user(pelanggan_id):
    cursor.execute("""
    SELECT p.pesanan_id, m.motor_id, m.nomor_polisi, p.tanggal_pesan, p.status_pembayaran, p.total, p.lama_penyewaan, p.tanggal_pengambilan
    FROM pesanan p JOIN motor m ON p.motor_id = m.motor_id
    WHERE p.pelanggan_id = %s
    ORDER BY p.tanggal_pesan DESC
    """, (pelanggan_id,))
    data = cursor.fetchall()
    print("\n== Pesanan Anda ==")
    if not data:
        print("Belum ada pesanan.")
    else:
        for row in data:
            tanggal_pengambilan_raw = row[7]

            if isinstance(tanggal_pengambilan_raw, str):
                tanggal_pengambilan_obj = datetime.strptime(tanggal_pengambilan_raw, "%Y-%m-%d").date()
            elif isinstance(tanggal_pengambilan_raw, date):
                tanggal_pengambilan_obj = tanggal_pengambilan_raw
            else:
                print(f"Warning: Tipe data tanggal_pengambilan tidak dikenal: {type(tanggal_pengambilan_raw)}")
                tanggal_pengambilan_obj = None
                
            lama_penyewaan = row[6]
            tanggal_seharusnya_kembali = tanggal_pengambilan_obj + timedelta(days=lama_penyewaan) if tanggal_pengambilan_obj else "N/A"

            print(f"ID Pesanan: {row[0]} | Motor: {row[1]} - {row[2]} | Tanggal Pesan: {row[3]} | Tgl Ambil: {tanggal_pengambilan_obj.strftime('%Y-%m-%d') if tanggal_pengambilan_obj else 'N/A'} | Lama Sewa: {row[6]} hari | Seharusnya Kembali: {tanggal_seharusnya_kembali.strftime('%Y-%m-%d') if isinstance(tanggal_seharusnya_kembali, date) else tanggal_seharusnya_kembali} | Total: Rp{row[5]:,} | Status: {row[4]}")
            
            cursor.execute("""
                SELECT f.nama_barang, f.harga
                FROM detail_pesanan dp
                JOIN fasilitas f ON dp.fasilitas_id = f.fasilitas_id
                WHERE dp.pesanan_id = %s
            """, (row[0],))
            fasilitas_terkait = cursor.fetchall()
            if fasilitas_terkait:
                print("  Fasilitas Tambahan:")
                for fas_nama, fas_harga in fasilitas_terkait:
                    print(f"    - {fas_nama} (Rp{fas_harga:,})")
    input("\nTekan Enter untuk melanjutkan...")

def beri_ulasan(pelanggan_id):
    print("\n== Beri Ulasan ==")
    cursor.execute("""
    SELECT p.pesanan_id, m.nomor_polisi, p.tanggal_pesan, p.tanggal_pengambilan, p.lama_penyewaan
    FROM pesanan p
    JOIN motor m ON p.motor_id = m.motor_id
    LEFT JOIN ulasan u ON p.pesanan_id = u.pesanan_id
    WHERE p.pelanggan_id = %s AND p.status_pembayaran IN ('Sudah Dikonfirmasi', 'Dikonfirmasi') AND u.ulasan_id IS NULL
    ORDER BY p.tanggal_pesan DESC
    """, (pelanggan_id,))
    eligible_orders = cursor.fetchall()

    if not eligible_orders:
        print("Tidak ada pesanan yang memenuhi syarat untuk diulas atau semua sudah diulas.")
    else:
        print("Pesanan yang bisa diulas:")
        for order in eligible_orders:
            pesanan_id, nopol, tgl_pesan, tgl_ambil_raw, lama_sewa = order
            
            if isinstance(tgl_ambil_raw, str):
                tgl_ambil_obj = datetime.strptime(tgl_ambil_raw, "%Y-%m-%d").date()
            elif isinstance(tgl_ambil_raw, date):
                tgl_ambil_obj = tgl_ambil_raw
            else:
                tgl_ambil_obj = None

            tgl_seharusnya_kembali = tgl_ambil_obj + timedelta(days=lama_sewa) if tgl_ambil_obj else "N/A"
            print(f"ID Pesanan: {pesanan_id} | Motor: {nopol} | Tgl Pesan: {tgl_pesan} | Tgl Ambil: {tgl_ambil_obj.strftime('%Y-%m-%d') if tgl_ambil_obj else 'N/A'} | Seharusnya Kembali: {tgl_seharusnya_kembali.strftime('%Y-%m-%d') if isinstance(tgl_seharusnya_kembali, date) else tgl_seharusnya_kembali}")

        try:
            pesanan_id_ulasan = int(input("Masukkan ID Pesanan yang ingin Anda ulas: "))
        except ValueError:
            print("❌ ID Pesanan harus berupa angka.")
            input("\nTekan Enter untuk melanjutkan...")
            return

        cursor.execute("SELECT 1 FROM pesanan WHERE pesanan_id = %s AND pelanggan_id = %s", (pesanan_id_ulasan, pelanggan_id))
        if not cursor.fetchone():
            print("❌ ID Pesanan tidak valid atau bukan pesanan Anda.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        ulasan_text = input("Tulis ulasan Anda: ")
        tanggal_ulasan = date.today()

        try:
            cursor.execute("""
            INSERT INTO ulasan (pesanan_id, tanggal, ulasan)
            VALUES (%s, %s, %s)
            """, (pesanan_id_ulasan, tanggal_ulasan, ulasan_text))
            conn.commit()
            print("✅ Ulasan berhasil ditambahkan.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Gagal menambahkan ulasan: {e}")

    cursor.execute("""
    SELECT u.tanggal, u.ulasan, p.pesanan_id, m.nomor_polisi
    FROM ulasan u
    JOIN pesanan p ON u.pesanan_id = p.pesanan_id
    JOIN motor m ON p.motor_id = m.motor_id
    WHERE p.pelanggan_id = %s
    ORDER BY u.tanggal DESC LIMIT 5
    """, (pelanggan_id,))
    ulasan_terakhir = cursor.fetchall()
    if ulasan_terakhir:
        print("\n--- Ulasan Anda Sebelumnya ---")
        for ulasan_row in ulasan_terakhir:
            tanggal_raw = ulasan_row[0]
            if isinstance(tanggal_raw, str):
                tanggal_obj = datetime.strptime(tanggal_raw, "%Y-%m-%d").date()
            elif isinstance(tanggal_raw, date):
                tanggal_obj = ulasan_row[0]
            else:
                tanggal_obj = tanggal_raw
            print(f"Tanggal: {tanggal_obj.strftime('%Y-%m-%d')} | Motor: {ulasan_row[3]} | Ulasan: '{ulasan_row[1]}' (Pesanan ID: {ulasan_row[2]})")
    else:
        print("Anda belum memberikan ulasan.")
    input("\nTekan Enter untuk melanjutkan...")

def pelanggan_menu(pelanggan):
    while True:
        print("\n=== Menu Pelanggan ===")
        print("1. Tampilkan Motor Tersedia")
        print("2. Pesan Motor")
        print("3. Lihat Pesanan Anda")
        print("4. Beri Ulasan")
        print("0. Logout")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            tampilkan_motor()
        elif pilihan == "2":
            pesan_motor(pelanggan[0])
        elif pilihan == "3":
            lihat_pesanan_user(pelanggan[0])
        elif pilihan == "4":
            beri_ulasan(pelanggan[0])
        elif pilihan == "0":
            print("Logging out...")
            break
        else:
            print("❌ Pilihan tidak valid.")

def kelola_motor():
    while True:
        print("\n== Kelola Data Motor ==")
        print("1. Tambah Motor Baru")
        print("2. Lihat, Update, atau Hapus Motor")
        print("0. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            motor_id = input("ID Motor (misal: MTR001): ").upper().strip()
            cursor.execute("SELECT 1 FROM motor WHERE motor_id = %s", (motor_id,))
            if cursor.fetchone():
                print("❌ ID Motor sudah ada. Gunakan ID lain.")
                continue

            nomor_polisi = input("Nomor Polisi: ").upper().strip()
            cursor.execute("SELECT 1 FROM motor WHERE nomor_polisi = %s", (nomor_polisi,))
            if cursor.fetchone():
                print("❌ Nomor Polisi sudah ada. Gunakan Nomor Polisi lain.")
                continue

            cursor.execute("SELECT tipe_motor_id, tipe_merek FROM tipe_motor")
            tipe_motors = cursor.fetchall()
            if not tipe_motors:
                print("❌ Belum ada tipe motor yang terdaftar. Tambahkan tipe motor terlebih dahulu.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            print("\n== Pilih Tipe Motor ==")
            for tm_id, tm_merek in tipe_motors:
                print(f"ID: {tm_id} | Merek: {tm_merek}")
            
            tipe_motor_id = input("Masukkan ID Tipe Motor: ").upper().strip()
            cursor.execute("SELECT 1 FROM tipe_motor WHERE tipe_motor_id = %s", (tipe_motor_id,))
            if not cursor.fetchone():
                print("❌ ID Tipe Motor tidak valid.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            try:
                tahun = int(input("Tahun Pembuatan: "))
                harga_sewa = int(input("Harga Sewa per hari: "))
            except ValueError:
                print("❌ Input Tahun atau Harga Sewa tidak valid (harus angka).")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            try:
                cursor.execute("""
                INSERT INTO motor (motor_id, nomor_polisi, tipe_motor_id, tahun, harga_sewa, status_ketersediaan)
                VALUES (%s, %s, %s, %s, %s, TRUE)""", (motor_id, nomor_polisi, tipe_motor_id, tahun, harga_sewa))
                conn.commit()
                print("✅ Motor baru berhasil ditambahkan.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Gagal menambahkan motor: {e}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "2":
            print("\n== Daftar Motor ==")
            cursor.execute("""
            SELECT m.motor_id, t.tipe_merek, m.nomor_polisi, m.tahun, m.harga_sewa, m.status_ketersediaan
            FROM motor m JOIN tipe_motor t ON m.tipe_motor_id = t.tipe_motor_id
            ORDER BY m.motor_id ASC
            """)
            motors = cursor.fetchall()
            if not motors:
                print("Tidak ada motor yang terdaftar.")
            else:
                for motor in motors:
                    status = "Tersedia" if motor[5] else "Disewa"
                    print(f"ID: {motor[0]} | Tipe: {motor[1]} | Nopol: {motor[2]} | Tahun: {motor[3]} | Harga/hari: Rp{motor[4]:,} | Status: {status}")
            input("\nTekan Enter untuk melanjutkan...")
            
            sub_pilihan = input("\nApa yang ingin Anda lakukan? (U: Update, D: Hapus, L: Kembali ke menu utama kelola motor): ").upper().strip()
            if sub_pilihan == 'L':
                continue
            
            motor_id = input("Masukkan ID Motor yang ingin diubah/dihapus: ").upper().strip()
            cursor.execute("SELECT m.motor_id, t.tipe_merek, m.nomor_polisi, m.tahun, m.harga_sewa, m.status_ketersediaan FROM motor m JOIN tipe_motor t ON m.tipe_motor_id = t.tipe_motor_id WHERE m.motor_id = %s", (motor_id,))
            motor_found = cursor.fetchone()

            if not motor_found:
                print("❌ Motor tidak ditemukan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            if sub_pilihan == 'U':
                print(f"\n--- Update Motor ID: {motor_found[0]} ({motor_found[2]}) ---")
                print(f"Tipe Motor saat ini: {motor_found[1]}")
                print(f"Nomor Polisi saat ini: {motor_found[2]}")
                print(f"Tahun saat ini: {motor_found[3]}")
                print(f"Harga Sewa saat ini: Rp{motor_found[4]:,}")
                print(f"Status Ketersediaan saat ini: {'Tersedia' if motor_found[5] else 'Disewa'}")
                
                new_nopol = input(f"Nomor Polisi Baru (kosongkan jika tidak diubah, saat ini: {motor_found[2]}): ").upper().strip()
                new_tahun_str = input(f"Tahun Baru (kosongkan jika tidak diubah, saat ini: {motor_found[3]}): ").strip()
                new_harga_sewa_str = input(f"Harga Sewa Baru (kosongkan jika tidak diubah, saat ini: {motor_found[4]}): ").strip()
                new_status_str = input(f"Status Ketersediaan Baru (Tersedia/Disewa, kosongkan jika tidak diubah, saat ini: {'Tersedia' if motor_found[5] else 'Disewa'}): ").strip().lower()

                updates = []
                params = []

                if new_nopol:
                    cursor.execute("SELECT 1 FROM motor WHERE nomor_polisi = %s AND motor_id != %s", (new_nopol, motor_id))
                    if cursor.fetchone():
                        print("❌ Nomor Polisi baru sudah ada untuk motor lain. Update dibatalkan.")
                        input("\nTekan Enter untuk melanjutkan...")
                        continue
                    updates.append("nomor_polisi = %s")
                    params.append(new_nopol)
                
                if new_tahun_str:
                    try:
                        new_tahun = int(new_tahun_str)
                        updates.append("tahun = %s")
                        params.append(new_tahun)
                    except ValueError:
                        print("❌ Tahun tidak valid, harus angka. Update tahun dibatalkan.")
                        input("\nTekan Enter untuk melanjutkan...")
                        continue
                
                if new_harga_sewa_str:
                    try:
                        new_harga_sewa = int(new_harga_sewa_str)
                        updates.append("harga_sewa = %s")
                        params.append(new_harga_sewa)
                    except ValueError:
                        print("❌ Harga Sewa tidak valid, harus angka. Update harga sewa dibatalkan.")
                        input("\nTekan Enter untuk melanjutkan...")
                        continue
                
                if new_status_str:
                    if new_status_str == 'tersedia':
                        updates.append("status_ketersediaan = TRUE")
                    elif new_status_str == 'disewa':
                        updates.append("status_ketersediaan = FALSE")
                    else:
                        print("❌ Status tidak valid. Gunakan 'Tersedia' atau 'Disewa'. Update status dibatalkan.")
                        input("\nTekan Enter untuk melanjutkan...")
                        continue

                if updates:
                    try:
                        query = f"UPDATE motor SET {', '.join(updates)} WHERE motor_id = %s"
                        params.append(motor_id)
                        cursor.execute(query, tuple(params))
                        conn.commit()
                        print("✅ Motor berhasil diupdate.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal update motor: {e}")
                else:
                    print("Tidak ada perubahan yang dilakukan.")
                input("\nTekan Enter untuk melanjutkan...")
            elif sub_pilihan == 'D':
                konfirmasi = input(f"Anda yakin ingin menghapus motor {motor_found[0]} ({motor_found[2]})? (ya/tidak): ").lower().strip()
                if konfirmasi == 'ya':
                    try:
                        cursor.execute("SELECT 1 FROM pesanan WHERE motor_id = %s AND status_pembayaran IN ('Belum Bayar', 'Sudah Dikonfirmasi', 'Dikonfirmasi')", (motor_id,))
                        if cursor.fetchone():
                            print("❌ Motor ini tidak bisa dihapus karena masih terkait dengan pesanan aktif.")
                            input("\nTekan Enter untuk melanjutkan...")
                            continue
                            
                        cursor.execute("DELETE FROM detail_pesanan WHERE pesanan_id IN (SELECT pesanan_id FROM pesanan WHERE motor_id = %s)", (motor_id,))
                        cursor.execute("DELETE FROM pengembalian WHERE pesanan_id IN (SELECT pesanan_id FROM pesanan WHERE motor_id = %s)", (motor_id,))
                        cursor.execute("DELETE FROM pembayaran WHERE pesanan_id IN (SELECT pesanan_id FROM pesanan WHERE motor_id = %s)", (motor_id,))
                        cursor.execute("DELETE FROM ulasan WHERE pesanan_id IN (SELECT pesanan_id FROM pesanan WHERE motor_id = %s)", (motor_id,))
                        cursor.execute("UPDATE pengeluaran SET motor_id = NULL WHERE motor_id = %s", (motor_id,))
                        cursor.execute("DELETE FROM pesanan WHERE motor_id = %s", (motor_id,))
                        cursor.execute("DELETE FROM motor WHERE motor_id = %s", (motor_id,))
                        conn.commit()
                        print("✅ Motor berhasil dihapus (dan data terkait).")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal menghapus motor: {e}")
                else:
                    print("Penghapusan dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
            else:
                print("Pilihan tidak valid.")
                input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def kelola_tipe_motor():
    while True:
        print("\n== Kelola Data Tipe Motor ==")
        print("1. Tambah Tipe Motor Baru")
        print("2. Lihat, Update, atau Hapus Tipe Motor")
        print("0. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            tipe_motor_id = input("ID Tipe Motor (misal: TM001): ").upper().strip()
            cursor.execute("SELECT 1 FROM tipe_motor WHERE tipe_motor_id = %s", (tipe_motor_id,))
            if cursor.fetchone():
                print("❌ ID Tipe Motor sudah ada. Gunakan ID lain.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            tipe_merek = input("Nama Merek Tipe Motor: ").strip()
            try:
                cursor.execute("INSERT INTO tipe_motor (tipe_motor_id, tipe_merek) VALUES (%s, %s)", (tipe_motor_id, tipe_merek))
                conn.commit()
                print("✅ Tipe motor baru berhasil ditambahkan.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Gagal menambahkan tipe motor: {e}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "2":
            print("\n== Daftar Tipe Motor ==")
            cursor.execute("SELECT tipe_motor_id, tipe_merek FROM tipe_motor ORDER BY tipe_motor_id ASC")
            tipe_motors = cursor.fetchall()
            if not tipe_motors:
                print("Tidak ada tipe motor yang terdaftar.")
            else:
                for tm in tipe_motors:
                    print(f"ID: {tm[0]} | Merek: {tm[1]}")
            input("\nTekan Enter untuk melanjutkan...")
            
            sub_pilihan = input("\nApa yang ingin Anda lakukan? (U: Update, D: Hapus, L: Kembali ke menu utama kelola tipe motor): ").upper().strip()
            if sub_pilihan == 'L':
                continue
            
            tipe_motor_id = input("Masukkan ID Tipe Motor yang ingin diubah/dihapus: ").upper().strip()
            cursor.execute("SELECT tipe_motor_id, tipe_merek FROM tipe_motor WHERE tipe_motor_id = %s", (tipe_motor_id,))
            tipe_motor_found = cursor.fetchone()

            if not tipe_motor_found:
                print("❌ Tipe Motor tidak ditemukan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            if sub_pilihan == 'U':
                print(f"\n--- Update Tipe Motor ID: {tipe_motor_found[0]} ({tipe_motor_found[1]}) ---")
                new_tipe_merek = input(f"Nama Merek Baru (kosongkan jika tidak diubah, saat ini: {tipe_motor_found[1]}): ").strip()
                
                if new_tipe_merek:
                    try:
                        cursor.execute("UPDATE tipe_motor SET tipe_merek = %s WHERE tipe_motor_id = %s", (new_tipe_merek, tipe_motor_id))
                        conn.commit()
                        print("✅ Tipe motor berhasil diupdate.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal update tipe motor: {e}")
                else:
                    print("Tidak ada perubahan yang dilakukan.")
                input("\nTekan Enter untuk melanjutkan...")
            elif sub_pilihan == 'D':
                konfirmasi = input(f"Anda yakin ingin menghapus tipe motor {tipe_motor_found[0]} ({tipe_motor_found[1]})? (ya/tidak): ").lower().strip()
                if konfirmasi == 'ya':
                    try:
                        cursor.execute("SELECT 1 FROM motor WHERE tipe_motor_id = %s", (tipe_motor_id,))
                        if cursor.fetchone():
                            print("❌ Tipe motor ini tidak bisa dihapus karena masih terkait dengan data motor yang ada.")
                            print("Harap hapus atau ubah tipe motor pada motor yang terkait terlebih dahulu.")
                            input("\nTekan Enter untuk melanjutkan...")
                            continue

                        cursor.execute("DELETE FROM tipe_motor WHERE tipe_motor_id = %s", (tipe_motor_id,))
                        conn.commit()
                        print("✅ Tipe motor berhasil dihapus.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal menghapus tipe motor: {e}")
                else:
                    print("Penghapusan dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
            else:
                print("Pilihan tidak valid.")
                input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def kelola_fasilitas():
    while True:
        print("\n== Kelola Data Fasilitas ==")
        print("1. Tambah Fasilitas Baru")
        print("2. Lihat, Update, atau Hapus Fasilitas")
        print("0. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            fasilitas_id = input("ID Fasilitas (misal: F001): ").upper().strip()
            cursor.execute("SELECT 1 FROM fasilitas WHERE fasilitas_id = %s", (fasilitas_id,))
            if cursor.fetchone():
                print("❌ ID Fasilitas sudah ada. Gunakan ID lain.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            nama_barang = input("Nama Barang Fasilitas: ").strip()
            try:
                harga = int(input("Harga Fasilitas per pesanan: "))
            except ValueError:
                print("❌ Harga tidak valid (harus angka).")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            try:
                cursor.execute("INSERT INTO fasilitas (fasilitas_id, nama_barang, harga) VALUES (%s, %s, %s)", (fasilitas_id, nama_barang, harga))
                conn.commit()
                print("✅ Fasilitas baru berhasil ditambahkan.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Gagal menambahkan fasilitas: {e}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "2":
            print("\n== Daftar Fasilitas ==")
            cursor.execute("SELECT fasilitas_id, nama_barang, harga FROM fasilitas ORDER BY fasilitas_id ASC")
            fasilitas_list = cursor.fetchall()
            if not fasilitas_list:
                print("Tidak ada fasilitas yang terdaftar.")
            else:
                for f_id, f_nama, f_harga in fasilitas_list:
                    print(f"ID: {f_id} | Nama: {f_nama} | Harga: Rp{f_harga:,}")
            input("\nTekan Enter untuk melanjutkan...")
            
            sub_pilihan = input("\nApa yang ingin Anda lakukan? (U: Update, D: Hapus, L: Kembali ke menu utama kelola fasilitas): ").upper().strip()
            if sub_pilihan == 'L':
                continue

            fasilitas_id = input("Masukkan ID Fasilitas yang ingin diubah/dihapus: ").upper().strip()
            cursor.execute("SELECT fasilitas_id, nama_barang, harga FROM fasilitas WHERE fasilitas_id = %s", (fasilitas_id,))
            fasilitas_found = cursor.fetchone()

            if not fasilitas_found:
                print("❌ Fasilitas tidak ditemukan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            if sub_pilihan == 'U':
                print(f"\n--- Update Fasilitas ID: {fasilitas_found[0]} ({fasilitas_found[1]}) ---")
                new_nama_str = input(f"Nama Barang Baru (kosongkan jika tidak diubah, saat ini: {fasilitas_found[1]}): ").strip()
                new_harga_str = input(f"Harga Baru (kosongkan jika tidak diubah, saat ini: {fasilitas_found[2]}): ").strip()

                updates = []
                params = []

                if new_nama_str:
                    updates.append("nama_barang = %s")
                    params.append(new_nama_str)
                
                if new_harga_str:
                    try:
                        new_harga = int(new_harga_str)
                        updates.append("harga = %s")
                        params.append(new_harga)
                    except ValueError:
                        print("❌ Harga tidak valid, harus angka. Update harga dibatalkan.")
                        input("\nTekan Enter untuk melanjutkan...")
                        continue
                
                if updates:
                    try:
                        query = f"UPDATE fasilitas SET {', '.join(updates)} WHERE fasilitas_id = %s"
                        params.append(fasilitas_id)
                        cursor.execute(query, tuple(params))
                        conn.commit()
                        print("✅ Fasilitas berhasil diupdate.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal update fasilitas: {e}")
                else:
                    print("Tidak ada perubahan yang dilakukan.")
                input("\nTekan Enter untuk melanjutkan...")
            elif sub_pilihan == 'D':
                konfirmasi = input(f"Anda yakin ingin menghapus fasilitas {fasilitas_found[0]} ({fasilitas_found[1]})? (ya/tidak): ").lower().strip()
                if konfirmasi == 'ya':
                    try:
                        cursor.execute("SELECT 1 FROM detail_pesanan WHERE fasilitas_id = %s", (fasilitas_id,))
                        if cursor.fetchone():
                            print("❌ Fasilitas ini tidak bisa dihapus karena masih terkait dengan detail pesanan yang ada.")
                            input("\nTekan Enter untuk melanjutkan...")
                            continue

                        cursor.execute("DELETE FROM fasilitas WHERE fasilitas_id = %s", (fasilitas_id,))
                        conn.commit()
                        print("✅ Fasilitas berhasil dihapus.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal menghapus fasilitas: {e}")
                else:
                    print("Penghapusan dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
            else:
                print("Pilihan tidak valid.")
                input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def kelola_metode():
    while True:
        print("\n== Kelola Data Metode Pembayaran ==")
        print("1. Tambah Metode Pembayaran Baru")
        print("2. Lihat, Update, atau Hapus Metode Pembayaran")
        print("0. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            metode_id = input("ID Metode Pembayaran (misal: MP001): ").upper().strip()
            cursor.execute("SELECT 1 FROM metode_pembayaran WHERE metode_pembayaran_id = %s", (metode_id,))
            if cursor.fetchone():
                print("❌ ID Metode Pembayaran sudah ada. Gunakan ID lain.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            jenis_pembayaran = input("Jenis Pembayaran (misal: Transfer Bank, GoPay): ").strip()
            no_rekening_ewallet = input("Nomor Rekening/E-wallet (opsional, kosongkan jika tidak ada): ").strip()
            
            try:
                cursor.execute("INSERT INTO metode_pembayaran (metode_pembayaran_id, jenis_pembayaran, no_rekening_ewallet) VALUES (%s, %s, %s)", 
                               (metode_id, jenis_pembayaran, no_rekening_ewallet if no_rekening_ewallet else None))
                conn.commit()
                print("✅ Metode pembayaran baru berhasil ditambahkan.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Gagal menambahkan metode pembayaran: {e}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "2":
            print("\n== Daftar Metode Pembayaran ==")
            cursor.execute("SELECT metode_pembayaran_id, jenis_pembayaran, no_rekening_ewallet FROM metode_pembayaran ORDER BY metode_pembayaran_id ASC")
            metode_list = cursor.fetchall()
            if not metode_list:
                print("Tidak ada metode pembayaran yang terdaftar.")
            else:
                for m_id, m_jenis, m_rek in metode_list:
                    rek_info = f" ({m_rek})" if m_rek else ""
                    print(f"ID: {m_id} | Jenis: {m_jenis}{rek_info}")
            input("\nTekan Enter untuk melanjutkan...")

            sub_pilihan = input("\nApa yang ingin Anda lakukan? (U: Update, D: Hapus, L: Kembali ke menu utama kelola metode): ").upper().strip()
            if sub_pilihan == 'L':
                continue

            metode_id = input("Masukkan ID Metode Pembayaran yang ingin diubah/dihapus: ").upper().strip()
            cursor.execute("SELECT metode_pembayaran_id, jenis_pembayaran, no_rekening_ewallet FROM metode_pembayaran WHERE metode_pembayaran_id = %s", (metode_id,))
            metode_found = cursor.fetchone()

            if not metode_found:
                print("❌ Metode pembayaran tidak ditemukan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            if sub_pilihan == 'U':
                print(f"\n--- Update Metode Pembayaran ID: {metode_found[0]} ({metode_found[1]}) ---")
                new_jenis_str = input(f"Jenis Pembayaran Baru (kosongkan jika tidak diubah, saat ini: {metode_found[1]}): ").strip()
                new_rek_str = input(f"Nomor Rekening/E-wallet Baru (kosongkan jika tidak diubah, saat ini: {metode_found[2] if metode_found[2] else 'kosong'}): ").strip()

                updates = []
                params = []

                if new_jenis_str:
                    updates.append("jenis_pembayaran = %s")
                    params.append(new_jenis_str)
                
                updates.append("no_rekening_ewallet = %s")
                params.append(new_rek_str if new_rek_str else None)
                
                if updates:
                    try:
                        query = "UPDATE metode_pembayaran SET jenis_pembayaran = %s, no_rekening_ewallet = %s WHERE metode_pembayaran_id = %s"
                        cursor.execute(query, (new_jenis_str if new_jenis_str else metode_found[1], new_rek_str if new_rek_str else None, metode_id))
                        conn.commit()
                        print("✅ Metode pembayaran berhasil diupdate.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal update metode pembayaran: {e}")
                else:
                    print("Tidak ada perubahan yang dilakukan.")
                input("\nTekan Enter untuk melanjutkan...")
            elif sub_pilihan == 'D':
                konfirmasi = input(f"Anda yakin ingin menghapus metode pembayaran {metode_found[0]} ({metode_found[1]})? (ya/tidak): ").lower().strip()
                if konfirmasi == 'ya':
                    try:
                        cursor.execute("SELECT 1 FROM pesanan WHERE metode_pembayaran_id = %s", (metode_id,))
                        if cursor.fetchone():
                            print("❌ Metode pembayaran ini tidak bisa dihapus karena masih terkait dengan pesanan.")
                            input("\nTekan Enter untuk melanjutkan...")
                            continue
                        cursor.execute("SELECT 1 FROM pembayaran WHERE metode_pembayaran_id = %s", (metode_id,))
                        if cursor.fetchone():
                            print("❌ Metode pembayaran ini tidak bisa dihapus karena masih terkait dengan riwayat pembayaran.")
                            input("\nTekan Enter untuk melanjutkan...")
                            continue

                        cursor.execute("DELETE FROM metode_pembayaran WHERE metode_pembayaran_id = %s", (metode_id,))
                        conn.commit()
                        print("✅ Metode pembayaran berhasil dihapus.")
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Gagal menghapus metode pembayaran: {e}")
                else:
                    print("Penghapusan dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
            else:
                print("Pilihan tidak valid.")
                input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def tampilkan_pesanan():
    print("\n== Daftar Pesanan ==")
    cursor.execute("""
    SELECT p.pesanan_id, m.motor_id, m.nomor_polisi, c.nama, p.tanggal_pesan, p.status_pembayaran, p.total, p.lama_penyewaan, p.tanggal_pengambilan
    FROM pesanan p
    JOIN motor m ON p.motor_id = m.motor_id
    JOIN pelanggan c ON p.pelanggan_id = c.pelanggan_id
    ORDER BY p.tanggal_pesan DESC
    """)
    rows = cursor.fetchall()
    if not rows:
        print("Belum ada pesanan.")
    else:
        for row in rows:
            tanggal_pengambilan_raw = row[8] 

            if isinstance(tanggal_pengambilan_raw, str):
                tanggal_pengambilan_obj = datetime.strptime(tanggal_pengambilan_raw, "%Y-%m-%d").date()
            elif isinstance(tanggal_pengambilan_raw, date):
                tanggal_pengambilan_obj = tanggal_pengambilan_raw
            else:
                tanggal_pengambilan_obj = None

            lama_penyewaan = row[7]
            tanggal_seharusnya_kembali = tanggal_pengambilan_obj + timedelta(days=lama_penyewaan) if tanggal_pengambilan_obj else "N/A"

            print(f"ID Pesanan: {row[0]} | Motor: {row[1]} - {row[2]} | Pelanggan: {row[3]} | Tanggal Pesan: {row[4]} | Lama Sewa: {row[7]} hari | Tanggal Ambil: {tanggal_pengambilan_obj.strftime('%Y-%m-%d') if tanggal_pengambilan_obj else 'N/A'} | Seharusnya Kembali: {tanggal_seharusnya_kembali.strftime('%Y-%m-%d') if isinstance(tanggal_seharusnya_kembali, date) else tanggal_seharusnya_kembali} | Total: Rp{row[6]:,} | Status: {row[5]}")

            cursor.execute("""
                SELECT f.nama_barang, f.harga
                FROM detail_pesanan dp
                JOIN fasilitas f ON dp.fasilitas_id = f.fasilitas_id
                WHERE dp.pesanan_id = %s
            """, (row[0],))
            fasilitas_terkait = cursor.fetchall()
            if fasilitas_terkait:
                print("  Fasilitas Tambahan:")
                for fas_nama, fas_harga in fasilitas_terkait:
                    print(f"    - {fas_nama} (Rp{fas_harga:,})")
    input("\nTekan Enter untuk melanjutkan...")

def konfirmasi_pembayaran(admin_id):
    while True:
        print("\n== Konfirmasi Pembayaran ==")
        cursor.execute("""
        SELECT p.pesanan_id, c.nama AS pelanggan_nama, m.nomor_polisi, p.total, p.status_pembayaran
        FROM pesanan p
        JOIN pelanggan c ON p.pelanggan_id = c.pelanggan_id
        JOIN motor m ON p.motor_id = m.motor_id
        WHERE p.status_pembayaran IN ('Belum Bayar', 'Sudah Dikonfirmasi')
        ORDER BY p.tanggal_pesan ASC
        """)
        pesanan_pending = cursor.fetchall()

        if not pesanan_pending:
            print("Tidak ada pesanan yang perlu dikonfirmasi saat ini.")
            input("\nTekan Enter untuk melanjutkan...")
            break
        
        print("Pesanan yang menunggu konfirmasi/verifikasi:")
        for pesanan_row in pesanan_pending:
            print(f"ID Pesanan: {pesanan_row[0]} | Pelanggan: {pesanan_row[1]} | Motor: {pesanan_row[2]} | Total: Rp{pesanan_row[3]:,} | Status: {pesanan_row[4]}")
        input("\nTekan Enter untuk melanjutkan...")

        try:
            pesanan_id = int(input("Masukkan ID Pesanan yang akan dikonfirmasi/ditolak (0 untuk kembali): "))
            if pesanan_id == 0:
                break
        except ValueError:
            print("❌ ID Pesanan harus berupa angka.")
            continue
        
        cursor.execute("SELECT status_pembayaran FROM pesanan WHERE pesanan_id = %s", (pesanan_id,))
        current_status_row = cursor.fetchone()
        
        if not current_status_row:
            print("❌ Pesanan tidak ditemukan.")
            continue
        
        current_status = current_status_row[0]
        if current_status not in ['Belum Bayar', 'Sudah Dikonfirmasi']:
            print(f"❌ Status pesanan saat ini adalah '{current_status}', tidak perlu dikonfirmasi/ditolak.")
            continue

        konfirmasi_pilihan = input("Konfirmasi (K: Dikonfirmasi, D: Ditolak, B: Kembali): ").upper().strip()

        if konfirmasi_pilihan == 'K':
            new_status = 'Dikonfirmasi'
        elif konfirmasi_pilihan == 'D':
            new_status = 'Ditolak'
        elif konfirmasi_pilihan == 'B':
            continue
        else:
            print("❌ Pilihan tidak valid.")
            continue
        
        try:
            cursor.execute("UPDATE pesanan SET status_pembayaran = %s WHERE pesanan_id = %s", (new_status, pesanan_id))
            
            if new_status == 'Dikonfirmasi':
                cursor.execute("SELECT total, metode_pembayaran_id FROM pesanan WHERE pesanan_id = %s", (pesanan_id,))
                pesanan_info = cursor.fetchone()
                if pesanan_info:
                    total_pembayaran = pesanan_info[0]
                    metode_pembayaran_id = pesanan_info[1]
                    tanggal_pembayaran = date.today()
                    status_pembayaran = 'Berhasil'

                    cursor.execute("""
                    INSERT INTO pembayaran (pesanan_id, tanggal_pembayaran, jumlah_pembayaran, metode_pembayaran_id, status)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (pesanan_id, tanggal_pembayaran, total_pembayaran, metode_pembayaran_id, status_pembayaran))
                print("✅ Pembayaran berhasil dikonfirmasi dan dicatat.")
            elif new_status == 'Ditolak':
                cursor.execute("SELECT motor_id FROM pesanan WHERE pesanan_id = %s", (pesanan_id,))
                motor_id = cursor.fetchone()[0]
                cursor.execute("UPDATE motor SET status_ketersediaan = TRUE WHERE motor_id = %s", (motor_id,))
                print("✅ Pembayaran ditolak dan status motor dikembalikan.")
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Gagal update status pembayaran: {e}")
        input("\nTekan Enter untuk melanjutkan...")

def kelola_pengeluaran(admin_id):
    while True:
        print("\n== Kelola Pengeluaran ==")
        print("1. Tambah Pengeluaran Baru")
        print("2. Lihat Riwayat Pengeluaran")
        print("0. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            tanggal_str = input("Tanggal Pengeluaran (YYYY-MM-DD): ")
            try:
                tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            try:
                jumlah = int(input("Jumlah Pengeluaran: "))
                if jumlah <= 0:
                    print("❌ Jumlah pengeluaran harus lebih dari 0.")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
            except ValueError:
                print("❌ Jumlah tidak valid (harus angka).")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            deskripsi = input("Deskripsi Pengeluaran: ").strip()
            
            motor_terkait = input("Apakah pengeluaran ini terkait dengan motor tertentu? (ya/tidak): ").lower().strip()
            motor_id_terkait = None
            if motor_terkait == 'ya':
                tampilkan_motor()
                motor_id_input = input("Masukkan ID Motor yang terkait (kosongkan jika tidak ada): ").upper().strip()
                if motor_id_input:
                    cursor.execute("SELECT 1 FROM motor WHERE motor_id = %s", (motor_id_input,))
                    if cursor.fetchone():
                        motor_id_terkait = motor_id_input
                    else:
                        print("❌ ID Motor tidak ditemukan. Pengeluaran tidak akan dikaitkan dengan motor.")
                        input("\nTekan Enter untuk melanjutkan...")
            
            try:
                cursor.execute("""
                INSERT INTO pengeluaran (tanggal, jumlah, deskripsi, motor_id, admin_id)
                VALUES (%s, %s, %s, %s, %s)
                """, (tanggal, jumlah, deskripsi, motor_id_terkait, admin_id))
                conn.commit()
                print("✅ Pengeluaran berhasil dicatat.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Gagal mencatat pengeluaran: {e}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "2":
            print("\n== Riwayat Pengeluaran ==")
            cursor.execute("""
            SELECT pg.pengeluaran_id, pg.tanggal, pg.jumlah, pg.deskripsi, COALESCE(m.nomor_polisi, 'N/A') AS nomor_polisi, a.username
            FROM pengeluaran pg
            LEFT JOIN motor m ON pg.motor_id = m.motor_id
            JOIN admin a ON pg.admin_id = a.admin_id
            ORDER BY pg.tanggal DESC
            """)
            rows = cursor.fetchall()
            if not rows:
                print("Belum ada riwayat pengeluaran.")
            else:
                for row in rows:
                    tanggal_raw = row[1]
                    if isinstance(tanggal_raw, str):
                        tanggal_obj = datetime.strptime(tanggal_raw, "%Y-%m-%d").date()
                    elif isinstance(tanggal_raw, date):
                        tanggal_obj = tanggal_raw
                    else:
                        tanggal_obj = tanggal_raw
                    print(f"ID: {row[0]} | Tanggal: {tanggal_obj.strftime('%Y-%m-%d')} | Jumlah: Rp{row[2]:,} | Deskripsi: {row[3]} | Motor: {row[4]} | Admin: {row[5]}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def kelola_pengembalian(admin_id):
    while True:
        print("\n== Input & Lihat Pengembalian ==")
        print("1. Input Pengembalian")
        print("2. Lihat Riwayat Pengembalian")
        print("0. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            cursor.execute("""
                SELECT p.pesanan_id, m.nomor_polisi, c.nama, p.tanggal_pengambilan, p.lama_penyewaan, p.total, p.status_pembayaran
                FROM pesanan p
                JOIN motor m ON p.motor_id = m.motor_id
                JOIN pelanggan c ON p.pelanggan_id = c.pelanggan_id
                LEFT JOIN pengembalian pg ON p.pesanan_id = pg.pesanan_id
                WHERE (p.status_pembayaran = 'Sudah Dikonfirmasi' OR p.status_pembayaran = 'Dikonfirmasi')
                AND pg.pengembalian_id IS NULL
                ORDER BY p.tanggal_pengambilan ASC
            """)
            active_orders = cursor.fetchall()
            
            print("\n== Pesanan Aktif untuk Pengembalian ==")
            if not active_orders:
                print("Tidak ada pesanan aktif yang perlu dikembalikan.")
            else:
                for order in active_orders:
                    pesanan_id, nopol, nama_pelanggan, tgl_ambil_raw, lama_sewa, total_sewa, status_bayar = order
                    
                    if isinstance(tgl_ambil_raw, str):
                        tgl_ambil_obj = datetime.strptime(tgl_ambil_raw, "%Y-%m-%d").date()
                    elif isinstance(tgl_ambil_raw, date):
                        tgl_ambil_obj = tgl_ambil_raw
                    else:
                        print(f"Warning: Tipe data tanggal_pengambilan di pesanan aktif tidak dikenal: {type(tgl_ambil_raw)}")
                        tgl_ambil_obj = None
                        continue

                    tgl_seharusnya_kembali = tgl_ambil_obj + timedelta(days=lama_sewa)
                    print(f"ID Pesanan: {pesanan_id} | Motor: {nopol} | Pelanggan: {nama_pelanggan} | Tgl Ambil: {tgl_ambil_obj.strftime('%Y-%m-%d')} | Lama Sewa: {lama_sewa} hari | Seharusnya Kembali: {tgl_seharusnya_kembali.strftime('%Y-%m-%d')} | Total Sewa: Rp{total_sewa:,} | Status Pembayaran: {status_bayar}")
            input("\nTekan Enter untuk melanjutkan...")
            
            try:
                pesanan_id = int(input("Masukkan ID Pesanan yang dikembalikan: "))
            except ValueError:
                print("❌ ID Pesanan harus angka.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            cursor.execute("SELECT tanggal_pengambilan, lama_penyewaan, motor_id FROM pesanan WHERE pesanan_id = %s", (pesanan_id,))
            order_details = cursor.fetchone()
            
            if not order_details:
                print("❌ Pesanan tidak ditemukan atau tidak aktif untuk pengembalian.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            tanggal_pengambilan_raw_db, lama_penyewaan, motor_id = order_details
            
            cursor.execute("SELECT 1 FROM pengembalian WHERE pesanan_id = %s", (pesanan_id,))
            if cursor.fetchone():
                print("❌ Pesanan ini sudah dicatat pengembaliannya.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            tanggal_pengembalian_input_str = input("Tanggal Pengembalian Aktual (YYYY-MM-DD): ")
            try:
                tanggal_pengembalian_aktual = datetime.strptime(tanggal_pengembalian_input_str, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            if isinstance(tanggal_pengambilan_raw_db, str):
                tanggal_pengambilan_obj_db = datetime.strptime(tanggal_pengambilan_raw_db, "%Y-%m-%d").date()
            elif isinstance(tanggal_pengambilan_raw_db, date):
                tanggal_pengambilan_obj_db = tanggal_pengambilan_raw_db
            else:
                print(f"Warning: Tipe data tanggal_pengambilan dari DB untuk perhitungan denda tidak dikenal: {type(tanggal_pengambilan_raw_db)}")
                input("\nTekan Enter untuk melanjutkan...")
                continue


            tanggal_seharusnya_kembali = tanggal_pengambilan_obj_db + timedelta(days=lama_penyewaan)
            
            denda = 0
            if tanggal_pengembalian_aktual > tanggal_seharusnya_kembali:
                selisih_hari = (tanggal_pengembalian_aktual - tanggal_seharusnya_kembali).days
                cursor.execute("SELECT harga_sewa FROM motor WHERE motor_id = %s", (motor_id,))
                harga_sewa_per_hari = cursor.fetchone()[0]
                denda = selisih_hari * harga_sewa_per_hari
                print(f"❗ Motor terlambat dikembalikan {selisih_hari} hari. Denda: Rp{denda:,}")
            else:
                print("✅ Motor dikembalikan tepat waktu atau lebih awal.")
            
            try:
                cursor.execute("""
                INSERT INTO pengembalian(tanggal_pengembalian, denda, pesanan_id, admin_id)
                VALUES (%s, %s, %s, %s)""", (tanggal_pengembalian_input_str, denda, pesanan_id, admin_id))
                conn.commit()
                
                cursor.execute("UPDATE motor SET status_ketersediaan = TRUE WHERE motor_id = %s", (motor_id,))
                conn.commit()
                print("✅ Pengembalian berhasil dicatat dan status motor diperbarui.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Gagal mencatat pengembalian: {e}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "2":
            cursor.execute("""
            SELECT pg.pengembalian_id, p.pesanan_id, m.nomor_polisi, c.nama, pg.tanggal_pengembalian, pg.denda, a.username
            FROM pengembalian pg
            JOIN pesanan p ON pg.pesanan_id = p.pesanan_id
            JOIN motor m ON p.motor_id = m.motor_id
            JOIN pelanggan c ON p.pelanggan_id = c.pelanggan_id
            JOIN admin a ON pg.admin_id = a.admin_id
            ORDER BY pg.tanggal_pengembalian DESC
            """)
            rows = cursor.fetchall()
            print("\n--- Riwayat Pengembalian ---")
            if not rows:
                print("Belum ada riwayat pengembalian.")
            else:
                for row in rows:
                    tanggal_pengembalian_raw = row[4]

                    if isinstance(tanggal_pengembalian_raw, str):
                        tanggal_pengembalian_obj = datetime.strptime(tanggal_pengembalian_raw, "%Y-%m-%d").date()
                    elif isinstance(tanggal_pengembalian_raw, date):
                        tanggal_pengembalian_obj = tanggal_pengembalian_raw
                    else:
                        print(f"Warning: Tipe data tanggal_pengembalian di riwayat pengembalian tidak dikenal: {type(tanggal_pengembalian_raw)}")
                        tanggal_pengembalian_obj = None
                        continue

                    print(f"ID Pengembalian: {row[0]} | ID Pesanan: {row[1]} | Motor: {row[2]} | Pelanggan: {row[3]} | Tgl Kembali: {tanggal_pengembalian_obj.strftime('%Y-%m-%d')} | Denda: Rp{row[5]:,} | Admin: {row[6]}")
            input("\nTekan Enter untuk melanjutkan...")
        elif pilihan == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def laporan():
    while True:
        print("\n== Laporan Penyewaan ==")
        print("1. Total Pendapatan dari Pesanan (Dikonfirmasi)")
        print("2. Total Pengeluaran")
        print("3. Net Profit (Pendapatan - Pengeluaran)")
        print("4. Motor Paling Sering Disewa")
        print("5. Jumlah Pesanan per Status")
        print("6. Ulasan Terbaru")
        print("0. Kembali")
        p = input("Pilih: ")
        if p == "1":
            cursor.execute("SELECT SUM(total) FROM pesanan WHERE status_pembayaran IN ('Sudah Dikonfirmasi', 'Dikonfirmasi')")
            result_pesanan = cursor.fetchone()
            total_pesanan = result_pesanan[0] if result_pesanan and result_pesanan[0] is not None else 0

            cursor.execute("SELECT SUM(denda) FROM pengembalian")
            result_denda = cursor.fetchone()
            total_denda = result_denda[0] if result_denda and result_denda[0] is not None else 0
            
            total_pendapatan = total_pesanan + total_denda
            print(f"Total pendapatan dari pesanan yang sudah dikonfirmasi (termasuk denda): Rp{total_pendapatan:,}")
            input("\nTekan Enter untuk melanjutkan...")
        elif p == "2":
            cursor.execute("SELECT SUM(jumlah) FROM pengeluaran")
            result_pengeluaran = cursor.fetchone()
            hasil = result_pengeluaran[0] if result_pengeluaran and result_pengeluaran[0] is not None else 0
            print(f"Total Pengeluaran: Rp{hasil:,}")
            input("\nTekan Enter untuk melanjutkan...")
        elif p == "3":
            cursor.execute("SELECT SUM(total) FROM pesanan WHERE status_pembayaran IN ('Sudah Dikonfirmasi', 'Dikonfirmasi')")
            result_pendapatan_pesanan = cursor.fetchone()
            total_pendapatan_pesanan = result_pendapatan_pesanan[0] if result_pendapatan_pesanan and result_pendapatan_pesanan[0] is not None else 0

            cursor.execute("SELECT SUM(denda) FROM pengembalian")
            result_pendapatan_denda = cursor.fetchone()
            total_pendapatan_denda = result_pendapatan_denda[0] if result_pendapatan_denda and result_pendapatan_denda[0] is not None else 0
            
            total_pendapatan_bersih = total_pendapatan_pesanan + total_pendapatan_denda

            cursor.execute("SELECT SUM(jumlah) FROM pengeluaran")
            result_total_pengeluaran = cursor.fetchone()
            total_pengeluaran = result_total_pengeluaran[0] if result_total_pengeluaran and result_total_pengeluaran[0] is not None else 0

            net_profit = total_pendapatan_bersih - total_pengeluaran
            print(f"Net Profit: Rp{net_profit:,}")
            input("\nTekan Enter untuk melanjutkan...")
        elif p == "4":
            cursor.execute("""
            SELECT m.motor_id, t.tipe_merek, COUNT(*) as total_disewa
            FROM pesanan p
            JOIN motor m ON p.motor_id = m.motor_id
            JOIN tipe_motor t ON m.tipe_motor_id = t.tipe_motor_id
            GROUP BY m.motor_id, t.tipe_merek
            ORDER BY total_disewa DESC LIMIT 5
            """)
            data = cursor.fetchall()
            print("\n--- Motor Paling Sering Disewa ---")
            if data:
                for rank, (motor_id, tipe_merek, total_disewa) in enumerate(data, 1):
                    print(f"{rank}. Motor ID: {motor_id} | Tipe: {tipe_merek} ({total_disewa}x disewa)")
            else:
                print("Belum ada data penyewaan.")
            input("\nTekan Enter untuk melanjutkan...")
        elif p == "5":
            cursor.execute("SELECT status_pembayaran, COUNT(*) FROM pesanan GROUP BY status_pembayaran")
            rows = cursor.fetchall()
            print("\n--- Jumlah Pesanan per Status ---")
            if not rows:
                print("Belum ada pesanan.")
            else:
                for row in rows:
                    print(f"{row[0]}: {row[1]} pesanan")
            input("\nTekan Enter untuk melanjutkan...")
        elif p == "6":
            cursor.execute("""
            SELECT u.tanggal, u.ulasan, p.pesanan_id, c.nama, m.nomor_polisi
            FROM ulasan u
            JOIN pesanan p ON u.pesanan_id = p.pesanan_id
            JOIN pelanggan c ON p.pelanggan_id = c.pelanggan_id
            JOIN motor m ON p.motor_id = m.motor_id
            ORDER BY u.tanggal DESC LIMIT 5
            """)
            rows = cursor.fetchall()
            print("\n--- Ulasan Terbaru ---")
            if not rows:
                print("Belum ada ulasan.")
            else:
                for row in rows:
                    tanggal_raw = row[0]
                    if isinstance(tanggal_raw, str):
                        tanggal_obj = datetime.strptime(tanggal_raw, "%Y-%m-%d").date()
                    elif isinstance(tanggal_raw, date):
                        tanggal_obj = tanggal_raw
                    else:
                        tanggal_obj = tanggal_raw

                    print(f"Tanggal: {tanggal_obj.strftime('%Y-%m-%d')} | Pelanggan: {row[3]} | Motor: {row[4]} | Ulasan: '{row[1]}' (Pesanan ID: {row[2]})")
            input("\nTekan Enter untuk melanjutkan...")
        elif p == "0":
            break
        else:
            print("❌ Pilihan tidak valid.")

def admin_menu(admin):
    while True:
        print(f"\n=== Selamat Datang, Admin {admin[1]} ===")
        print("1. Kelola Data Motor")
        print("2. Kelola Data Tipe Motor")
        print("3. Kelola Data Fasilitas")
        print("4. Kelola Data Metode Pembayaran")
        print("5. Lihat Semua Pesanan")
        print("6. Konfirmasi Pembayaran")
        print("7. Kelola Pengeluaran")
        print("8. Kelola Pengembalian")
        print("9. Laporan Penyewaan")
        print("0. Logout")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            kelola_motor()
        elif pilihan == "2":
            kelola_tipe_motor()
        elif pilihan == "3":
            kelola_fasilitas()
        elif pilihan == "4":
            kelola_metode()
        elif pilihan == "5":
            tampilkan_pesanan()
        elif pilihan == "6":
            konfirmasi_pembayaran(admin[0])
        elif pilihan == "7":
            kelola_pengeluaran(admin[0])
        elif pilihan == "8":
            kelola_pengembalian(admin[0])
        elif pilihan == "9":
            laporan()
        elif pilihan == "0":
            print("Logging out...")
            break
        else:
            print("❌ Pilihan tidak valid.")

def main():
    connect_db()
    create_tables()
    cursor.execute("SELECT 1 FROM admin WHERE username = 'admin'")
    if not cursor.fetchone():
        try:
            cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", ('admin', 'admin123'))
            conn.commit()
            print("Admin default (username: admin, password: admin123) ditambahkan.")
        except Exception as e:
            conn.rollback()
            print(f"Gagal menambahkan admin default: {e}")

    while True:
        print("\n=== Amanah Rent Bike Bali ===")
        print("1. Login Pelanggan")
        print("2. Daftar Pelanggan")
        print("3. Login Admin")
        print("0. Keluar")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            pelanggan = login_pelanggan()
            if pelanggan:
                pelanggan_menu(pelanggan)
        elif pilihan == "2":
            register_pelanggan()
        elif pilihan == "3":
            admin = login_admin()
            if admin:
                admin_menu(admin)
        elif pilihan == "0":
            print("Terima kasih telah menggunakan layanan Amanah Rent Bike Bali.")
            break
        else:
            print("❌ Pilihan tidak valid.")
    
    close_db()

if __name__ == "__main__":
    main()
