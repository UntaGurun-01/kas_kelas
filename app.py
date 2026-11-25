from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
from functools import wraps
import json
import os
import sys

app = Flask(__name__)

# ─── KONFIGURASI ─────────────────────────────────────────────────────────────
app.secret_key = os.environ.get('SECRET_KEY', 'kas-kelas-user-portal-secret-2024')

# Terhubung ke database kas_kelas (Database bersama dengan Web Admin)
_db_url = os.environ.get("DATABASE_URL") or "mysql+pymysql://root:@localhost:3306/kas_kelas?charset=utf8mb4"
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,
    'pool_pre_ping': True,
}

db = SQLAlchemy(app)

# ─── MODELS (PERSIS DENGAN WEB ADMIN) ─────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap  = db.Column(db.String(150))
    role          = db.Column(db.Enum('ketua', 'bendahara', 'anggota', name='user_role_enum', native_enum=False), default='anggota')
    foto_profil   = db.Column(db.String(255), default=None)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


class Kelas(db.Model):
    __tablename__ = 'kelas'
    id            = db.Column(db.Integer, primary_key=True)
    nama_kelas    = db.Column(db.String(100), nullable=False, default='B')
    jurusan       = db.Column(db.String(100), default='Teknik Informatika')
    angkatan      = db.Column(db.String(50),  default='2024/24')
    schedule      = db.Column(db.String(100))
    ketua_nama    = db.Column(db.String(100))
    no_dana       = db.Column(db.String(50),  default='+62123456')
    an_dana       = db.Column(db.String(100), default='Bendahara Kelas')
    no_gopay      = db.Column(db.String(50),  default='')
    an_gopay      = db.Column(db.String(100), default='Bendahara Kelas')
    no_ovo        = db.Column(db.String(50),  default='')
    an_ovo        = db.Column(db.String(100), default='Bendahara Kelas')
    no_brimo      = db.Column(db.String(50),  default='')
    an_brimo      = db.Column(db.String(100), default='Kas Kelas 2024')
    iuran_bulanan = db.Column(db.Numeric(15, 2), default=5000)
    notification_sound = db.Column(db.String(255))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)


class Anggota(db.Model):
    __tablename__ = 'anggota'
    id           = db.Column(db.Integer, primary_key=True)
    nama         = db.Column(db.String(150), nullable=False)
    nim          = db.Column(db.String(20), unique=True, nullable=False)
    jurusan      = db.Column(db.String(100))
    email        = db.Column(db.String(150))
    phone        = db.Column(db.String(20))
    foto_profil  = db.Column(db.String(255), default=None)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'))
    status_aktif = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    user       = db.relationship('User', backref=db.backref('anggota_rel', uselist=False))
    pembayaran = db.relationship('Pembayaran', backref='anggota', lazy=True)


class Kategori(db.Model):
    __tablename__ = 'kategori'
    id    = db.Column(db.Integer, primary_key=True)
    nama  = db.Column(db.String(100), nullable=False)
    jenis = db.Column(db.Enum('pemasukan', 'pengeluaran', name='kategori_jenis_enum', native_enum=False), nullable=False)
    warna = db.Column(db.String(20), default='#3265F1')
    icon  = db.Column(db.String(50), default='bi-tag')


class Transaksi(db.Model):
    __tablename__ = 'transaksi'
    id          = db.Column(db.Integer, primary_key=True)
    tanggal     = db.Column(db.Date, nullable=False)
    jenis       = db.Column(db.Enum('pemasukan', 'pengeluaran', name='transaksi_jenis_enum', native_enum=False), nullable=False)
    keterangan  = db.Column(db.Text)
    nominal     = db.Column(db.Numeric(15, 2), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'))
    anggota_id  = db.Column(db.Integer, db.ForeignKey('anggota.id'))
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    kategori = db.relationship('Kategori', backref='transaksi', lazy=True)
    anggota  = db.relationship('Anggota', backref='transaksi', lazy=True, foreign_keys=[anggota_id])
    creator  = db.relationship('User', backref='transaksi_dibuat', lazy=True, foreign_keys=[user_id])


class Pembayaran(db.Model):
    __tablename__ = 'pembayaran'
    id                = db.Column(db.Integer, primary_key=True)
    anggota_id        = db.Column(db.Integer, db.ForeignKey('anggota.id'), nullable=False)
    bulan             = db.Column(db.Integer, nullable=False)
    tahun             = db.Column(db.Integer, nullable=False)
    nominal           = db.Column(db.Numeric(15, 2), nullable=False, default=5000)
    status            = db.Column(db.String(20), default='belum_lunas')
    tanggal_bayar     = db.Column(db.Date)
    metode_pembayaran = db.Column(db.String(50))
    payment_token     = db.Column(db.String(255))
    payment_url       = db.Column(db.String(500))
    order_id          = db.Column(db.String(100))
    transaksi_id      = db.Column(db.Integer)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)


class Notifikasi(db.Model):
    __tablename__ = 'notifikasi'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    judul      = db.Column(db.String(200), nullable=False)
    pesan      = db.Column(db.Text, nullable=False)
    jenis      = db.Column(db.String(50), default='info')
    icon       = db.Column(db.String(50), default='bi-bell')
    dibaca     = db.Column(db.Boolean, default=False)
    link       = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─── NAMA BULAN HELPER ────────────────────────────────────────────────────────
BULAN_NAMA = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session['user']['role'] not in ('ketua', 'bendahara'):
            flash('Akses ditolak. Fitur ini khusus pengurus kelas.', 'danger')
            return redirect(url_for('beranda'))
        return f(*args, **kwargs)
    return decorated

def hitung_statistik():
    from sqlalchemy import func
    total_masuk  = int(db.session.query(func.sum(Transaksi.nominal)).filter_by(jenis='pemasukan').scalar() or 0)
    total_keluar = int(db.session.query(func.sum(Transaksi.nominal)).filter_by(jenis='pengeluaran').scalar() or 0)
    saldo        = total_masuk - total_keluar
    
    kelas = Kelas.query.first()
    iuran_per_bulan = int(kelas.iuran_bulanan) if kelas and kelas.iuran_bulanan else 5000
    
    jumlah_anggota = Anggota.query.filter_by(status_aktif=True).count()
    
    # Hitung tunggakan bulan ini
    now = date.today()
    belum_lunas_cnt = Pembayaran.query.filter_by(bulan=now.month, tahun=now.year, status='belum_lunas').count()
    total_tagihan = belum_lunas_cnt * iuran_per_bulan

    return {
        'saldo': saldo,
        'total_pemasukan': total_masuk,
        'total_pengeluaran': total_keluar,
        'total_tagihan': total_tagihan,
        'jumlah_anggota': jumlah_anggota,
        'iuran_bulanan': iuran_per_bulan,
        'nama_kelas': kelas.nama_kelas if kelas else 'TIF',
        'jurusan': kelas.jurusan if kelas else 'Teknik Informatika 24',
        'ketua_nama': kelas.ketua_nama if kelas else 'meliana harefa',
    }

@app.before_request
def sync_user_session():
    if 'user' in session and session['user'].get('id'):
        user_id = session['user']['id']
        u = db.session.get(User, user_id)
        if u:
            # Pastikan foto_profil selalu sinkron dari MySQL saat web di-refresh
            if u.foto_profil:
                session['user']['foto_profil'] = u.foto_profil
            else:
                a = Anggota.query.filter((Anggota.user_id == u.id) | (Anggota.nim == u.username)).first()
                if a and a.foto_profil:
                    u.foto_profil = a.foto_profil
                    session['user']['foto_profil'] = a.foto_profil
                    db.session.commit()
            if u.nama_lengkap:
                session['user']['nama'] = u.nama_lengkap
            session.modified = True

# ─── ROUTES ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('beranda') if 'user' in session else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('beranda'))
    if request.method == 'POST':
        nama_input = (request.form.get('nama') or request.form.get('username') or '').strip()
        nim_input  = (request.form.get('nim') or request.form.get('password') or '').strip()
        
        # 1. Jalur Login Khusus Admin / Bendahara
        if nama_input.lower() in ('admin', 'bendahara') and nim_input in ('admin123', 'admin', '123456'):
            admin_user = User.query.filter(User.username.in_(['admin', 'bendahara'])).first()
            if admin_user:
                kelas = Kelas.query.first()
                session['user'] = {
                    'id': admin_user.id,
                    'username': admin_user.username,
                    'nama': admin_user.nama_lengkap or admin_user.username,
                    'role': admin_user.role,
                    'email': admin_user.email,
                    'kelas': kelas.nama_kelas if kelas else 'B',
                    'avatar': (admin_user.nama_lengkap or 'A')[0].upper(),
                    'foto_profil': admin_user.foto_profil,
                    'anggota_id': None,
                    'nim': 'Pengurus',
                }
                flash(f'Selamat datang, {admin_user.nama_lengkap or "Admin"}! 👋', 'success')
                return redirect(url_for('beranda'))

        # 2. Jalur Login Siswa / Anggota: Validasi Nama & NIM / Kata Kunci 24
        anggota = None
        input_nama_clean = nama_input.lower().replace('.', '').strip()
        nim_clean = nim_input.strip()

        # Kasus A: Jika user menginput NIM lengkap (awalan 24)
        if nim_clean.startswith('24') and len(nim_clean) > 2:
            kandidat = Anggota.query.filter(Anggota.nim == nim_clean).first()
            if kandidat:
                k_nama_clean = kandidat.nama.lower().replace('.', '').strip()
                words = [w for w in input_nama_clean.split() if len(w) >= 2]
                if not input_nama_clean or (input_nama_clean in k_nama_clean or any(w in k_nama_clean for w in words)):
                    anggota = kandidat

        # Kasus B: Jika user mencari via Nama dan mengisi kata kunci '24' atau NIM-nya
        if not anggota and input_nama_clean:
            kandidat_list = Anggota.query.filter(Anggota.nama.ilike(f"%{input_nama_clean}%")).all()
            if not kandidat_list:
                first_word = input_nama_clean.split()[0]
                kandidat_list = Anggota.query.filter(Anggota.nama.ilike(f"%{first_word}%")).all()

            for k in kandidat_list:
                # Cocok jika kata kunci adalah '24' (karena angkatan 2024) ATAU NIM lengkapnya
                if nim_clean in ('24', k.nim, k.nim[:2]):
                    anggota = k
                    break

        # Jika Anggota berhasil divalidasi
        if anggota:
            kelas = Kelas.query.first()
            # Ambil atau buat akun User pendamping
            user = User.query.get(anggota.user_id) if anggota.user_id else None
            if not user:
                user = User.query.filter_by(username=anggota.nim).first()
            if not user:
                user = User(
                    username=anggota.nim,
                    email=anggota.email or f"{anggota.nim}@mhs.tif.ac.id",
                    nama_lengkap=anggota.nama,
                    role='anggota'
                )
                user.set_password(nim_input)
                db.session.add(user)
                db.session.flush()
                anggota.user_id = user.id
                db.session.commit()

            foto = user.foto_profil or anggota.foto_profil
            session['user'] = {
                'id': user.id,
                'username': anggota.nim,
                'nama': anggota.nama,
                'role': 'anggota',
                'email': anggota.email,
                'kelas': kelas.nama_kelas if kelas else 'B',
                'avatar': anggota.nama[0].upper() if anggota.nama else 'S',
                'foto_profil': foto,
                'anggota_id': anggota.id,
                'nim': anggota.nim,
            }
            print(f"[LOGIN SISWA BERHASIL] {anggota.nama} (NIM: {anggota.nim})")
            flash(f'Selamat datang, {anggota.nama}! 👋', 'success')
            return redirect(url_for('beranda'))

        print(f"[LOGIN GAGAL] Nama: '{nama_input}', NIM: '{nim_input}'")
        flash('Nama atau NIM tidak sesuai dengan data anggota kelas. Pastikan NIM diawali angka 24.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Berhasil logout.', 'info')
    return redirect(url_for('login'))

@app.route('/beranda')
@login_required
def beranda():
    stats = hitung_statistik()
    recent = Transaksi.query.order_by(Transaksi.tanggal.desc(), Transaksi.id.desc()).limit(5).all()
    
    # Riwayat iuran user yang sedang login
    user_id = session['user']['id']
    anggota_id = session['user'].get('anggota_id')
    
    riwayat_user = []
    if anggota_id:
        pembayaran_list = Pembayaran.query.filter_by(anggota_id=anggota_id).order_by(Pembayaran.tahun.desc(), Pembayaran.bulan.desc()).limit(4).all()
        for p in pembayaran_list:
            b_nama = BULAN_NAMA[p.bulan] if 1 <= p.bulan <= 12 else str(p.bulan)
            riwayat_user.append({
                'bulan': f"{b_nama} {p.tahun}",
                'jumlah': int(p.nominal),
                'status': 'Lunas' if p.status == 'lunas' else 'Belum Lunas',
                'tanggal_bayar': p.tanggal_bayar.strftime('%Y-%m-%d') if p.tanggal_bayar else None
            })
    else:
        # Jika belum punya anggota_id (misal akun admin), tampilkan 3 transaksi pemasukan terakhir
        top_incomes = Transaksi.query.filter_by(jenis='pemasukan').order_by(Transaksi.tanggal.desc()).limit(3).all()
        for t in top_incomes:
            riwayat_user.append({
                'bulan': t.keterangan[:24],
                'jumlah': int(t.nominal),
                'status': 'Lunas',
                'tanggal_bayar': t.tanggal.strftime('%Y-%m-%d') if t.tanggal else None
            })

    # Data Grafik Garis (6 bulan terakhir)
    from sqlalchemy import func, extract
    bulan_nums = [5, 6, 7, 8, 9, 10]
    months_label = [BULAN_NAMA[m][:3] for m in bulan_nums]

    def get_monthly(jenis):
        rows = (db.session.query(
                    extract('month', Transaksi.tanggal).label('bln'),
                    func.sum(Transaksi.nominal).label('total'))
                .filter(Transaksi.jenis == jenis,
                        extract('month', Transaksi.tanggal).in_(bulan_nums))
                .group_by('bln').all())
        lookup = {int(r.bln): int(r.total) for r in rows}
        return [lookup.get(b, 0) for b in bulan_nums]

    pemasukan_data  = get_monthly('pemasukan')
    pengeluaran_data = get_monthly('pengeluaran')

    # Data Donut Chart Kategori
    kat_rows = (db.session.query(Kategori.nama, func.sum(Transaksi.nominal).label('total'))
                .join(Transaksi, Transaksi.kategori_id == Kategori.id)
                .group_by(Kategori.nama).all())
    kategori_data = {r[0]: int(r[1]) for r in kat_rows}
    if not kategori_data:
        kategori_data = {'Iuran Kas': stats['total_pemasukan']} if stats['total_pemasukan'] > 0 else {'Belum Ada Transaksi': 0}

    return render_template('beranda.html',
        stats=stats,
        recent_transaksi=recent,
        riwayat_user=riwayat_user,
        months=json.dumps(months_label),
        pemasukan_data=json.dumps(pemasukan_data),
        pengeluaran_data=json.dumps(pengeluaran_data),
        kategori_data=json.dumps(kategori_data),
    )

@app.route('/iuran-saya')
@login_required
def iuran():
    anggota_id = session['user'].get('anggota_id')
    data = []
    
    if anggota_id:
        pembayaran_list = Pembayaran.query.filter_by(anggota_id=anggota_id).order_by(Pembayaran.tahun.desc(), Pembayaran.bulan.desc()).all()
        for p in pembayaran_list:
            b_nama = BULAN_NAMA[p.bulan] if 1 <= p.bulan <= 12 else str(p.bulan)
            data.append({
                'bulan': f"{b_nama} {p.tahun}",
                'jumlah': int(p.nominal),
                'status': 'Lunas' if p.status == 'lunas' else 'Belum Lunas',
                'tanggal_bayar': p.tanggal_bayar.strftime('%Y-%m-%d') if p.tanggal_bayar else None,
                'metode': p.metode_pembayaran or '—'
            })
    else:
        # Fallback jika admin melihat halaman ini
        data = [
            {'bulan': 'Oktober 2026', 'jumlah': 5000, 'status': 'Lunas', 'tanggal_bayar': '2026-10-13', 'metode': 'Tunai'},
            {'bulan': 'November 2026', 'jumlah': 5000, 'status': 'Belum Lunas', 'tanggal_bayar': None, 'metode': '—'}
        ]

    lunas = sum(1 for i in data if i['status'] == 'Lunas')
    belum = sum(1 for i in data if i['status'] == 'Belum Lunas')
    total_dibayar = sum(i['jumlah'] for i in data if i['status'] == 'Lunas')
    
    kelas = Kelas.query.first()
    return render_template('iuran.html', data=data, lunas=lunas, belum=belum, total_dibayar=total_dibayar, kelas=kelas)

@app.route('/transaksi')
@login_required
def transaksi():
    filter_jenis = request.args.get('jenis', 'semua')
    q = Transaksi.query.order_by(Transaksi.tanggal.desc(), Transaksi.id.desc())
    if filter_jenis in ('pemasukan', 'pengeluaran'):
        q = q.filter_by(jenis=filter_jenis)
    
    items = q.all()
    stats = hitung_statistik()
    
    # Format transaksi agar template bisa membaca kategori & nominal dengan rapi
    data = []
    running_saldo = stats['saldo']
    for t in items:
        data.append({
            'id': t.id,
            'tanggal': t.tanggal.strftime('%Y-%m-%d') if t.tanggal else '—',
            'keterangan': t.keterangan or 'Tanpa Keterangan',
            'jenis': t.jenis,
            'jumlah': int(t.nominal),
            'saldo': running_saldo,
            'kategori': t.kategori.nama if t.kategori else 'Iuran Kas',
        })
    return render_template('transaksi.html', data=data, filter_jenis=filter_jenis, stats=stats)

@app.route('/transaksi/tambah', methods=['GET', 'POST'])
@admin_required
def tambah_transaksi():
    kategori_list = Kategori.query.all()
    if request.method == 'POST':
        jenis       = request.form.get('jenis')
        keterangan  = request.form.get('keterangan')
        jumlah      = int(request.form.get('jumlah', 0))
        kategori_id = request.form.get('kategori')
        tanggal     = datetime.strptime(request.form.get('tanggal'), '%Y-%m-%d').date()

        t = Transaksi(
            tanggal=tanggal,
            keterangan=keterangan,
            jenis=jenis,
            nominal=jumlah,
            kategori_id=int(kategori_id) if kategori_id else None,
            user_id=session['user']['id']
        )
        db.session.add(t)
        db.session.commit()
        flash('Transaksi kas kelas berhasil dicatat!', 'success')
        return redirect(url_for('transaksi'))
    return render_template('tambah_transaksi.html', kategori_list=kategori_list)

@app.route('/riwayat')
@login_required
def riwayat():
    items = Transaksi.query.order_by(Transaksi.tanggal.desc(), Transaksi.id.desc()).all()
    stats = hitung_statistik()
    data = []
    for t in items:
        data.append({
            'tanggal': t.tanggal.strftime('%Y-%m-%d') if t.tanggal else '—',
            'keterangan': t.keterangan or 'Tanpa Keterangan',
            'jenis': t.jenis,
            'jumlah': int(t.nominal),
            'saldo': stats['saldo'],
            'kategori': t.kategori.nama if t.kategori else 'Iuran',
        })
    return render_template('riwayat.html', data=data, stats=stats)

@app.route('/pengumuman')
@login_required
def pengumuman():
    notifs = Notifikasi.query.order_by(Notifikasi.created_at.desc()).all()
    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'judul': n.judul,
            'isi': n.pesan,
            'penting': n.jenis in ('pembayaran', 'penting'),
            'penulis': 'Bendahara Kelas',
            'tanggal': n.created_at.strftime('%Y-%m-%d') if n.created_at else '—'
        })
    return render_template('pengumuman.html', data=data)

@app.route('/pengumuman/tambah', methods=['GET', 'POST'])
@admin_required
def tambah_pengumuman():
    if request.method == 'POST':
        judul   = request.form.get('judul')
        isi     = request.form.get('isi')
        penting = request.form.get('penting') == 'on'
        
        n = Notifikasi(
            user_id=session['user']['id'],
            judul=judul,
            pesan=isi,
            jenis='pembayaran' if penting else 'info',
            icon='bi-megaphone-fill' if penting else 'bi-info-circle',
            link='/pengumuman'
        )
        db.session.add(n)
        db.session.commit()
        flash('Pengumuman berhasil disebarkan ke anggota kelas!', 'success')
        return redirect(url_for('pengumuman'))
    return render_template('tambah_pengumuman.html')

@app.route('/profil')
@login_required
def profil():
    user_id = session['user']['id']
    user = User.query.get(user_id)
    anggota = Anggota.query.filter_by(user_id=user_id).first() if user else None
    if not anggota and user:
        anggota = Anggota.query.filter_by(nim=user.username).first()
        if anggota:
            anggota.user_id = user.id
            db.session.commit()
    kelas = Kelas.query.first()
    
    # Sync foto_profil & nim if updated in DB
    if user and user.foto_profil:
        session['user']['foto_profil'] = user.foto_profil
    elif anggota and anggota.foto_profil:
        session['user']['foto_profil'] = anggota.foto_profil

    if anggota and anggota.nim:
        session['user']['nim'] = anggota.nim

    lunas = 0
    total = 0
    if anggota:
        p_list = Pembayaran.query.filter_by(anggota_id=anggota.id).all()
        lunas  = sum(1 for p in p_list if p.status == 'lunas')
        total  = sum(int(p.nominal) for p in p_list if p.status == 'lunas')
    else:
        lunas = 1
        total = 5000
        
    return render_template('profil.html',
                           user=user,
                           anggota=anggota,
                           kelas=kelas,
                           lunas=lunas,
                           total=total)

@app.route('/profil/upload-foto', methods=['POST'])
@login_required
def upload_foto():
    if 'foto_profil' not in request.files:
        flash('Pilih berkas foto terlebih dahulu.', 'warning')
        return redirect(url_for('profil'))
    
    file = request.files['foto_profil']
    if file.filename == '':
        flash('Tidak ada berkas yang dipilih.', 'warning')
        return redirect(url_for('profil'))
    
    allowed = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        flash('Format berkas tidak didukung! Gunakan format PNG, JPG, JPEG, atau WEBP.', 'danger')
        return redirect(url_for('profil'))
    
    user_id = session['user']['id']
    timestamp = int(datetime.now().timestamp())
    filename = f"avatar_u{user_id}_{timestamp}.{ext}"
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)
    
    user = db.session.get(User, user_id)
    if user:
        user.foto_profil = filename
    anggota = Anggota.query.filter_by(user_id=user_id).first()
    if not anggota and user:
        anggota = Anggota.query.filter_by(nim=user.username).first()
        if anggota:
            anggota.user_id = user.id
    if anggota:
        anggota.foto_profil = filename
    db.session.commit()
    
    session['user']['foto_profil'] = filename
    session.modified = True
    flash('Foto profil berhasil diunggah dari perangkat kamu! 📸', 'success')
    return redirect(url_for('profil'))

@app.route('/profil/update-kelas', methods=['POST'])
@login_required
def update_kelas():
    kelas = Kelas.query.first()
    if not kelas:
        kelas = Kelas()
        db.session.add(kelas)
    
    kelas.nama_kelas = request.form.get('nama_kelas', kelas.nama_kelas).strip()
    kelas.jurusan    = request.form.get('jurusan', kelas.jurusan).strip()
    kelas.angkatan   = request.form.get('angkatan', kelas.angkatan).strip()
    kelas.no_dana    = request.form.get('no_dana', kelas.no_dana or '+62123456').strip()
    
    db.session.commit()
    session['user']['kelas'] = kelas.nama_kelas
    flash('Informasi Kelas & No DANA berhasil diperbarui! ✅', 'success')
    return redirect(url_for('profil'))

@app.route('/profil/update-akun', methods=['POST'])
@login_required
def update_akun():
    user_id = session['user']['id']
    user = User.query.get(user_id)
    anggota = Anggota.query.filter_by(user_id=user_id).first()
    
    nama_baru  = request.form.get('nama', '').strip()
    nim_baru   = request.form.get('nim', '').strip()
    email_baru = request.form.get('email', '').strip()
    phone_baru = request.form.get('phone', '').strip()
    
    if nama_baru and user:
        user.nama_lengkap = nama_baru
        session['user']['nama'] = nama_baru
        session['user']['avatar'] = nama_baru[0].upper()
        if anggota:
            anggota.nama = nama_baru
            
    if nim_baru and anggota:
        anggota.nim = nim_baru
        session['user']['nim'] = nim_baru
        if user:
            user.username = nim_baru
            session['user']['username'] = nim_baru
            
    if email_baru and user:
        user.email = email_baru
        session['user']['email'] = email_baru
        if anggota:
            anggota.email = email_baru
            
    if phone_baru and anggota:
        anggota.phone = phone_baru
        
    db.session.commit()
    flash('Data akun Anda berhasil diperbarui!', 'success')
    return redirect(url_for('profil'))

@app.route('/anggota')
@login_required
def anggota_page():
    anggota_list = Anggota.query.filter_by(status_aktif=True).order_by(Anggota.nama).all()
    now = date.today()
    
    # Ambil status pembayaran bulan berjalan
    pembayaran_map = {}
    p_rows = Pembayaran.query.filter_by(bulan=now.month, tahun=now.year).all()
    for p in p_rows:
        pembayaran_map[p.anggota_id] = p.status
        
    result = []
    for a in anggota_list:
        status_bayar = pembayaran_map.get(a.id, 'belum_lunas')
        result.append({
            'id': a.id,
            'nama': a.nama,
            'kelas': session['user'].get('kelas', 'TIF'),
            'status': 'Lunas' if status_bayar == 'lunas' else 'Belum Lunas',
            'jumlah': 5000 if status_bayar == 'lunas' else 0,
        })
    return render_template('anggota.html', data=result)

# ─── PENGATURAN & TENTANG WEBSITE ───────────────────────────────────────────
@app.route('/pengaturan')
@login_required
def pengaturan():
    kelas = Kelas.query.first()
    user_id = session['user']['id']
    user = db.session.get(User, user_id)
    transaksi_count = Transaksi.query.count()
    riwayat_count = Pembayaran.query.filter_by(status='lunas').count()
    current_theme = session.get('theme', 'dark')
    
    return render_template('pengaturan.html',
                           kelas=kelas,
                           user=user,
                           transaksi_count=transaksi_count,
                           riwayat_count=riwayat_count,
                           current_theme=current_theme)

@app.route('/pengaturan/tema', methods=['POST'])
@login_required
def pengaturan_tema():
    tema = request.form.get('tema', 'dark').lower()
    if tema not in ('dark', 'light'):
        tema = 'dark'
    session['theme'] = tema
    session.modified = True
    
    # Support AJAX fetch request without page reload
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'status': 'success', 'tema': tema})
        
    flash(f'Tema tampilan berhasil diubah ke mode {"Gelap (Dark)" if tema == "dark" else "Terang (Light)"}! 🎨', 'success')
    return redirect(url_for('pengaturan'))

@app.route('/pengaturan/nada', methods=['POST'])
@login_required
def pengaturan_nada():
    kelas = Kelas.query.first()
    if not kelas:
        kelas = Kelas()
        db.session.add(kelas)
        
    sound_preset = request.form.get('sound_preset')
    
    # 1. Custom MP3 / Audio upload dari perangkat pengguna
    if 'audio_file' in request.files:
        audio = request.files['audio_file']
        if audio and audio.filename != '':
            allowed_audio = {'mp3', 'wav', 'ogg', 'm4a', 'aac'}
            ext = audio.filename.rsplit('.', 1)[-1].lower() if '.' in audio.filename else ''
            if ext in allowed_audio:
                timestamp = int(datetime.now().timestamp())
                filename = f"sound_custom_{timestamp}.{ext}"
                audio_dir = os.path.join(app.root_path, 'static', 'uploads', 'audio')
                os.makedirs(audio_dir, exist_ok=True)
                audio.save(os.path.join(audio_dir, filename))
                kelas.notification_sound = filename
                db.session.commit()
                flash('Nada notifikasi kustom berhasil diunggah dari perangkat kamu! 🎵', 'success')
                return redirect(url_for('pengaturan'))
            else:
                flash('Format audio tidak didukung! Gunakan format MP3, WAV, OGG, atau M4A.', 'danger')
                return redirect(url_for('pengaturan'))
                
    # 2. Preset nada bawaan
    if sound_preset:
        kelas.notification_sound = sound_preset
        db.session.commit()
        flash(f'Nada notifikasi berhasil diubah ke: {sound_preset} 🔔', 'success')
        
    return redirect(url_for('pengaturan'))

@app.route('/pengaturan/ewallet', methods=['POST'])
@login_required
def pengaturan_ewallet():
    kelas = Kelas.query.first()
    if not kelas:
        kelas = Kelas()
        db.session.add(kelas)
        
    kelas.no_dana  = request.form.get('no_dana', '').strip()
    kelas.an_dana  = request.form.get('an_dana', 'Bendahara Kelas').strip()
    kelas.no_gopay = request.form.get('no_gopay', '').strip()
    kelas.an_gopay = request.form.get('an_gopay', 'Bendahara Kelas').strip()
    kelas.no_ovo   = request.form.get('no_ovo', '').strip()
    kelas.an_ovo   = request.form.get('an_ovo', 'Bendahara Kelas').strip()
    kelas.no_brimo = request.form.get('no_brimo', '').strip()
    kelas.an_brimo = request.form.get('an_brimo', 'Kas Kelas 2024').strip()
    
    db.session.commit()
    flash('Akun e-Wallet & Bank (DANA, GoPay, OVO, BRImo) berhasil diperbarui dan aktif! 💳', 'success')
    return redirect(url_for('pengaturan'))

@app.route('/pengaturan/hapus-data', methods=['POST'])
@login_required
def hapus_data_kas():
    konfirmasi = request.form.get('konfirmasi', '').strip().upper()
    hapus_transaksi = request.form.get('hapus_transaksi') == 'on'
    hapus_riwayat   = request.form.get('hapus_riwayat') == 'on'
    
    if konfirmasi != 'HAPUS':
        flash('Konfirmasi gagal! Ketik kata "HAPUS" dengan huruf kapital untuk mengonfirmasi penghapusan data.', 'danger')
        return redirect(url_for('pengaturan'))
        
    pesan_list = []
    if hapus_transaksi:
        Transaksi.query.delete()
        pesan_list.append('seluruh data transaksi kas')
    if hapus_riwayat:
        Pembayaran.query.update({
            Pembayaran.status: 'belum_lunas',
            Pembayaran.tanggal_bayar: None,
            Pembayaran.metode_pembayaran: None,
            Pembayaran.transaksi_id: None
        })
        pesan_list.append('riwayat pembayaran kas kelas')
        
    db.session.commit()
    pesan = ' dan '.join(pesan_list) if pesan_list else 'data kas'
    flash(f'Berhasil! {pesan.capitalize()} telah berhasil dihapus / di-reset.', 'success')
    return redirect(url_for('pengaturan'))

@app.route('/tentang')
@login_required
def tentang():
    kelas = Kelas.query.first()
    jumlah_anggota = Anggota.query.filter_by(status_aktif=True).count()
    total_transaksi = Transaksi.query.count()
    total_masuk = db.session.query(db.func.sum(Transaksi.nominal)).filter(Transaksi.jenis == 'pemasukan').scalar() or 0
    
    # Ambil data pembuat (Agam & Ryo)
    agam = Anggota.query.filter(Anggota.nim == '2455201016').first()
    if not agam:
        agam = Anggota.query.filter(Anggota.nama.ilike('%AGAM%')).first()
        
    ryo = Anggota.query.filter(Anggota.nim == '2455201033').first()
    if not ryo:
        ryo = Anggota.query.filter(Anggota.nama.ilike('%RYO%')).first()
    if not ryo:
        ryo = Anggota.query.filter(Anggota.nama.ilike('%RIO%')).first()
        
    return render_template('tentang.html',
                           kelas=kelas,
                           jumlah_anggota=jumlah_anggota,
                           total_transaksi=total_transaksi,
                           total_masuk=total_masuk,
                           agam=agam,
                           ryo=ryo)

@app.route('/api/stats')
@login_required
def api_stats():
    return jsonify(hitung_statistik())

# ─── INIT DB & VERIFIKASI KONEKSI MYSQL ───────────────────────────────────────
def periksa_koneksi_database():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                print("==================================================")
                print("[OK] DATABASE MYSQL AKTIF & TERHUBUNG!")
                print("     Host    : localhost:3306")
                print("     Database: kas_kelas (Database Bersama Admin)")
                print("==================================================")
            db.create_all()
        except Exception as e:
            print("==================================================")
            print("[ERROR] DATABASE MYSQL TIDAK DAPAT DIAKSES!")
            print("Penyebab: Port MySQL (3306) belum aktif atau XAMPP belum dijalankan.")
            print("Solusi  : Buka XAMPP Control Panel lalu klik 'Start' pada modul MySQL.")
            print("Detail Error:", e)
            print("==================================================")
            sys.exit(1)

periksa_koneksi_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
