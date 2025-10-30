# ai_engine.py
import pandas as pd
import random
from config import EXCEL_PATH, SHEET_PON, SHEET_LOWONGAN, SHEET_HASIL
import streamlit as st # Import streamlit untuk menampilkan error

# --- Fungsi Bantuan untuk Membaca Excel dengan Aman ---
def load_excel_sheet(file_path, sheet_name):
    """
    Fungsi internal untuk membaca sheet Excel dengan aman.
    Ini akan membersihkan spasi di nama kolom.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # --- INI ADALAH PERBAIKANNYA ---
        # Membersihkan spasi di awal/akhir dari semua nama kolom
        # Ini akan memperbaiki error 'OkupasiID ' (dengan spasi)
        df.columns = df.columns.str.strip()
        # ---------------------------------
        
        return df
        
    except FileNotFoundError:
        st.error(f"Error: File database tidak ditemukan di {file_path}. Pastikan ada di folder 'data/'.")
        return None
    except Exception as e:
        # Menangkap error jika sheet-nya tidak ada
        st.error(f"Error: Gagal membaca sheet '{sheet_name}' dari file Excel. Detail: {e}")
        return None

# --- Tahap 1 & 2: Pemetaan Profil ke PON TIK (Simulasi) ---
def map_profile_to_pon(profile_text: str):
    """
    SIMULASI: Memetakan teks profil (CV) ke okupasi di PON TIK.
    """
    print(f"Memetakan profil: {profile_text[:50]}...")
    
    # Membaca data PON TIK sebagai referensi (menggunakan fungsi baru)
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
    
    # Cek apakah df berhasil di-load
    if df_pon is None:
        return None, 0, "Gagal memuat database PON TIK. Cek error di atas."
        
    if df_pon.empty:
        return None, 0, "Database PON TIK kosong."
    
    try:
        # Ambil sampel acak
        random_row = df_pon.sample(n=1).iloc[0]
        
        # Kode ini sekarang aman dari 'KeyError' akibat spasi
        okupasi_id = random_row['OkupasiID']
        okupasi_nama = random_row['Okupasi']
        
        skor_kecocokan = random.uniform(0.65, 0.95)
        gap_keterampilan = "Python (Advanced), Manajemen Proyek, Cloud Computing (AWS/GCP)"
        
        print(f"Hasil Pemetaan: {okupasi_nama} (Skor: {skor_kecocokan:.2f})")
        
        return okupasi_id, okupasi_nama, skor_kecocokan, gap_keterampilan

    except KeyError as e:
        # --- PERBAIKAN ERROR HANDLING ---
        # Pesan error ini akan muncul jika nama kolomnya *benar-benar* salah eja (bukan spasi)
        st.error(f"FATAL: Kolom {e} tidak ditemukan di sheet 'PON_TIK_Master'.")
        st.error(f"Nama kolom yang ada di file Excel Anda adalah: {list(df_pon.columns)}")
        st.error("SOLUSI: Harap samakan ejaan kolom di file Excel Anda (misal: 'OkupasiID', 'Okupasi').")
        return None, 0, f"Error: Kolom {e} tidak ada."
    except Exception as e:
        st.error(f"Error tidak terduga di map_profile_to_pon: {e}")
        return None, 0, "Error internal."


# --- Tahap 3: Pembuatan Soal Asesmen (Simulasi) ---
def generate_assessment_questions(okupasi_id: str):
    """
    SIMULASI: Membuat soal asesmen berdasarkan okupasi.
    """
    print(f"Membuat soal untuk Okupasi ID: {okupasi_id}...")
    
    questions = [
        {
            "id": "q1",
            "teks": "Jelaskan perbedaan antara SQL dan NoSQL dalam konteks skenario X.",
            "tipe": "pilihan_ganda",
            "opsi": ["Opsi A", "Opsi B", "Opsi C", "Opsi D"],
            "jawaban_benar": "Opsi B"
        },
        {
            "id": "q2",
            "teks": "Bagaimana Anda menangani missing value dalam sebuah dataset?",
            "tipe": "pilihan_ganda",
            "opsi": ["Dihapus", "Diisi mean/median", "Dimodelkan", "Semua benar tergantung konteks"],
            "jawaban_benar": "Semua benar tergantung konteks"
        },
        {
            "id": "q3",
            "teks": "Studi Kasus: Diberikan data penjualan, buatlah visualisasi...",
            "tipe": "esai_singkat",
            "jawaban_benar": None 
        }
    ]
    return questions

# --- Tahap 4: Validasi Asesmen (Simulasi) ---
def validate_assessment(answers: dict):
    """
    SIMULASI: Menilai jawaban asesmen.
    """
    print(f"Memvalidasi jawaban: {answers}...")
    
    skor = random.randint(60, 95)
    level = "Menengah" if skor > 75 else "Junior"
    
    print(f"Hasil Asesmen: Skor {skor}, Level {level}")
    return skor, level

# --- Tahap 5: Rekomendasi (Simulasi) ---
def get_recommendations(okupasi_id: str, gap_keterampilan: str):
    """
    SIMULASI: Memberikan rekomendasi pekerjaan dan pelatihan.
    """
    print(f"Mencari rekomendasi untuk {okupasi_id}...")
    
    # 1. Rekomendasi Pekerjaan (menggunakan fungsi baru)
    df_lowongan = load_excel_sheet(EXCEL_PATH, SHEET_LOWONGAN)
    
    rekomendasi_pekerjaan = []
    if df_lowongan is not None and not df_lowongan.empty:
        try:
            # Pastikan kolom di 'Lowongan_Industri' juga dibersihkan
            rekomendasi_pekerjaan = df_lowongan.sample(n=min(3, len(df_lowongan))).to_dict('records')
        except KeyError as e:
            st.error(f"Error: Kolom {e} tidak ditemukan di sheet 'Lowongan_Industri'.")
            st.error(f"Nama kolom yang ada adalah: {list(df_lowongan.columns)}")
        except Exception as e:
            st.error(f"Error saat memproses lowongan: {e}")
            
    # 2. Rekomendasi Pelatihan (berdasarkan gap)
    rekomendasi_pelatihan = [
        f"Kursus Intensif: {gap_keterampilan.split(',')[0]}",
        f"Sertifikasi: {gap_keterampilan.split(',')[-1]}",
        "Workshop: Komunikasi Efektif untuk Tim Teknis"
    ]
    
    return rekomendasi_pekerjaan, rekomendasi_pelatihan

# --- Tahap 6 & 7: Data Dashboard (Simulasi) ---
def get_national_dashboard_data():
    """
    SIMULASI: Mengambil data agregat untuk dashboard nasional.
    """
    print("Mengambil data dashboard nasional...")
    
    # TODO: Ganti ini dengan agregasi data nyata dari df_hasil dan df_talenta
    
    # Contoh data simulasi
    distribusi_okupasi = pd.DataFrame({
        'Okupasi': ['Data Analyst', 'Web Developer', 'UI/UX Designer', 'Cyber Security'],
        'Jumlah_Talenta': [random.randint(50, 200) for _ in range(4)]
    }).set_index('Okupasi')
    
    sebaran_lokasi = pd.DataFrame({
        'lat': [-6.20, -6.91, -7.25, -7.79],
        'lon': [106.81, 107.61, 112.75, 110.36],
        'size': [random.randint(10, 100) for _ in range(4)] # Mewakili jumlah talenta
    })
    
    skill_gap_umum = pd.DataFrame({
        'Keterampilan': ['Cloud Computing', 'AI/ML', 'Project Management', 'Data Governance'],
        'Jumlah_Gap': [random.randint(30, 150) for _ in range(4)]
    }).set_index('Keterampilan')
    
    return distribusi_okupasi, sebaran_lokasi, skill_gap_umum
