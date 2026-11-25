# 💰 Sistem Kas Kelas

Aplikasi web **Sistem Kas Kelas** yang dibangun untuk membantu pengelolaan keuangan kas kelas secara terstruktur dan mudah digunakan. Sistem ini menyediakan berbagai fitur untuk mengelola data anggota, pembayaran iuran, transaksi pemasukan dan pengeluaran, riwayat transaksi, pengumuman, pengaturan, serta profil pengguna.

Aplikasi dikembangkan menggunakan **Python dan Flask** sebagai backend, **MySQL** sebagai database, serta teknologi frontend berbasis **HTML, CSS, dan JavaScript**.

---

## 📋 Deskripsi Aplikasi

Sistem Kas Kelas merupakan aplikasi pengelolaan kas berbasis web yang dirancang untuk mempermudah proses pencatatan dan pemantauan keuangan kelas.

Melalui sistem ini, pengguna dapat melihat informasi kas, melakukan pencatatan pembayaran iuran, memantau transaksi pemasukan dan pengeluaran, melihat riwayat aktivitas keuangan, serta mengakses informasi terkait kelas dalam satu aplikasi.

Sistem juga dilengkapi dengan tampilan dashboard dan visualisasi data untuk membantu pengguna memahami kondisi keuangan kas dengan lebih mudah.

---

## ✨ Fitur Utama

### 1. 🏠 Dashboard / Beranda

- Menampilkan ringkasan informasi kas kelas.
- Menampilkan informasi saldo dan aktivitas keuangan.
- Menyediakan akses cepat menuju fitur utama sistem.
- Menampilkan informasi penting yang berkaitan dengan kondisi kas.

### 2. 👥 Data Anggota

- Menampilkan daftar anggota kelas.
- Mengelola data anggota yang terdaftar.
- Menyediakan informasi anggota secara terstruktur.
- Memudahkan pengelolaan data anggota kelas.

### 3. 💵 Pembayaran Iuran

- Mencatat pembayaran iuran anggota.
- Menampilkan informasi pembayaran.
- Membantu memantau pembayaran iuran.
- Menyimpan data pembayaran secara terstruktur.

### 4. 💳 Transaksi Kas

- Mencatat transaksi pemasukan.
- Mencatat transaksi pengeluaran.
- Menyimpan informasi nominal dan keterangan transaksi.
- Membantu mengontrol aktivitas keuangan kas kelas.

### 5. 📜 Riwayat Transaksi

- Menampilkan riwayat transaksi kas.
- Memudahkan pengguna melihat transaksi sebelumnya.
- Membantu proses monitoring aktivitas keuangan.
- Menyediakan informasi transaksi secara terstruktur.

### 6. 📢 Pengumuman

- Menampilkan informasi dan pengumuman kelas.
- Membantu menyampaikan informasi kepada anggota.
- Menyediakan tempat khusus untuk informasi yang berkaitan dengan kegiatan kelas.

### 7. ⚙️ Pengaturan

- Menyediakan pengaturan aplikasi.
- Mengelola konfigurasi sistem sesuai kebutuhan.
- Menyediakan akses terhadap pengaturan yang tersedia pada aplikasi.

### 8. 👤 Profil

- Menampilkan informasi profil pengguna.
- Menyediakan informasi akun pengguna.
- Memudahkan pengguna mengakses informasi pribadi yang berkaitan dengan sistem.

---

## 📊 Visualisasi Data

Sistem menggunakan **Chart.js** untuk membantu menampilkan data dalam bentuk grafik dan diagram.

Visualisasi dapat digunakan untuk memberikan gambaran yang lebih mudah dipahami mengenai aktivitas dan kondisi keuangan kas kelas.

---

## 🛠️ Teknologi yang Digunakan

### Backend

- **Python**
- **Flask**
- **Flask-SQLAlchemy**

### Database

- **MySQL**

### Frontend

- **HTML5**
- **CSS3**
- **JavaScript**

### UI / Styling

- **Bootstrap**
- **Tailwind CSS**

### Data Visualization

- **Chart.js**

---

## 📁 Struktur Project

```text
PROJECT SISTEM KAS KELAS/
│
├── templates/
│   ├── login.html
│   ├── pembayaran.html
│   ├── pengaturan.html
│   ├── tentang.html
│   └── transaksi.html
│
├── utils/
│
├── app.py
├── config.py
├── extensions.py
├── init_db.py
├── models.py
├── requirements.txt
│
├── .env
├── .env.example
├── .env.local
├── .gitignore
├── .vercelignore
├── vercel.json
├── wsgi.py
└── README.md
```

---

## 🗄️ Database

Sistem menggunakan **MySQL** sebagai database untuk menyimpan data aplikasi.

Konfigurasi koneksi database dikelola melalui file konfigurasi dan environment variable agar informasi koneksi tidak ditulis secara langsung pada kode utama aplikasi.

Beberapa komponen backend yang berkaitan dengan database antara lain:

- `config.py`
- `extensions.py`
- `models.py`
- `init_db.py`

---

## 📦 Dependencies

Daftar library Python yang digunakan oleh aplikasi tersedia di:

```text
requirements.txt
```

Untuk menginstalnya, jalankan:

```bash
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Clone Repository

Clone repository menggunakan Git:

```bash
git clone https://github.com/UntaGurun-01/kas_kelas.git
```

Kemudian masuk ke folder project:

```bash
cd kas_kelas
```

### 2. Buat Virtual Environment

Disarankan menggunakan virtual environment:

```bash
python -m venv venv
```

Aktifkan virtual environment pada Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Jalankan:

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment

Salin file environment contoh:

```text
.env.example
```

kemudian sesuaikan konfigurasi database dan kebutuhan aplikasi pada file `.env`.

**Jangan membagikan file `.env` ke repository publik apabila di dalamnya terdapat credential atau informasi rahasia.**

### 5. Siapkan Database

Pastikan MySQL sudah berjalan dan database yang diperlukan oleh aplikasi telah tersedia.

Sesuaikan konfigurasi koneksi database dengan environment yang digunakan.

### 6. Jalankan Aplikasi

Jalankan aplikasi Flask melalui:

```bash
python app.py
```

Setelah server berjalan, buka alamat lokal yang ditampilkan oleh Flask pada terminal.

---

## 🔐 Konfigurasi Environment

Aplikasi menggunakan environment variable untuk menyimpan konfigurasi tertentu.

Contoh konfigurasi dapat disediakan melalui:

```text
.env.example
```

Sedangkan konfigurasi lokal digunakan melalui:

```text
.env
```

File `.env` sebaiknya tidak diunggah ke repository publik karena dapat berisi informasi sensitif seperti credential database.

---

## 🌐 Deployment

Project memiliki konfigurasi:

```text
vercel.json
```

yang dapat digunakan sebagai bagian dari konfigurasi deployment.

Namun, konfigurasi deployment tetap perlu disesuaikan dengan environment dan kebutuhan server yang digunakan.

---

## 🎯 Tujuan Pengembangan

Sistem Kas Kelas dikembangkan untuk:

- Mempermudah pencatatan keuangan kelas.
- Mengurangi pencatatan manual.
- Mempermudah pengelolaan pembayaran iuran.
- Mempermudah pencatatan pemasukan dan pengeluaran.
- Menyediakan riwayat transaksi yang terstruktur.
- Membantu pengguna memantau kondisi kas.
- Menyediakan informasi keuangan melalui dashboard dan visualisasi data.

---

## 📌 Catatan

Project ini merupakan aplikasi pengelolaan kas kelas berbasis web yang dikembangkan sebagai project pembelajaran dan pengembangan sistem informasi.

Penggunaan aplikasi pada lingkungan produksi memerlukan konfigurasi database, environment, keamanan akun, serta deployment server yang sesuai.

---

## 👨‍💻 Project

**Nama:** Sistem Kas Kelas

**Platform:** Web Application

**Backend:** Python + Flask

**Database:** MySQL

**Frontend:** HTML + CSS + JavaScript

**Repository:** `UntaGurun-01/kas_kelas`

---

⭐ Jika project ini bermanfaat, jangan lupa memberikan **Star** pada repository.
