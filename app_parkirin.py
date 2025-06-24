# --- Mengimpor pustaka-pustaka yang dibutuhkan ---
import customtkinter as ctk # untuk membuat aplikasi GUI dengan tampilan modern
import datetime # untuk bekerja dengan tanggal dan waktu
import math # untuk operasi matematika (perhitungan)
from tkinter import messagebox, StringVar # untuk menampilkan pesan kesalahan atau informasi pada pengguna
from PIL import Image # untuk memanggil gambar
import json # untuk menangani file json (membaca, mengedit, dan menyimpan data format JSON)
import os # untuk berinteraksi dengan sistem operasi

# --- Path Absolut untuk Aset-Aset ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_MOBIL = os.path.join(BASE_DIR, "assets", "cctv_mobil.jpg")
PATH_MOTOR = os.path.join(BASE_DIR, "assets", "cctv_motor.jpg")
PATH_BG_MENU = os.path.join(BASE_DIR, "assets", "gambar_main.png")

# --- Komponen Kustom Spinbox ---
class CTkSpinbox(ctk.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 start_value: int = 1,
                 min_value: int = 0,
                 max_value: int = 100,
                 **kwargs):

        super().__init__(*args, width=width, height=height, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = start_value
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.subtract_button = ctk.CTkButton(self, text="▼", width=height-6, height=height-6, command=self.decrement_value)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)
        
        self.entry = ctk.CTkEntry(self, width=width-(height*2), height=height, border_width=0, justify="center")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        
        self.add_button = ctk.CTkButton(self, text="▲", width=height-6, height=height-6, command=self.increment_value)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)
        
        self.set(start_value)

    def increment_value(self):
        new_value = self.current_value + 1
        if new_value > self.max_value: new_value = self.min_value
        self.set(new_value)

    def decrement_value(self):
        new_value = self.current_value - 1
        if new_value < self.min_value: new_value = self.max_value
        self.set(new_value)

    def get(self) -> int:
        try: 
            return int(self.entry.get())
        except ValueError: 
            return self.current_value

    def set(self, value: int):
        self.current_value = max(self.min_value, min(value, self.max_value))
        self.entry.delete(0, "end")
        self.entry.insert(0, str(self.current_value))

    def configure_state(self, state: str):
        self.entry.configure(state=state)
        self.add_button.configure(state=state)
        self.subtract_button.configure(state=state)

# --- Konfigurasi Aplikasi ---
TARIF_MOTOR = { "jam_pertama": 3000, "per_jam_berikutnya": 2000 }
TARIF_MOBIL = { "jam_pertama": 5000, "per_jam_berikutnya": 4000 }
DENDA_TIKET_HILANG = 50000
NAMA_FILE_RIWAYAT = os.path.join(BASE_DIR, "history", "riwayat_parkir.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Parkir Gambir")
        self.geometry("1200x800")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.kendaraan_terparkir = {}
        self.riwayat_parkir = self.muat_riwayat_dari_json()
        self.last_parkir_id = self.inisialisasi_id_terakhir()
        self.frame_kiri = ctk.CTkFrame(self, width=400, border_width=2, fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.frame_kiri.place(relx=0.02, rely=0.04, relwidth=0.35, relheight=0.92)
        self.frame_kanan = ctk.CTkFrame(self, border_width=2)
        self.frame_kanan.place(relx=0.38, rely=0.04, relwidth=0.6, relheight=0.75)
        self.status_box = ctk.CTkTextbox(self, height=100, font=("Consolas", 12), border_width=2)
        self.status_box.place(relx=0.38, rely=0.805, relwidth=0.6, relheight=0.155)
        self.setup_left_panel()
        self.setup_right_panel()
        self.update_daftar_kendaraan()
        self.update_riwayat()
        self.update_clock()

    def inisialisasi_id_terakhir(self):
        if not self.riwayat_parkir:
            return 0
        max_id = max(item.get('id', 0) for item in self.riwayat_parkir)
        # print(f"Inisialisasi ID terakhir ke: {max_id}")
        return max_id

    def muat_riwayat_dari_json(self):
        if not os.path.exists(NAMA_FILE_RIWAYAT):
            # print("File riwayat tidak ditemukan. Memulai dengan riwayat kosong.")
            return []
        try:
            with open(NAMA_FILE_RIWAYAT, 'r') as f:
                data_mentah = json.load(f)
                for item in data_mentah:
                    item['waktu_masuk'] = datetime.datetime.fromisoformat(item['waktu_masuk'])
                    item['waktu_keluar'] = datetime.datetime.fromisoformat(item['waktu_keluar'])
                # print(f"Berhasil memuat {len(data_mentah)} data riwayat dari {NAMA_FILE_RIWAYAT}")
                return data_mentah
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            # print(f"Error membaca file JSON: {e}. Memulai dengan riwayat kosong.")
            return []

    def simpan_riwayat_ke_json(self):
        data_untuk_disimpan = []
        for item in self.riwayat_parkir:
            item_copy = item.copy()
            item_copy['waktu_masuk'] = item['waktu_masuk'].isoformat()
            item_copy['waktu_keluar'] = item['waktu_keluar'].isoformat()
            data_untuk_disimpan.append(item_copy)
            
        history_dir = os.path.dirname(NAMA_FILE_RIWAYAT)
        os.makedirs(history_dir, exist_ok=True)

        with open(NAMA_FILE_RIWAYAT, 'w') as f:
            json.dump(data_untuk_disimpan, f, indent=4)
        # print(f"Riwayat berhasil disimpan ke {NAMA_FILE_RIWAYAT}")

    def setup_left_panel(self):
        self.frame_kiri.grid_rowconfigure(0, weight=0)
        self.frame_kiri.grid_rowconfigure(1, weight=1)
        self.frame_kiri.grid_columnconfigure(0, weight=1)
        self.frame_kiri.configure(fg_color="black")

        self.label_waktu = ctk.CTkLabel(self.frame_kiri, text="", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        self.label_waktu.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")

        action_area_container = ctk.CTkFrame(self.frame_kiri, corner_radius=10, border_width=0, fg_color="black")
        action_area_container.grid(row=1, column=0, padx=10, pady=(10, 20), sticky="nsew")
        action_area_container.grid_rowconfigure(0, weight=0)
        action_area_container.grid_rowconfigure(1, weight=1)
        action_area_container.grid_columnconfigure(0, weight=1)

        image_top_frame = ctk.CTkFrame(action_area_container, corner_radius=10, fg_color="black")
        image_top_frame.grid(row=0, column=0, padx=0, pady=(20, 10), sticky="ew")
        image_top_frame.grid_rowconfigure(0, weight=1)
        image_top_frame.grid_columnconfigure(0, weight=1)

        # Memuat gambar latar belakang menu, kecuali dalam mode testing
        if not os.environ.get('IS_TESTING'):
            try:
                menu_bg_image = ctk.CTkImage(Image.open(PATH_BG_MENU), size=(360, 50))
                menu_bg_label = ctk.CTkLabel(image_top_frame, text="", image=menu_bg_image)
                menu_bg_label.pack(expand=True, fill="both", padx=10, pady=(0, 15))
            except Exception as e:
                # print(f"Gagal memuat gambar menu: {e}")
                fallback_label_img = ctk.CTkLabel(image_top_frame, text="[Gagal Memuat Gambar Menu]", text_color="gray", font=ctk.CTkFont(size=14))
                fallback_label_img.pack(pady=20, padx=20)
        else:
            # Jika dalam mode testing, tampilkan label pengganti secara langsung
            fallback_label_img = ctk.CTkLabel(image_top_frame, text="[Mode Testing - Gambar Dinonaktifkan]", text_color="gray", font=ctk.CTkFont(size=14))
            fallback_label_img.pack(pady=20, padx=20)


        self.main_selection_frame = ctk.CTkFrame(action_area_container, fg_color="black")
        self.checkin_frame = ctk.CTkFrame(action_area_container, fg_color="black")
        self.checkout_frame = ctk.CTkFrame(action_area_container, fg_color="black")

        button_font = ctk.CTkFont(size=16, weight="bold")
        ctk.CTkButton(self.main_selection_frame, text="MASUKKAN KENDARAAN (CHECK-IN)", command=self.show_checkin_view, height=200, font=button_font, fg_color="blue", text_color="white").pack(pady=(10, 15), fill="x", expand=True)
        ctk.CTkButton(self.main_selection_frame, text="KELUARKAN KENDARAAN (CHECK-OUT)", command=self.show_checkout_view, height=200, font=button_font, fg_color="red", text_color="white", hover_color="darkred").pack(pady=(10, 15), fill="x", expand=True)

        self.main_selection_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
        self.checkin_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
        self.checkout_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))

        self.populate_checkin_frame()
        self.populate_checkout_frame()
        self.show_main_view()

    def populate_checkin_frame(self):
        wrapper = ctk.CTkFrame(self.checkin_frame, fg_color=("#dbdbdb", "#2b2b2b"), corner_radius=8)
        wrapper.pack(expand=True, fill="both", pady=(5, 5), padx=0)
        ctk.CTkLabel(wrapper, text="Check-in Kendaraan", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10,15), padx=20, fill="x")
        ctk.CTkLabel(wrapper, text="Nomor Polisi", anchor="w").pack(anchor="w", padx=20)
        nopol_frame_in = ctk.CTkFrame(wrapper, fg_color="transparent")
        nopol_frame_in.pack(fill="x", padx=20, pady=(0, 15))
        self.entry_nopol_in_1 = ctk.CTkEntry(nopol_frame_in, placeholder_text="B"); self.entry_nopol_in_1.pack(side="left", padx=(0,5), fill="x", expand=True)
        self.entry_nopol_in_2 = ctk.CTkEntry(nopol_frame_in, placeholder_text="1234"); self.entry_nopol_in_2.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_nopol_in_3 = ctk.CTkEntry(nopol_frame_in, placeholder_text="XYZ"); self.entry_nopol_in_3.pack(side="left", padx=(5,0), fill="x", expand=True)
        ctk.CTkLabel(wrapper, text="Jenis Kendaraan", anchor="w").pack(anchor="w", padx=20)
        self.opsi_jenis = ctk.CTkOptionMenu(wrapper, values=["Mobil", "Motor"]); self.opsi_jenis.pack(pady=(5,15), padx=20, fill="x", expand=True)
        ctk.CTkLabel(wrapper, text="Waktu Masuk akan dicatat otomatis.", justify="center").pack(pady=(5,10), padx=20)
        ctk.CTkButton(wrapper, text="Konfirmasi Check-in", command=self.event_checkin, height=40).pack(pady=(15, 10), padx=20, fill="x")
        ctk.CTkButton(wrapper, text="Kembali", command=self.show_main_view, fg_color="gray").pack(pady=(0,15), padx=20, fill="x")

    def populate_checkout_frame(self):
        wrapper = ctk.CTkFrame(self.checkout_frame, fg_color="transparent", corner_radius=8)
        wrapper.pack(expand=True, fill="both", pady=0, padx=0)
        ctk.CTkLabel(wrapper, text="Proses Keluar", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=(10,10), padx=20, fill="x")
        ctk.CTkLabel(wrapper, text="Nomor Polisi", anchor="w", text_color="white").pack(anchor="w", padx=20, pady=(10,0))
        nopol_frame_out = ctk.CTkFrame(wrapper, fg_color="transparent")
        nopol_frame_out.pack(fill="x", padx=20, pady=5)
        self.entry_nopol_out_1 = ctk.CTkEntry(nopol_frame_out, placeholder_text="B"); self.entry_nopol_out_1.pack(side="left", padx=(0,5), fill="x", expand=True)
        self.entry_nopol_out_2 = ctk.CTkEntry(nopol_frame_out, placeholder_text="1234"); self.entry_nopol_out_2.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_nopol_out_3 = ctk.CTkEntry(nopol_frame_out, placeholder_text="XYZ"); self.entry_nopol_out_3.pack(side="left", padx=(5,0), fill="x", expand=True)
        self.manual_time_var = ctk.StringVar(value="off")
        self.manual_time_check = ctk.CTkCheckBox(wrapper, text="Gunakan Waktu Keluar Manual", variable=self.manual_time_var, onvalue="on", offvalue="off", command=self.toggle_manual_time_widgets, text_color="white")
        self.manual_time_check.pack(anchor="w", padx=20, pady=(15, 5))
        self.manual_time_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        self.manual_time_frame.pack(fill="x", padx=20, pady=5)
        now = datetime.datetime.now()
        date_frame = ctk.CTkFrame(self.manual_time_frame, fg_color="transparent"); date_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(date_frame, text="Tgl/Bln/Thn:", width=80, text_color="white").pack(side="left")
        self.spin_tgl_out = CTkSpinbox(date_frame, min_value=1, max_value=31, start_value=now.day); self.spin_tgl_out.pack(side="left", padx=5, fill="x", expand=True)
        self.spin_bln_out = CTkSpinbox(date_frame, min_value=1, max_value=12, start_value=now.month); self.spin_bln_out.pack(side="left", padx=5, fill="x", expand=True)
        self.spin_thn_out = CTkSpinbox(date_frame, min_value=2020, max_value=2030, start_value=now.year); self.spin_thn_out.pack(side="left", padx=5, fill="x", expand=True)
        time_frame = ctk.CTkFrame(self.manual_time_frame, fg_color="transparent"); time_frame.pack(fill="x")
        ctk.CTkLabel(time_frame, text="Jam/Mnt/Dtk:", width=80, text_color="white").pack(side="left")
        self.spin_jam_out = CTkSpinbox(time_frame, min_value=0, max_value=23, start_value=now.hour); self.spin_jam_out.pack(side="left", padx=5, fill="x", expand=True)
        self.spin_mnt_out = CTkSpinbox(time_frame, min_value=0, max_value=59, start_value=now.minute); self.spin_mnt_out.pack(side="left", padx=5, fill="x", expand=True)
        self.spin_dtk_out = CTkSpinbox(time_frame, min_value=0, max_value=59, start_value=now.second); self.spin_dtk_out.pack(side="left", padx=5, fill="x", expand=True)
        self.toggle_manual_time_widgets()
        self.check_denda_var = ctk.StringVar(value="off")
        self.check_denda = ctk.CTkCheckBox(wrapper, text="Tiket Hilang? (Denda Berlaku)", variable=self.check_denda_var, onvalue="on", offvalue="off", text_color="white")
        self.check_denda.pack(pady=15, padx=20, anchor="w")
        ctk.CTkButton(wrapper, text="Hitung Biaya & Tampilkan Rincian", command=self.event_checkout, fg_color="#D32F2F", hover_color="#B71C1C", height=40).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(wrapper, text="Kembali", command=self.show_main_view, fg_color="gray").pack(pady=(0,10), padx=20, fill="x")

    def show_main_view(self): 
        self.checkin_frame.grid_remove()
        self.checkout_frame.grid_remove()
        self.main_selection_frame.grid()
    
    def show_checkin_view(self): 
        self.main_selection_frame.grid_remove()
        self.checkout_frame.grid_remove()
        self.checkin_frame.grid()
    
    def show_checkout_view(self): 
        self.main_selection_frame.grid_remove()
        self.checkin_frame.grid_remove()
        self.checkout_frame.grid()
    
    def event_checkin(self):
        nopol = self.get_nopol_from_entries(self.entry_nopol_in_1, self.entry_nopol_in_2, self.entry_nopol_in_3)
        if not nopol: return messagebox.showerror("Error", "Nomor polisi harus diisi lengkap!")
        if nopol in self.kendaraan_terparkir: return messagebox.showerror("Error", f"Kendaraan {nopol} sudah terparkir.")
        
        jenis = self.opsi_jenis.get()
        waktu_masuk = datetime.datetime.now()
        self.kendaraan_terparkir[nopol] = {'jenis': jenis, 'waktu_masuk': waktu_masuk}
        
        tiket_virtual = (f"   Nomor Polisi    : {nopol}\n"
                         f"   Jenis Kendaraan : {jenis}\n\n"
                         f"   Waktu Masuk     : {waktu_masuk.strftime('%d %b %Y, %H:%M:%S')}")
        
        gambar_path = PATH_MOBIL if jenis == "Mobil" else PATH_MOTOR
        self.buka_dialog_checkin_sukses_modern(tiket_virtual, gambar_path)
        self.tulis_status(f"✅ Check-in sukses: {nopol} ({waktu_masuk.strftime('%H:%M:%S')})")
        self.update_daftar_kendaraan()
        self.entry_nopol_in_1.delete(0, 'end'); self.entry_nopol_in_2.delete(0, 'end'); self.entry_nopol_in_3.delete(0, 'end')
        self.show_main_view()

    def buka_dialog_checkin_sukses_modern(self, info_tiket, path_gambar):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Konfirmasi Tiket")
        dialog.geometry("500x650")
        dialog.transient(self); dialog.grab_set(); dialog.resizable(False, False)
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Check-in Berhasil!", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        image_container = ctk.CTkFrame(main_frame, corner_radius=10, border_width=2)
        image_container.pack(pady=10, padx=20, fill="x")
        
        if not os.environ.get('IS_TESTING'):
            try:
                image_ctk = ctk.CTkImage(Image.open(path_gambar), size=(400, 250))
                image_label = ctk.CTkLabel(image_container, text="", image=image_ctk)
                image_label.pack(pady=10, padx=10)
            except Exception as e:
                error_text = f"Gagal memuat gambar:\n{path_gambar}"
                error_label = ctk.CTkLabel(image_container, text=error_text, text_color="gray", height=250, wraplength=380, font=ctk.CTkFont(size=14))
                error_label.pack(pady=10, padx=10)

        ticket_info_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#EEEEEE", "#333333"))
        ticket_info_frame.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(ticket_info_frame, text="--- TIKET PARKIR VIRTUAL ---", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        ctk.CTkLabel(ticket_info_frame, text=info_tiket, font=("Consolas", 14), justify="left").pack(pady=10, padx=20, anchor="w")
        ctk.CTkLabel(ticket_info_frame, text="--- Harap simpan bukti ini ---", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray").pack(pady=(5, 15))
        
        ctk.CTkLabel(main_frame, text="Terima Kasih & Selamat Jalan!", font=ctk.CTkFont(size=14)).pack(pady=(0, 20))
        ctk.CTkButton(main_frame, text="OK", command=dialog.destroy, width=150, height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, side="bottom")

    def toggle_manual_time_widgets(self):
        state = "normal" if self.manual_time_var.get() == "on" else "disabled"
        for spinbox in [self.spin_tgl_out, self.spin_bln_out, self.spin_thn_out, self.spin_jam_out, self.spin_mnt_out, self.spin_dtk_out]:
            spinbox.configure_state(state)

    def get_checkout_time(self):
        if self.manual_time_var.get() == "off":
            return datetime.datetime.now()
        try:
            thn, bln, tgl = self.spin_thn_out.get(), self.spin_bln_out.get(), self.spin_tgl_out.get()
            jam, mnt, dtk = self.spin_jam_out.get(), self.spin_mnt_out.get(), self.spin_dtk_out.get()
            return datetime.datetime(thn, bln, tgl, jam, mnt, dtk)
        except ValueError:
            messagebox.showerror("Error Waktu", f"Tanggal tidak valid: {tgl}/{bln}/{thn}.")
            return None
    
    def event_checkout(self):
        nopol = self.get_nopol_from_entries(self.entry_nopol_out_1, self.entry_nopol_out_2, self.entry_nopol_out_3)
        if not nopol: return messagebox.showerror("Error", "Nomor polisi checkout harus diisi!")
        if nopol not in self.kendaraan_terparkir: return messagebox.showerror("Error", f"Kendaraan {nopol} tidak ditemukan.")
        
        waktu_keluar_aktual = self.get_checkout_time()
        if waktu_keluar_aktual is None: return
        
        data_parkir = self.kendaraan_terparkir[nopol]
        waktu_masuk = data_parkir['waktu_masuk']
        
        if waktu_keluar_aktual < waktu_masuk: return messagebox.showerror("Error Waktu", "Waktu keluar tidak boleh lebih awal dari waktu masuk.")
        
        is_denda = self.check_denda_var.get() == "on"
        total_biaya, info_pembayaran, status_checkout = 0, "", ""
        
        if is_denda:
            status_checkout, total_biaya = "Denda Tiket Hilang", DENDA_TIKET_HILANG
            info_pembayaran = f"-- Rincian Denda --\n\n Nopol: {nopol}\n Status: {status_checkout}\n\n TOTAL DENDA : Rp {total_biaya:10,.0f}"
        else:
            status_checkout = "Lunas"
            durasi = waktu_keluar_aktual - waktu_masuk
            total_jam = math.ceil(durasi.total_seconds() / 3600)
            if total_jam < 1: total_jam = 1
            
            hari, sisa_detik = divmod(int(durasi.total_seconds()), 86400)
            jam, sisa_detik = divmod(sisa_detik, 3600)
            menit, _ = divmod(sisa_detik, 60)
            durasi_str = f"{hari} hari, {jam} jam, {menit} menit"
            
            total_biaya = self.hitung_biaya(data_parkir['jenis'], total_jam)
            info_pembayaran = (f"-- Rincian Pembayaran --\n\n"
                               f"Nopol         : {nopol}\n"
                               f"Waktu Masuk   : {waktu_masuk.strftime('%d-%b %H:%M')}\n"
                               f"Waktu Keluar  : {waktu_keluar_aktual.strftime('%d-%b %H:%M')}\n"
                               f"Durasi        : {durasi_str}\n"
                               f"(Dihitung {total_jam} jam)\n"
                               f"-------------------------\n"
                               f"TOTAL BIAYA   : Rp {total_biaya:10,.0f}\n"
                               f"-------------------------")
        
        self.buka_dialog_pembayaran(nopol, info_pembayaran, total_biaya, status_checkout, waktu_keluar_aktual)

    def buka_dialog_pembayaran(self, nopol, info, biaya, status, waktu_keluar_valid):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Konfirmasi Pembayaran")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("450x350")
        
        ctk.CTkLabel(dialog, text=info, font=("Consolas", 14), justify="left").pack(pady=20, padx=20)
        
        metode_bayar_var = StringVar(value="Cash")
        radio_frame = ctk.CTkFrame(dialog, fg_color="transparent"); 
        radio_frame.pack(pady=10)
        
        ctk.CTkRadioButton(radio_frame, text="Tunai (Cash)", variable=metode_bayar_var, value="Cash").pack(side="left", padx=10)
        ctk.CTkRadioButton(radio_frame, text="Cashless (E-Money)", variable=metode_bayar_var, value="E-Money").pack(side="left", padx=10)
        
        konfirmasi = lambda: (self.proses_pembayaran_final(nopol, biaya, metode_bayar_var.get(), status, waktu_keluar_valid), dialog.destroy())
        ctk.CTkButton(dialog, text="Konfirmasi & Selesaikan Transaksi", command=konfirmasi).pack(pady=20, padx=20)

    def proses_pembayaran_final(self, nopol, total_biaya, metode, status, waktu_keluar):
        self.last_parkir_id += 1
        data_lama = self.kendaraan_terparkir[nopol]
        
        riwayat_entry = {
            'id': self.last_parkir_id,
            'nopol': nopol, 
            'jenis': data_lama['jenis'], 
            'waktu_masuk': data_lama['waktu_masuk'], 
            'waktu_keluar': waktu_keluar, 
            'total_biaya': total_biaya, 
            'status': status,
            'metode_bayar': metode
        }

        self.riwayat_parkir.insert(0, riwayat_entry)
        self.simpan_riwayat_ke_json()
        del self.kendaraan_terparkir[nopol]
        
        self.tulis_status(f"✅ Checkout {nopol} selesai. Status: {status}. Bayar: Rp {total_biaya:,.0f} ({metode})")
        
        self.update_daftar_kendaraan(); 
        self.update_riwayat()
        
        self.entry_nopol_out_1.delete(0, 'end'); 
        self.entry_nopol_out_2.delete(0, 'end'); 
        self.entry_nopol_out_3.delete(0, 'end')
        self.check_denda.deselect()
        self.manual_time_check.deselect()
        self.toggle_manual_time_widgets()
        self.show_main_view()
    
    def setup_right_panel(self):
        self.frame_kanan.grid_columnconfigure(0, weight=1)
        self.frame_kanan.grid_rowconfigure(0, weight=1)
        
        tabview = ctk.CTkTabview(self.frame_kanan)
        tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tab_aktif = tabview.add("Parkir Aktif")
        tab_riwayat = tabview.add("Riwayat Parkir")
        
        self.scroll_aktif = ctk.CTkScrollableFrame(tab_aktif); self.scroll_aktif.pack(expand=True, fill="both", padx=5, pady=5)
        self.scroll_riwayat = ctk.CTkScrollableFrame(tab_riwayat); self.scroll_riwayat.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.tulis_status("Selamat Datang di Sistem Parkir Gambir !\n---")

    def update_clock(self): 
        self.label_waktu.configure(text=datetime.datetime.now().strftime("%A, %d %B %Y | %H:%M:%S"))
        self.after(1000, self.update_clock)

    def get_nopol_from_entries(self, p1, p2, p3):
        part1 = p1.get().strip()
        part2 = p2.get().strip()
        part3 = p3.get().strip()
        if not all([part1, part2, part3]):
            return None
        nopol = f"{part1} {part2} {part3}".upper()
        return nopol
    
    def hitung_biaya(self, jenis, total_jam): 
        tarif = TARIF_MOBIL if jenis == 'Mobil' else TARIF_MOTOR
        return tarif['jam_pertama'] if total_jam <= 1 else tarif['jam_pertama'] + (total_jam - 1) * tarif['per_jam_berikutnya']
    
    def tulis_status(self, pesan): 
        self.status_box.configure(state="normal")
        self.status_box.delete("0.0", "end")
        self.status_box.insert("0.0", pesan)
        self.status_box.configure(state="disabled")
    
    def update_daftar_kendaraan(self):
        for widget in self.scroll_aktif.winfo_children(): 
            widget.destroy()
        
        if not self.kendaraan_terparkir: 
            ctk.CTkLabel(self.scroll_aktif, text="-- Tidak ada kendaraan aktif --", text_color="gray").pack(pady=10)
        else:
            header = ctk.CTkFrame(self.scroll_aktif, fg_color="transparent")
            header.pack(fill="x", padx=5)
            header.grid_columnconfigure((0, 1, 2), weight=1)
            
            ctk.CTkLabel(header, text="No. Pol", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
            ctk.CTkLabel(header, text="Jenis", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
            ctk.CTkLabel(header, text="Waktu Masuk", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)

            for nopol, data in sorted(self.kendaraan_terparkir.items(), key=lambda item: item[1]['waktu_masuk'], reverse=True):
                item = ctk.CTkFrame(self.scroll_aktif); item.pack(fill="x", padx=5, pady=3)
                item.grid_columnconfigure((0, 1, 2), weight=1)
                ctk.CTkLabel(item, text=nopol).grid(row=0, column=0)
                ctk.CTkLabel(item, text=data['jenis']).grid(row=0, column=1)
                ctk.CTkLabel(item, text=data['waktu_masuk'].strftime('%d-%b %H:%M:%S')).grid(row=0, column=2)
    
    def update_riwayat(self):
        for widget in self.scroll_riwayat.winfo_children(): widget.destroy()
        
        if not self.riwayat_parkir:
            ctk.CTkLabel(self.scroll_riwayat, text="-- Riwayat masih kosong --", text_color="gray").pack(pady=10)
            return
        
        header = ctk.CTkFrame(self.scroll_riwayat, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=(2,5))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=3)
        header.grid_columnconfigure(2, weight=3)
        header.grid_columnconfigure(3, weight=3)
        header.grid_columnconfigure(4, weight=2)
        header.grid_columnconfigure(5, weight=2)

        ctk.CTkLabel(header, text="ID", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="No. Pol", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(header, text="Waktu Keluar", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(header, text="Total Biaya", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, sticky="w")
        ctk.CTkLabel(header, text="Status", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, sticky="w")
        ctk.CTkLabel(header, text="Metode", font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, sticky="w")

        for data in self.riwayat_parkir:
            item = ctk.CTkFrame(self.scroll_riwayat)
            item.pack(fill="x", padx=5, pady=3)
            item.grid_columnconfigure(0, weight=1)
            item.grid_columnconfigure(1, weight=3)
            item.grid_columnconfigure(2, weight=3)
            item.grid_columnconfigure(3, weight=3)
            item.grid_columnconfigure(4, weight=2)
            item.grid_columnconfigure(5, weight=2)
            
            id_val = data.get('id', '-')
            nopol_val = data.get('nopol', '-')
            waktu_keluar_val = data.get('waktu_keluar').strftime('%d-%b %H:%M') if data.get('waktu_keluar') else '-'
            biaya_val = f"Rp {data.get('total_biaya', 0):,.0f}"
            status_val = data.get('status', '-')
            metode_val = data.get('metode_bayar', '-')

            ctk.CTkLabel(item, text=id_val, anchor="w").grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(item, text=nopol_val, anchor="w").grid(row=0, column=1, sticky="ew")
            ctk.CTkLabel(item, text=waktu_keluar_val, anchor="w").grid(row=0, column=2, sticky="ew")
            ctk.CTkLabel(item, text=biaya_val, anchor="w").grid(row=0, column=3, sticky="ew")
            ctk.CTkLabel(item, text=status_val, anchor="w").grid(row=0, column=4, sticky="ew")
            ctk.CTkLabel(item, text=metode_val, anchor="w").grid(row=0, column=5, sticky="ew")

if __name__ == "__main__":
    app = App()
    app.mainloop()