import unittest
from unittest.mock import patch, MagicMock
import os
import datetime
import sys
import json

# Menambahkan direktori utama (Parkirin) ke sys.path agar Python bisa menemukan app_parkirin.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app_parkirin import App, PATH_MOBIL, PATH_MOTOR, PATH_BG_MENU

class TestParkirApp(unittest.TestCase):

    @patch('app_parkirin.messagebox.showerror')  # Mocking untuk menampilkan pesan error
    @patch('app_parkirin.CTkImage')  # Mocking CTkImage untuk menghindari memuat gambar
    def test_event_checkin(self, mock_ctk_image, mock_showerror):
        # Mocking gambar agar tidak mempengaruhi unit test
        mock_ctk_image.return_value = MagicMock()
        
        app = App()
        # Simulasikan input nomor polisi yang valid
        app.entry_nopol_in_1.insert(0, 'B')
        app.entry_nopol_in_2.insert(0, '1234')
        app.entry_nopol_in_3.insert(0, 'XYZ')
        
        # Mock fungsi untuk memastikan dialog check-in sukses
        with patch.object(app, 'buka_dialog_checkin_sukses_modern') as mock_buka_dialog:
            app.event_checkin()
            
            # Pastikan kendaraan berhasil ditambahkan
            self.assertIn('B 1234 XYZ', app.kendaraan_terparkir)
            # Pastikan fungsi dialog check-in sukses dipanggil
            mock_buka_dialog.assert_called_once()

    @patch('app_parkirin.messagebox.showerror')
    def test_event_checkin_duplicate_vehicle(self, mock_showerror):
        app = App()
        # Simulasikan kendaraan yang sudah ada dalam parkiran
        app.kendaraan_terparkir['B 1234 XYZ'] = {'jenis': 'Mobil', 'waktu_masuk': '2025-06-23 10:00:00'}
        
        # Simulasikan input nomor polisi yang sudah ada
        app.entry_nopol_in_1.insert(0, 'B')
        app.entry_nopol_in_2.insert(0, '1234')
        app.entry_nopol_in_3.insert(0, 'XYZ')
        
        # Coba check-in kendaraan yang sudah terparkir
        app.event_checkin()
        
        # Pastikan error message ditampilkan
        mock_showerror.assert_called_with("Error", "Kendaraan B 1234 XYZ sudah terparkir.")

    @patch('app_parkirin.messagebox.showerror')
    @patch('app_parkirin.messagebox.showinfo')  # Untuk memverifikasi dialog sukses check-out
    @patch('app_parkirin.CTkImage')  # Mocking untuk CTkImage
    def test_event_checkout(self, mock_ctk_image, mock_showinfo, mock_showerror):
        # Mocking gambar agar tidak mempengaruhi unit test
        mock_ctk_image.return_value = MagicMock()
        
        app = App()
        # Simulasikan kendaraan yang sudah terparkir
        app.kendaraan_terparkir['B 1234 XYZ'] = {'jenis': 'Mobil', 'waktu_masuk': datetime.datetime(2025, 6, 23, 10, 0, 0)}
        
        # Simulasikan input nomor polisi
        app.entry_nopol_out_1.insert(0, 'B')
        app.entry_nopol_out_2.insert(0, '1234')
        app.entry_nopol_out_3.insert(0, 'XYZ')

        # Simulasikan waktu checkout
        with patch('app_parkirin.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2025, 6, 23, 12, 0, 0)  # Menggunakan datetime objek
            app.event_checkout()

        # Verifikasi bahwa dialog pembayaran dipanggil
        mock_showinfo.assert_called_once()

        # Verifikasi riwayat parkir dan kendaraan terparkir
        self.assertNotIn('B 1234 XYZ', app.kendaraan_terparkir)
        self.assertEqual(len(app.riwayat_parkir), 1)

    @patch('app_parkirin.messagebox.showerror')
    def test_event_checkout_vehicle_not_found(self, mock_showerror):
        app = App()
        # Simulasikan input nomor polisi yang tidak ada dalam parkiran
        app.entry_nopol_out_1.insert(0, 'B')
        app.entry_nopol_out_2.insert(0, '1234')
        app.entry_nopol_out_3.insert(0, 'XYZ')

        # Coba checkout kendaraan yang tidak ada
        app.event_checkout()

        # Pastikan error message ditampilkan
        mock_showerror.assert_called_with("Error", "Kendaraan B 1234 XYZ tidak ditemukan.")

    def test_hitung_biaya(self):
        app = App()
        # Tes biaya untuk mobil
        biaya_mobil = app.hitung_biaya('Mobil', 2)  # 2 jam
        self.assertEqual(biaya_mobil, 9000)  # 5000 untuk jam pertama, 4000 untuk jam kedua
        
        # Tes biaya untuk motor
        biaya_motor = app.hitung_biaya('Motor', 3)  # 3 jam
        self.assertEqual(biaya_motor, 7000)  # 3000 untuk jam pertama, 2000 untuk jam kedua, 2000 untuk jam ketiga

    @patch('app_parkirin.json.load')
    def test_muat_riwayat_dari_json(self, mock_json_load):
        app = App()
        # Simulasikan data riwayat yang ada di file JSON
        mock_json_load.return_value = [
            {
                "id": 1,
                "nopol": "B 1234 XYZ",
                "jenis": "Mobil",
                "waktu_masuk": "2025-06-23T10:00:00",
                "waktu_keluar": "2025-06-23T12:00:00",
                "total_biaya": 9000,
                "status": "Lunas",
                "metode_bayar": "Cash"
            }
        ]
        
        # Tes fungsi memuat riwayat dari JSON
        riwayat = app.muat_riwayat_dari_json()
        
        # Pastikan riwayat dimuat dengan benar
        self.assertEqual(len(riwayat), 1)
        self.assertEqual(riwayat[0]['nopol'], 'B 1234 XYZ')

    @patch('app_parkirin.json.dump')
    def test_simpan_riwayat_ke_json(self, mock_json_dump):
        app = App()
        # Tambahkan riwayat parkir untuk disimpan
        app.riwayat_parkir = [{'id': 1, 'nopol': 'B 1234 XYZ', 'jenis': 'Mobil', 'waktu_masuk': '2025-06-23 10:00:00', 'waktu_keluar': '2025-06-23 12:00:00', 'total_biaya': 9000, 'status': 'Lunas', 'metode_bayar': 'Cash'}]
        
        # Tes fungsi menyimpan riwayat ke file JSON
        app.simpan_riwayat_ke_json()
        
        # Verifikasi bahwa json.dump dipanggil untuk menyimpan riwayat
        mock_json_dump.assert_called_once()

    @patch('app_parkirin.messagebox.showerror')
    def test_get_checkout_time_manual(self, mock_showerror):
        app = App()
        # Simulasikan input tanggal dan waktu manual untuk checkout
        app.manual_time_var.set("on")
        app.spin_tgl_out.set(23)
        app.spin_bln_out.set(6)
        app.spin_thn_out.set(2025)
        app.spin_jam_out.set(12)
        app.spin_mnt_out.set(30)
        app.spin_dtk_out.set(0)
        
        # Ambil waktu checkout manual
        checkout_time = app.get_checkout_time()
        
        # Verifikasi waktu checkout yang diambil
        self.assertEqual(checkout_time, datetime.datetime(2025, 6, 23, 12, 30))

    # --- Test Format Riwayat Parkir ---
    @patch('app_parkirin.CTkLabel')
    def test_riwayat_format(self, mock_ctk_label):
        app = App()
        # Menambahkan riwayat parkir
        app.riwayat_parkir = [{'id': 1, 'nopol': 'B 1234 XYZ', 'jenis': 'Mobil', 'waktu_masuk': '2025-06-23 10:00:00', 'waktu_keluar': '2025-06-23 12:00:00', 'total_biaya': 9000, 'status': 'Lunas', 'metode_bayar': 'Cash'}]
        
        # Panggil fungsi untuk update riwayat
        app.update_riwayat()
        
        # Verifikasi apakah label riwayat dibuat dengan benar
        mock_ctk_label.assert_called_with(text="ID", font=ctk.CTkFont(weight="bold"))

    # --- Test Kinerja dengan Data Lebih Banyak ---
    def test_kinerja_dengan_data_banyak(self):
        app = App()
        # Menambahkan banyak kendaraan untuk menguji kinerja
        for i in range(1000):
            app.kendaraan_terparkir[f"B {i} XYZ"] = {'jenis': 'Mobil', 'waktu_masuk': datetime.datetime(2025, 6, 23, 10, 0, 0)}
        
        # Memperbarui daftar kendaraan
        app.update_daftar_kendaraan()
        
        # Verifikasi jumlah kendaraan dalam daftar
        self.assertEqual(len(app.kendaraan_terparkir), 1000)

if __name__ == "__main__":
    unittest.main()
