-- ============================================================
--  KAS-KELAS DATABASE SCHEMA
--  Database: kas_kelas_user
--  Engine: MySQL (XAMPP/phpMyAdmin)
-- ============================================================

CREATE DATABASE IF NOT EXISTS `kas_kelas_user`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `kas_kelas_user`;

-- ── TABEL USERS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `users` (
  `id`         INT AUTO_INCREMENT PRIMARY KEY,
  `username`   VARCHAR(50)  NOT NULL UNIQUE,
  `password`   VARCHAR(255) NOT NULL,
  `nama`       VARCHAR(100) NOT NULL,
  `email`      VARCHAR(120) NOT NULL UNIQUE,
  `role`       ENUM('admin','siswa') NOT NULL DEFAULT 'siswa',
  `kelas`      VARCHAR(50)  NOT NULL DEFAULT 'XII-IPA-1',
  `avatar`     VARCHAR(5)   NOT NULL DEFAULT 'U',
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── TABEL ANGGOTA ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `anggota` (
  `id`         INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`    INT NOT NULL,
  `kelas`      VARCHAR(50) NOT NULL DEFAULT 'XII-IPA-1',
  `status`     ENUM('Lunas','Belum Lunas') NOT NULL DEFAULT 'Belum Lunas',
  `jumlah`     INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── TABEL TRANSAKSI ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS `transaksi` (
  `id`          INT AUTO_INCREMENT PRIMARY KEY,
  `tanggal`     DATE         NOT NULL,
  `keterangan`  VARCHAR(255) NOT NULL,
  `jenis`       ENUM('pemasukan','pengeluaran') NOT NULL,
  `jumlah`      INT          NOT NULL,
  `kategori`    VARCHAR(50)  NOT NULL DEFAULT 'Lainnya',
  `saldo`       INT          NOT NULL DEFAULT 0,
  `created_by`  INT,
  `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── TABEL IURAN ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `iuran` (
  `id`           INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`      INT  NOT NULL,
  `bulan`        VARCHAR(30) NOT NULL,
  `jumlah`       INT NOT NULL DEFAULT 50000,
  `status`       ENUM('Lunas','Belum Lunas') NOT NULL DEFAULT 'Belum Lunas',
  `tanggal_bayar` DATE,
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── TABEL PENGUMUMAN ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS `pengumuman` (
  `id`         INT AUTO_INCREMENT PRIMARY KEY,
  `judul`      VARCHAR(200) NOT NULL,
  `isi`        TEXT         NOT NULL,
  `penting`    TINYINT(1)   NOT NULL DEFAULT 0,
  `penulis`    VARCHAR(100) NOT NULL,
  `tanggal`    DATE         NOT NULL,
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
--  DATA AWAL (SEED)
-- ============================================================

-- Users
INSERT INTO `users` (`username`,`password`,`nama`,`email`,`role`,`kelas`,`avatar`) VALUES
('admin',   'admin123',  'Administrator', 'admin@kaskelas.id', 'admin',  'XII-IPA-1', 'A'),
('budi',    'budi123',   'Budi Santoso',  'budi@siswa.id',    'siswa',  'XII-IPA-1', 'B'),
('sari',    'sari123',   'Sari Dewi',     'sari@siswa.id',    'siswa',  'XII-IPA-1', 'S'),
('ahmad',   'ahmad123',  'Ahmad Rizki',   'ahmad@siswa.id',   'siswa',  'XII-IPA-1', 'A'),
('dewi',    'dewi123',   'Dewi Lestari',  'dewi@siswa.id',    'siswa',  'XII-IPA-1', 'D'),
('eko',     'eko123',    'Eko Prasetyo',  'eko@siswa.id',     'siswa',  'XII-IPA-1', 'E');

-- Anggota
INSERT INTO `anggota` (`user_id`,`kelas`,`status`,`jumlah`) VALUES
(2, 'XII-IPA-1', 'Lunas',       50000),
(3, 'XII-IPA-1', 'Belum Lunas', 0),
(4, 'XII-IPA-1', 'Lunas',       50000),
(5, 'XII-IPA-1', 'Lunas',       50000),
(6, 'XII-IPA-1', 'Belum Lunas', 0);

-- Transaksi
INSERT INTO `transaksi` (`tanggal`,`keterangan`,`jenis`,`jumlah`,`kategori`,`saldo`,`created_by`) VALUES
('2024-10-01','Iuran Bulanan - Budi Santoso',    'pemasukan',   50000, 'Iuran',    50000,  1),
('2024-10-02','Iuran Bulanan - Ahmad Rizki',     'pemasukan',   50000, 'Iuran',   100000,  1),
('2024-10-03','Iuran Bulanan - Dewi Lestari',    'pemasukan',   50000, 'Iuran',   150000,  1),
('2024-10-05','Pembelian ATK Kelas',             'pengeluaran', 35000, 'ATK',     115000,  1),
('2024-10-10','Dekorasi Kelas',                  'pengeluaran', 45000, 'Dekorasi', 70000,  1),
('2024-10-15','Iuran Bulanan - Budi Santoso (Nov)','pemasukan', 50000, 'Iuran',   120000,  1);

-- Iuran
INSERT INTO `iuran` (`user_id`,`bulan`,`jumlah`,`status`,`tanggal_bayar`) VALUES
(2, 'Agustus 2024',  50000, 'Lunas',       '2024-08-05'),
(2, 'September 2024',50000, 'Lunas',       '2024-09-02'),
(2, 'Oktober 2024',  50000, 'Lunas',       '2024-10-01'),
(2, 'November 2024', 50000, 'Belum Lunas', NULL),
(3, 'Agustus 2024',  50000, 'Lunas',       '2024-08-08'),
(3, 'September 2024',50000, 'Lunas',       '2024-09-10'),
(3, 'Oktober 2024',  50000, 'Belum Lunas', NULL);

-- Pengumuman
INSERT INTO `pengumuman` (`judul`,`isi`,`penting`,`penulis`,`tanggal`) VALUES
('Reminder Iuran Bulan Oktober',
 'Harap segera melunasi iuran kas kelas bulan Oktober sebelum tanggal 15. Nominal iuran sebesar Rp 50.000/bulan.',
 1, 'Administrator', '2024-10-01'),
('Kegiatan Study Tour November',
 'Kas kelas akan digunakan untuk mendukung kegiatan study tour bulan November. Detail lebih lanjut akan diinformasikan.',
 0, 'Administrator', '2024-10-08'),
('Laporan Keuangan September',
 'Laporan keuangan bulan September telah selesai dibuat. Total pemasukan Rp 450.000 dan total pengeluaran Rp 280.000.',
 0, 'Administrator', '2024-10-12');
