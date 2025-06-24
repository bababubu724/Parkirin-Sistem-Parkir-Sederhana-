Parkirin

Parkirin adalah aplikasi parkir berbasis GUI yang memudahkan manajemen kendaraan yang parkir. Aplikasi ini memiliki berbagai fitur untuk menangani check-in, check-out kendaraan, menghitung biaya parkir, dan menyimpan riwayat parkir. Selain itu, aplikasi ini juga mendukung berbagai macam pembayaran (cash dan cashless) serta denda untuk tiket yang hilang.

Fitur Utama:

* Check-in kendaraan: Mencatat kendaraan yang masuk ke area parkir beserta jenis kendaraan (mobil/motor) dan waktu masuk.
* Check-out kendaraan: Memungkinkan kendaraan untuk keluar dan menghitung biaya parkir berdasarkan durasi parkir.
* Perhitungan biaya parkir: Biaya parkir dihitung berdasarkan tarif per jam untuk kendaraan mobil atau motor.
* Riwayat parkir: Menyimpan data riwayat parkir yang meliputi informasi kendaraan, waktu masuk, waktu keluar, biaya, dan metode pembayaran.
* Denda tiket hilang: Jika tiket parkir hilang, pengguna dikenakan denda sesuai tarif yang ditentukan.
* Pembayaran Cash/Cashless: Mendukung pembayaran secara tunai maupun menggunakan e-money.

Prasyarat:

* Python 3.x
* `customtkinter`: Digunakan untuk antarmuka grafis dengan elemen-elemen modern.
* `PIL` (Pillow): Untuk membuka dan memanipulasi gambar.
* `json`: Untuk menangani file JSON dalam menyimpan data riwayat parkir.
* `math`: Untuk operasi matematika (perhitungan durasi dan biaya).
* `tkinter`: Untuk membuat antarmuka grafis dasar.

Instalasi:

1. Pastikan Python 3.x terinstal di sistem Anda.
2. Install pustaka yang diperlukan dengan menjalankan perintah berikut:

   ```
   pip install customtkinter pillow
   
   ```

Cara Menjalankan Aplikasi:

1. Pastikan Anda telah mengunduh atau mempersiapkan gambar untuk kendaraan (mobil/motor) pada direktori `assets/`:

   * `cctv_mobil.jpg` untuk gambar mobil
   * `cctv_motor.jpg` untuk gambar motor
   * `gambar_main.png` untuk gambar latar menu utama

2. Jalankan aplikasi dengan menjalankan script `app_parkirin.py`:

   ```
   python app_parkirin.py
   
   ```

Struktur Proyek:

Sistem-Parkir-Gambir/
│
├── assets/                   # Direktori untuk gambar kendaraan dan latar belakang menu
│   ├── cctv_mobil.jpg        # Gambar mobil
│   ├── cctv_motor.jpg        # Gambar motor
│   └── gambar_main.png       # Gambar latar belakang menu utama
│
├── app_parkirin.py           # File utama untuk menjalankan aplikasi
│
├── unittest_parkirin.py      # File untuk unit test
│
├── README.md                 # Dokumen ini
│
└── history/                  # Direktori untuk menyimpan riwayat parkir dalam format JSON
    └── riwayat_parkir.json   # Riwayat parkir kendaraan

Penjelasan Kode:

* CTkSpinbox: Komponen spinbox kustom yang digunakan untuk memilih tanggal, bulan, tahun, jam, menit, dan detik pada proses check-out.
* App: Kelas utama yang menangani aplikasi parkir, mulai dari check-in, check-out, hingga menyimpan riwayat parkir.
* Check-in dan Check-out: Fitur untuk mencatat kendaraan yang datang dan menghitung biaya saat kendaraan keluar.
* Pembayaran: Dialog yang memungkinkan pengguna untuk memilih metode pembayaran (cash atau cashless).

Tampilan Aplikasi:

Aplikasi ini menyediakan antarmuka grafis yang sederhana dan mudah digunakan. Berikut adalah beberapa tampilan utama:

1. Check-in kendaraan: Menyediakan input untuk nomor polisi, jenis kendaraan, dan tombol untuk melakukan check-in.
2. Check-out kendaraan: Menampilkan form untuk mengisi nomor polisi kendaraan yang keluar, dengan opsi untuk memilih waktu keluar manual dan menghitung biaya.
3. Riwayat parkir: Menampilkan daftar kendaraan yang telah parkir beserta waktu masuk, keluar, biaya, dan status pembayaran.

---

Terima kasih telah menggunakan Sistem Parkir Gambir!
