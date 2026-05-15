# Capscoba Backend

Backend project ini dibuat menggunakan Django dan Django REST Framework (DRF) dengan sistem Role-Based Access Control (RBAC) menggunakan JSON Web Token (JWT).

## 🚀 Step-by-Step Setup Backend

Panduan ini digunakan jika kamu ingin menjalankan project ini dari awal atau di komputer/server baru.

### 1. Persiapan Awal (Prerequisites)
Pastikan hal-hal berikut sudah terinstall di komputermu:
- **Python** (Versi 3.8 ke atas disarankan)
- **PostgreSQL** (Sistem database utama yang digunakan)

### 2. Setup Virtual Environment
Buka terminal dan masuk ke folder `backend`, kemudian buat virtual environment untuk mengisolasi package python:
```bash
# Membuat virtual environment dengan nama ".venv"
python -m venv .venv

# Mengaktifkan virtual environment (Windows)
.venv\Scripts\activate

# Mengaktifkan virtual environment (Mac/Linux)
source .venv/bin/activate
```

### 3. Install Dependencies
Pastikan virtual environment sudah aktif (biasanya ada tulisan `(.venv)` di awal command line). Install semua requirements yang dibutuhkan:
```bash
pip install -r requirements.txt
```
*(Jika belum ada `requirements.txt`, install secara manual: `pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-decouple psycopg2 requests`)*

### 4. Konfigurasi Environment Variables (.env)
Buat file bernama `.env` di **folder root backend** (sejajar dengan file `manage.py`). File ini menyimpan seluruh data sensitif:

```env
# Konfigurasi Database PostgreSQL
DB_NAME=capstone
DB_USER=postgres
DB_PASSWORD=PasswordPostgresKamu
DB_HOST=localhost
DB_PORT=5432

# CORS Frontend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Konfigurasi Django Base
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=django-insecure-kunci-rahasia-kamu
DEBUG=True

# Konfigurasi JWT Token
JWT_ACCESS_TOKEN_MINUTES=60
JWT_REFRESH_TOKEN_DAYS=1
```
> **Penting**: Pastikan database `capstone` sudah terbuat di dalam PostgreSQL milikmu. (Bisa menggunakan pgAdmin atau psql `CREATE DATABASE capstone;`)

### 5. Menjalankan Migrations Database
Setelah koneksi database di `.env` sudah benar, lakukan migrasi untuk membuat tabel-tabel di database (termasuk Auth, Employee, Profile, dan TrainingData).
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seeding Database (Penting!)
Jalankan file seeder untuk memasukkan group roles yang dibutuhkan (Super Administrator, Administrator, Dean, Head of Division, Team Leader, dan Employee) beserta 1 akun Super Administrator.
```bash
python manage.py seed
```
Jika sukses, kamu akan mendapatkan output bahwa group telah terbuat dan akun default terbentuk:
- **Username:** `superadmin`
- **Password:** `superadmin123`

*(Catatan: Kamu bisa langsung menggunakan kredensial ini untuk login sebagai level tertinggi di frontend).*

### 7. Menjalankan Development Server
Terakhir, jalankan server Django secara lokal:
```bash
python manage.py runserver
```
Server backend kamu akan berjalan di `http://127.0.0.1:8000/`.

---

## 🛠️ Penggunaan Database Selanjutnya

Setelah sistem tersetup, **urutan alur data pertama kali** (dilakukan oleh Super Administrator) adalah:
1. Login menggunakan `superadmin`
2. Tambahkan data **Employee** utama terlebih dahulu (Data Karyawan / Pegawai asli).
3. Buat **User** baru untuk karyawan yang diberikan akses menggunakan sistem.
4. Buatkan (Assign) user tersebut ke **Profile** yang disambungkan ke spesifik Employee NIK, sehingga hak akses RBAC (Role-Based Access Control) dapat bekerja.
