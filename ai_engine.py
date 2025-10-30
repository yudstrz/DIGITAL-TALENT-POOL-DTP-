# ai_engine.py
import pandas as pd
import random
import re
# --- PERBAIKAN: Kembali menggunakan config untuk .xlsx ---
from config import (
    EXCEL_PATH, SHEET_PON, SHEET_LOWONGAN, SHEET_HASIL, SHEET_TALENTA
)
# ----------------------------------------------------
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- PERBAIKAN: Kembali ke 'load_excel_sheet' ---
def load_excel_sheet(file_path, sheet_name):
    """
    Fungsi bantuan untuk membaca sheet Excel dengan aman.
    """
    try:
        # header=1 berarti nama kolom ada di BARIS KEDUA (indeks 1)
        # Ini sesuai dengan metadata file Anda (estimatedRowsAboveHeader: 1)
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        
        df.columns = df.columns.str.strip()
        df = df.fillna('') 
        return df
    except FileNotFoundError:
        st.error(f"Gagal memuat file: '{file_path}'. Pastikan file ada di folder 'data/'.")
        return None
    except Exception as e:
        # Ini akan menangkap error jika sheet-nya tidak ada
        st.error(f"Gagal memuat sheet '{sheet_name}'. Pastikan nama sheet di file Excel dan config.py sama. Error: {e}")
        return None
# --------------------------------------------------

def initialize_ai_engine():
    """
    Satu kali setup. Membangun "database vektor" (simulasi)
    dari file Excel.
    """
    if st.session_state.ai_initialized:
        return True # Sudah di-load

    try:
        # --- PERBAIKAN: Membaca sheet dari .xlsx ---
        df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
        if df_pon is None or df_pon.empty:
            st.error(f"Data sheet '{SHEET_PON}' tidak bisa dimuat atau kosong.")
            return False
            
        df_jobs = load_excel_sheet(EXCEL_PATH, SHEET_LOWONGAN)
        if df_jobs is None: 
            st.warning(f"Sheet '{SHEET_LOWONGAN}' tidak ditemukan. Rekomendasi pekerjaan tidak akan berfungsi.")
            df_jobs = pd.DataFrame(columns=['OkupasiID', 'Deskripsi_Pekerjaan', 'Posisi', 'Perusahaan', 'Keterampilan_Dibutuhkan'])
        # -----------------------------------------

        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        pon_corpus = df_pon['Okupasi'] + ' ' + df_pon['Unit_Kompetensi'] + ' ' + df_pon['Kuk_Keywords']
        job_corpus = df_jobs['Posisi'] + ' ' + df_jobs['Deskripsi_Pekerjaan'] + ' ' + df_jobs['Keterampilan_Dibutuhkan']

        if pon_corpus.empty and job_corpus.empty:
             st.error("Data PON dan Lowongan kosong, tidak bisa melatih model AI.")
             return False
        
        full_corpus = pd.concat([pon_corpus, job_corpus])
        vectorizer.fit(full_corpus)

        if not pon_corpus.empty:
            st.session_state.pon_vectors = vectorizer.transform(pon_corpus)
            st.session_state.pon_data = df_pon
        
        if not job_corpus.empty:
            st.session_state.job_vectors = vectorizer.transform(job_corpus)
            st.session_state.job_data = df_jobs

        st.session_state.vectorizer = vectorizer
        st.session_state.ai_initialized = True
        print("--- AI Engine Berhasil Diinisialisasi (Simulasi Vector DB) ---")
        return True

    except KeyError as e:
        st.error(f"Error saat inisialisasi AI Engine: KeyError {e}.")
        st.error(f"Ini berarti kolom {e} tidak ditemukan. Pastikan ejaan di baris 2 Excel Anda sudah benar.")
        if 'df_pon' in locals() and df_pon is not None:
             st.error(f"Kolom yang terbaca dari '{SHEET_PON}' adalah: {list(df_pon.columns)}")
        st.session_state.ai_initialized = False
        return False
    except Exception as e:
        st.error(f"Error saat inisialisasi AI Engine: {e}")
        st.session_state.ai_initialized = False
        return False

# ... (Sisa file ai_engine.py tetap sama) ...

def extract_profile_entities(raw_cv: str):
    words = set(re.findall(r'\b\w{4,}\b', raw_cv.lower()))
    profile_text = ' '.join(words)
    print(f"Hasil Ekstraksi (Simulasi): {profile_text[:100]}...")
    return profile_text


def map_profile_to_pon(profile_text: str):
    print(f"Memetakan profil (Tahap 2): {profile_text[:50]}...")
    
    if not st.session_state.ai_initialized or st.session_state.pon_vectors is None:
        st.error("AI Engine belum siap atau data PON TIK kosong. Coba refresh.")
        return None, None, 0, ""

    try:
        query_vector = st.session_state.vectorizer.transform([profile_text])
        scores = cosine_similarity(query_vector, st.session_state.pon_vectors)
        best_match_index = scores.argmax()
        best_score = scores[0, best_match_index]
        
        pon_data = st.session_state.pon_data.iloc[best_match_index]
        okupasi_id = pon_data['OkupasiID']
        okupasi_nama = pon_data['Okupasi']
        
        gap_keterampilan = "Cloud Computing (AWS/GCP), CI/CD Pipelines, Manajemen Proyek Agile"
        
        print(f"Hasil Pemetaan: {okupasi_nama} (Skor: {best_score:.2f})")
        
        return okupasi_id, okupasi_nama, best_score, gap_keterampilan

    except Exception as e:
        st.error(f"Error di Tahap 2 (Pemetaan): {e}. Mungkin data PON TIK kosong?")
        return None, None, 0, ""

def generate_assessment_questions(okupasi_id: str):
    print(f"Membuat soal (Tahap 3) untuk Okupasi ID: {okupasi_id}...")
    
    questions = [
        {"id": "q1", "teks": f"Skenario {okupasi_id}: Anda diminta mengoptimalkan query database...", "tipe": "pilihan_ganda", "opsi": ["Menambah Indeks", "Mengecek Query Plan", "Denormalisasi", "Upgrade Server"], "jawaban_benar": "Mengecek Query Plan"},
        {"id": "q2", "teks": "Bagaimana Anda menangani konflik dependensi library Python...", "tipe": "pilihan_ganda", "opsi": ["Pakai Docker", "Pakai Virtual Environment (venv)", "Force install", "Semua benar tergantung konteks"], "jawaban_benar": "Semua benar tergantung konteks"},
        {"id": "q3", "teks": "Jelaskan arsitektur microservices yang Anda usulkan...", "tipe": "esai_singkat", "jawaban_benar": None}
    ]
    return questions

def validate_assessment(answers: dict):
    print(f"Memvalidasi jawaban (Tahap 4): {answers}...")
    
    skor = random.randint(60, 95)
    level = "Menengah"
    
    if skor > 90:
        level = "Ahli (Rekomendasi Asesmen Lanjutan)"
    elif skor > 70:
        level = "Menengah"
    else:
        level = "Junior"
        
    print(f"Hasil Asesmen: Skor {skor}, Level {level}")
    return skor, level

def get_recommendations(okupasi_id: str, gap_keterampilan: str, profil_teks: str):
    print(f"Mencari rekomendasi (Tahap 5) untuk {okupasi_id}...")
    
    rekomendasi_pekerjaan = []
    rekomendasi_pelatihan = []

    if not st.session_state.ai_initialized:
        st.error("AI Engine belum siap.")
        return [], []

    try:
        if st.session_state.job_vectors is not None and st.session_state.job_vectors.shape[0] > 0:
            query_vector = st.session_state.vectorizer.transform([profil_teks])
            scores = cosine_similarity(query_vector, st.session_state.job_vectors)
            top_3_indices = scores.argsort()[0][-3:][::-1]
            rekomendasi_pekerjaan = st.session_state.job_data.iloc[top_3_indices].to_dict('records')
        else:
            print("Tidak ada data lowongan untuk direkomendasikan.")
            
    except Exception as e:
        st.error(f"Error saat mencari rekomendasi pekerjaan: {e}")

    try:
        gaps = [g.strip() for g in gap_keterampilan.split(',')]
        for gap in gaps:
            rekomendasi_pelatihan.append(
                f"Kursus Intensif: {gap} (dicari dari database pelatihan)"
            )
    except Exception as e:
        st.error(f"Error saat membuat rekomendasi pelatihan: {e}")

    return rekomendasi_pekerjaan, rekomendasi_pelatihan

def get_national_dashboard_data():
    print("Mengambil data dashboard (Tahap 6 & 7)...")
    
    # --- PERBAIKAN: Membaca sheet dari .xlsx ---
    df_hasil = load_excel_sheet(EXCEL_PATH, SHEET_HASIL)
    df_talenta = load_excel_sheet(EXCEL_PATH, SHEET_TALENTA)
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
    # ----------------------------------------

    if df_hasil is None or df_talenta is None or df_pon is None:
        st.error("Gagal memuat data untuk dashboard (Hasil, Talenta, atau PON).")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    distribusi_okupasi = pd.DataFrame(columns=['Okupasi', 'Jumlah_Talenta']).set_index('Okupasi')
    if 'OkupasiID_Mapped' in df_hasil.columns and 'OkupasiID' in df_pon.columns:
        if not df_hasil.empty and not df_pon.empty:
            merged_data = pd.merge(df_hasil, df_pon, left_on='OkupasiID_Mapped', right_on='OkupasiID', how='left')
            distribusi_okupasi_series = merged_data['Okupasi'].value_counts()
            if not distribusi_okupasi_series.empty:
                distribusi_okupasi = distribusi_okupasi_series.reset_index()
                distribusi_okupasi.columns = ['Okupasi', 'Jumlah_Talenta']
                distribusi_okupasi = distribusi_okupasi.set_index('Okupasi')

    sebaran_lokasi = pd.DataFrame()
    if 'Lokasi' in df_talenta.columns and not df_talenta.empty:
        lokasi_counts = df_talenta['Lokasi'].value_counts().reset_index()
        lokasi_counts.columns = ['Lokasi', 'Jumlah']
        
        lokasi_map = {
            "Jakarta": {"lat": -6.20, "lon": 106.81},
            "Bandung": {"lat": -6.91, "lon": 107.61},
            "Surabaya": {"lat": -7.25, "lon": 112.75},
            "Yogyakarta": {"lat": -7.79, "lon": 110.36},
            "Medan": {"lat": 3.59, "lon": 98.67}
        }

        lokasi_counts['lat'] = lokasi_counts['Lokasi'].apply(lambda x: lokasi_map.get(x, {}).get('lat', 0))
        lokasi_counts['lon'] = lokasi_counts['Lokasi'].apply(lambda x: lokasi_map.get(x, {}).get('lon', 0))
        lokasi_counts = lokasi_counts[lokasi_counts['lat'] != 0]
        lokasi_counts['size'] = lokasi_counts['Jumlah']
        sebaran_lokasi = lokasi_counts
    
    skill_gap_umum = pd.DataFrame({
        'Keterampilan': ['Cloud Computing', 'AI/ML', 'Project Management', 'Data Governance'],
        'Jumlah_Gap': [random.randint(30, 150) for _ in range(4)]
    }).set_index('Keterampilan')

    return distribusi_okupasi, sebaran_lokasi, skill_gap_umum
