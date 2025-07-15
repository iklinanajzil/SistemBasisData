-- 1. Membuat DATABASE AMANAH _RENT_BALI 
CREATE DATABASE "Amanah_Rent_Bike_Bali" 
ulasan_id INTEGER No Primary Key No 
tanggal DATETIME No - No 
ulasan TEXT No -  No 
pesanan_id INTEGER No Foreign Key No 
METODE_PEMBAYARAN 
Nama Kolom Type Null Key Default 
metode_id INTEGER No Primary Key No 
jenis_pembayaran VARCHAR(30) No - No 
no_rekening_ewallet INTEGER Yes - No 
WITH 
OWNER = postgres 
ENCODING = 'UTF8' 
LOCALE_PROVIDER = 'libc' 
CONNECTION LIMIT = -1 
IS_TEMPLATE = False; 

-- 2. MEMBUAT TABEL PELANGGAN 
CREATE TABLE pelanggan (  
pelanggan_id SERIAL PRIMARY KEY,  
username VARCHAR(20) NOT NULL, 
email VARCHAR(50) NOT NULL, 
nomor_telp VARCHAR (13) NOT NULL, 
nama VARCHAR(30) NOT NULL, 
password VARCHAR(20) NOT NULL,  
asal_kota VARCHAR(30) NOT NULL  
); 

-- 3. MEMBUAT TABEL TIPE_MOTOR 
CREATE TABLE tipe_motor( 
tipe_motor_id CHAR(6) PRIMARY KEY, 
tipe_merek VARCHAR(30) NOT NULL 
); 

-- 4. MEMBUAT TABEL MOTOR 
CREATE TABLE motor( 
motor_id CHAR(6) PRIMARY KEY, 
nomor_polisi VARCHAR(11) NOT NULL, 
tipe_motor_id CHAR(6) NOT NULL, 
CONSTRAINT tipe_motor_fk FOREIGN KEY(tipe_motor_id) 
REFERENCES tipe_motor(tipe_motor_id), 
tahun INTEGER NOT NULL, 
harga_sewa INTEGER NOT NULL, 
status_ketersediaan BOOLEAN NOT NULL 
); 

-- 5. MEMBUAT TABEL ADMIN 
CREATE TABLE admin( 
admin_id INTEGER PRIMARY KEY, 
username VARCHAR(20) NOT NULL, 
password VARCHAR(20) NOT NULL 
); 

-- 6. MEMBUAT TABEL METODE_PEMBAYARAN 
CREATE TABLE metode_pembayaran( 
metode_pembayaran_id SERIAL PRIMARY KEY, 
jenis_pembayaran VARCHAR(30) NOT NULL, 
no_rekening_ewallet INTEGER NULL 
); 

-- 7. MEMBUAT TYPE STATUS PEMBAYARAN 
CREATE TYPE status_pembayaran AS ENUM ( 
'Belum Bayar', 
'Sudah Dikonfirmasi', 
'Dikonfirmasi', 
'Ditolak' 
); 

-- 8. MEMBUAT TABEL PESANAN 
CREATE TABLE pesanan( 
pesanan_id SERIAL PRIMARY KEY, 
tanggal_pesan DATE NOT NULL, 
lama_penyewaan INTEGER NOT NULL, 
tanggal_pengambilan DATE NOT NULL, 
total INTEGER NOT NULL, 
nama_pemilik_rekening VARCHAR(30) NOT NULL, 
status_pembayaran status_pembayaran NOT NULL, 
motor_id CHAR(6) NOT NULL, 
CONSTRAINT motor_fk FOREIGN KEY(motor_id) REFERENCES  
motor(motor_id), 
admin_id INTEGER NOT NULL, 
CONSTRAINT admin_fk FOREIGN KEY(admin_id) REFERENCES  
admin(admin_id), 
metode_pembayaran_id INTEGER NOT NULL, 
CONSTRAINT metode_pembayaran_fk FOREIGN KEY 
(metode_pembayaran_id) REFERENCES  
metode_pembayaran(metode_pembayaran_id), 
pelanggan_id INTEGER NOT NULL, 
CONSTRAINT pelanggan_fk FOREIGN KEY(pelanggan_id) REFERENCES  
pelanggan(pelanggan_id) 
); 

-- 9. MEMBUAT TABEL PENGELUARAN 
CREATE TABLE pengeluaran( 
pengeluaran_id SERIAL PRIMARY KEY, 
tanggal DATE NOT NULL, 
jumlah INTEGER NOT NULL, 
deskripsi TEXT NOT NULL, 
motor_id CHAR(6) NOT NULL, 
CONSTRAINT motor_fk FOREIGN KEY(motor_id) REFERENCES  
motor(motor_id), 
admin_id INTEGER NOT NULL, 
CONSTRAINT admin_fk FOREIGN KEY(admin_id) REFERENCES  
admin(admin_id) 
); 

-- 10. MEMBUAT TABEL FASILITAS 
CREATE TABLE fasilitas(  
fasilitas_id CHAR(6) PRIMARY KEY, 
nama_barang VARCHAR(20) NOT NULL, 
harga INTEGER NOT NULL  
); 
-- 11. MEMBUAT TABEL DETAIL_PESANAN 
CREATE TABLE detail_pesanan( 
detail_pesanan_id SERIAL PRIMARY KEY, 
pesanan_id INTEGER NOT NULL, 
CONSTRAINT pesanan_fk FOREIGN KEY(pesanan_id) REFERENCES  
pesanan(pesanan_id), 
fasilitas_id CHAR(6) NOT NULL, 
CONSTRAINT fasilitas_fk FOREIGN KEY(fasilitas_id) REFERENCES  
fasilitas(fasilitas_id) 
); 

-- 12. MEMBUAT TABEL ULASAN 
CREATE TABLE ulasan( 
id_ulasan SERIAL PRIMARY KEY, 
tanggal DATE NOT NULL, 
ulasan TEXT NOT NULL, 
pesanan_id INTEGER NOT NULL, 
CONSTRAINT pesanan_fk FOREIGN KEY(pesanan_id) REFERENCES  
pesanan(pesanan_id) 
); 

-- 13. MEMBUAT TABEL PENGEMBALIAN 
CREATE TABLE pengembalian( 
pengembalian_ID SERIAL PRIMARY KEY, 
tanggal_pengembalian DATE NOT NULL, 
denda INTEGER NULL, 
pesanan_id INTEGER NOT NULL, 
CONSTRAINT pesanan_fk FOREIGN KEY(pesanan_id) REFERENCES  
pesanan(pesanan_id), 
admin_id INTEGER NOT NULL, 
CONSTRAINT admin_fk FOREIGN KEY(admin_id) REFERENCES  
admin(admin_id) 
); 


-- QUERY 
-- 1. PELANGGAN 
insert into pelanggan(username, email, nomor_telp, nama, password, asal_kota)   
values  ('iklina', 'iklina@gmail.com', '081234567891', 'Iklina Najzil', 'iklina123', 
'Jember'), 
('gusti', 'gusti@gmail.com', '082345678912', 'Siti Gusti', 'gusti123', 'Bali'), 
('chelsea', 'chelsea@gmail.com', '083456789123', 'Chelsea Brilliant', 
'chelsea123', 'Denpasar'); 
select * from pelanggan 
  
-- 2. TIPE MOTOR 
insert into tipe_motor(tipe_motor_id, tipe_merek) 
values('SCPY01', 'Honda Scoopy Abu-abu'), 
('BEAT01', 'Honda Beat Merah-putih'), 
('YMHA01', 'Yamaha Mio Hijau'), 
('BEAT02', 'Honda Beat Abu-abu'), 
('SCPY02', 'Honda Scoopy Cream') 
select * from tipe_motor 
  
-- 3. MOTOR 
insert into motor(motor_id, nomor_polisi, tipe_motor_id, tahun, harga_sewa, 
status_ketersediaan)   
values  ('MTR001', 'DK 3254 YTR','SCPY02', 2024, 70000, TRUE), 
('MTR002', 'DK 5382 JKL', 'BEAT01', 2023, 60000, TRUE), 
('MTR003', 'DK 6311 LHK', 'BEAT02', 2022, 60000, TRUE), 
('MT0004', 'DK 3254 IQR', 'SCPY01', 2024, 70000,TRUE) 
select * from motor 
  
-- 4. ADMIN 
insert into admin(admin_id, username, password)   
values  (1, 'admin1', 'admin123'), 
(2, 'admin2', 'admin456'); 
select * from admin 
  
-- 5. METODE PEMBAYARAN 
insert into metode_pembayaran(jenis_pembayaran, no_rekening_ewallet)   
values  ('Bank', 12345678), 
('E-Wallet', 87654321), 
('Cash', NULL); 
select * from metode_pembayaran 
  
-- 6. PESANAN 
insert into pesanan(tanggal_pesan, lama_penyewaan, tanggal_pengambilan, total, 
nama_pemilik_rekening, status_pembayaran, motor_id, admin_id, 
metode_pembayaran_id, pelanggan_id)   
values  ('2025-06-01', 1, '2025-06-01', 80000, 'Iklina Najzil', 'Dikonfirmasi',  
'MTR001', 1, 1, 1), 
('2025-06-02', 7, '2025-06-02', 560000, 'Siti Gusti', 'Belum Bayar', 'MTR002',  
2, 2, 2); 
select * from pesanan 
  
-- 7. FASILITAS 
insert into fasilitas(fasilitas_id, nama_barang, harga)   
values ('F001', 'Helm', 10000), 
('F002', 'Jas Hujan', 5000), 
('F003', 'Peta Wisata', 2000); 
select * from fasilitas 
  
-- 8. DETAIL_PESANAN 
insert into detail_pesanan(pesanan_id, fasilitas_id)   
values (1, 'F001'), 
(1, 'F002'), 
(2, 'F001'), 
(2, 'F003'); 
select * from detail_pesanan 
  
-- 9. PENGELUARAN 
insert into pengeluaran(tanggal, jumlah, deskripsi, motor_id, admin_id)   
values ('2025-05-31', 150000, 'Servis rutin motor MTR001', 'MTR001', 1), 
('2025-05-28', 80000, 'Ganti oli motor MTR002', 'MTR002', 2); 
select * from pengeluaran 
  
-- 10. ULASAN  
insert into ulasan(tanggal, ulasan, pesanan_id)   
values  ('2025-06-03', 'Motor bersih dan nyaman', 1), 
('2025-06-10', 'Pelayanan sangat ramah', 2); 
select * from ulasan  
  
-- 11. PENGEMBALIAN 
insert into pengembalian(tanggal_pengembalian, denda, pesanan_id, admin_id)   
values ('2025-06-02', 0, 1, 1), 
('2025-06-10', 50000, 2, 2); 
select * from pengembalian 
