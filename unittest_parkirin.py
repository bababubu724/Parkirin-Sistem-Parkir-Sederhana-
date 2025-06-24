import unittest
from unittest.mock import patch, MagicMock, mock_open
import datetime
import json
import os
import customtkinter as ctk

from app_parkirin import App, TARIF_MOBIL, TARIF_MOTOR, DENDA_TIKET_HILANG, NAMA_FILE_RIWAYAT

class TestAppGUI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Metode ini berjalan sekali sebelum semua tes.
        """
        # Atur variabel lingkungan untuk menandakan mode tes
        os.environ['IS_TESTING'] = '1'
        
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        """Metode ini berjalan sekali setelah semua tes selesai."""
        cls.root.destroy()
        # Hapus variabel lingkungan setelah selesai
        os.environ.pop('IS_TESTING', None)

    def setUp(self):
        """
        Metode ini berjalan sebelum setiap tes individu.
        """
        self.app = App()
        # Nonaktifkan after-loop agar tidak mengganggu test runner
        self.app.after = MagicMock()

    def tearDown(self):
        """
        Metode ini berjalan setelah setiap tes individu.
        """
        self.app.destroy()

    def test_hitung_biaya_motor(self):
        self.assertEqual(self.app.hitung_biaya('Motor', 1), TARIF_MOTOR['jam_pertama'])
        biaya_3_jam = TARIF_MOTOR['jam_pertama'] + (2 * TARIF_MOTOR['per_jam_berikutnya'])
        self.assertEqual(self.app.hitung_biaya('Motor', 3), biaya_3_jam)

    def test_hitung_biaya_mobil(self):
        self.assertEqual(self.app.hitung_biaya('Mobil', 1), TARIF_MOBIL['jam_pertama'])
        biaya_5_jam = TARIF_MOBIL['jam_pertama'] + (4 * TARIF_MOBIL['per_jam_berikutnya'])
        self.assertEqual(self.app.hitung_biaya('Mobil', 5), biaya_5_jam)

    def test_get_nopol_from_entries(self):
        p1, p2, p3 = MagicMock(), MagicMock(), MagicMock()
        p1.get.return_value = " B "
        p2.get.return_value = " 1234 "
        p3.get.return_value = " XYZ "
        self.assertEqual(self.app.get_nopol_from_entries(p1, p2, p3), "B 1234 XYZ")

    def test_get_nopol_from_entries_gagal_jika_kosong(self):
        p1, p2, p3 = MagicMock(), MagicMock(), MagicMock()
        p1.get.return_value = "B"
        p2.get.return_value = ""
        p3.get.return_value = "XYZ"
        self.assertIsNone(self.app.get_nopol_from_entries(p1, p2, p3))

    def test_inisialisasi_id_terakhir(self):
        self.app.riwayat_parkir = []
        self.assertEqual(self.app.inisialisasi_id_terakhir(), 0)

        self.app.riwayat_parkir = [{'id': 1}, {'id': 5}, {'id': 3}]
        self.assertEqual(self.app.inisialisasi_id_terakhir(), 5)

    @patch('app_parkirin.messagebox')
    @patch('app_parkirin.App.buka_dialog_checkin_sukses_modern')
    def test_event_checkin_sukses(self, mock_dialog_sukses, mock_messagebox):
        nopol = "B 1234 TST"
        jenis = "Mobil"
        self.app.entry_nopol_in_1.insert(0, "B")
        self.app.entry_nopol_in_2.insert(0, "1234")
        self.app.entry_nopol_in_3.insert(0, "TST")
        self.app.opsi_jenis.set(jenis)
        self.app.event_checkin()
        self.assertIn(nopol, self.app.kendaraan_terparkir)
        self.assertEqual(self.app.kendaraan_terparkir[nopol]['jenis'], jenis)
        mock_dialog_sukses.assert_called_once()
        mock_messagebox.showerror.assert_not_called()

    @patch('app_parkirin.messagebox')
    def test_event_checkin_gagal_jika_sudah_parkir(self, mock_messagebox):
        nopol = "B 5678 ERR"
        self.app.kendaraan_terparkir[nopol] = {'jenis': 'Motor', 'waktu_masuk': datetime.datetime.now()}
        self.app.entry_nopol_in_1.insert(0, "B")
        self.app.entry_nopol_in_2.insert(0, "5678")
        self.app.entry_nopol_in_3.insert(0, "ERR")
        self.app.opsi_jenis.set("Motor")
        self.app.event_checkin()
        mock_messagebox.showerror.assert_called_once_with("Error", f"Kendaraan {nopol} sudah terparkir.")

    def test_proses_pembayaran_final(self):
        waktu_masuk = datetime.datetime(2024, 6, 24, 10, 0, 0)
        waktu_keluar = datetime.datetime(2024, 6, 24, 12, 0, 0)
        nopol = "D 4 VNL"
        total_biaya = 13000
        self.app.kendaraan_terparkir[nopol] = {'jenis': 'Mobil', 'waktu_masuk': waktu_masuk}
        self.app.last_parkir_id = 5

        with patch.object(self.app, 'simpan_riwayat_ke_json') as mock_simpan:
            self.app.proses_pembayaran_final(nopol, total_biaya, 'Cash', 'Lunas', waktu_keluar)
            mock_simpan.assert_called_once()

        self.assertNotIn(nopol, self.app.kendaraan_terparkir)
        self.assertEqual(self.app.last_parkir_id, 6)
        self.assertEqual(len(self.app.riwayat_parkir), 1)
        riwayat_terbaru = self.app.riwayat_parkir[0]
        self.assertEqual(riwayat_terbaru['id'], 6)
        self.assertEqual(riwayat_terbaru['status'], 'Lunas')

    @patch("builtins.open", new_callable=mock_open)
    def test_simpan_riwayat_ke_json(self, mock_file):
        waktu_sekarang = datetime.datetime.now()
        self.app.riwayat_parkir = [{'id': 1, 'nopol': 'Z 9999 ZZ', 'jenis': 'Motor', 'waktu_masuk': waktu_sekarang, 'waktu_keluar': waktu_sekarang, 'total_biaya': 3000, 'status': 'Lunas', 'metode_bayar': 'E-Money'}]
        self.app.simpan_riwayat_ke_json()
        mock_file.assert_called_with(NAMA_FILE_RIWAYAT, 'w')
        written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
        hasil_json = json.loads(written_data)
        self.assertEqual(hasil_json[0]['waktu_masuk'], waktu_sekarang.isoformat())

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)