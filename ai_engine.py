# ai_engine.py
import pandas as pd
import random
import re
from config import EXCEL_PATH, SHEET_PON, SHEET_LOWONGAN, SHEET_HASIL, SHEET_TALENTA
import streamlit as st

# --- Simulasi AI/ML dengan Scikit-learn ---
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Cache (Simulasi Database Vektor yang sudah di-load) ---
# Ini akan menyimpan "model" AI kita agar tidak perlu di-load ulang setiap kali
if 'ai_initialized' not in st.session_state:
    st.session_state.ai_initialized = False
    st.session_state.vectorizer = None # Model untuk mengubah teks jadi vektor
    st.session_state.pon_vectors = None   # Vektor dari semua okupasi PON
    st.session_state.pon_data = None      # Data PON (OkupasiID, Nama, dll)
    st.session_state.job_vectors = None   # Vektor dari semua lowongan kerja
    st.session_state.job_data = None      # Data Lowongan

def load_excel_sheet(file_path, sheet_name):
    """Fungsi bantuan untuk membaca Excel dengan aman dan membersihkan nama kolom."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        # Mengisi data kosong (NaN) dengan string kosong agar tidak error
        df = df.fillna('') 
        return df
    except Exception as e:
        st.error(f"Gagal memuat sheet '{sheet_name}'. Pastikan file dan sheet ada. Error: {e}")
        return None

def initialize_ai_engine():
    """
    Satu kali setup. Membangun "database vektor" (simulasi)
    dari file Excel. Ini meniru proses 'embedding' data PON TIK.
    """
    if st.session_state.ai_initialized:
        return True # Sudah di-load

    try:
        # 1. Load data PON TIK dari Excel
        df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
        if df_pon is None or df_pon.empty:
            st.error("Data PON TIK tidak bisa dimuat atau kosong.")
            return False
            
        # 2. Load data Lowongan dari Excel
        df_jobs = load_excel_sheet(EXCEL_PATH, SHEET_LOWONGAN)
        if df_jobs is None: 
            df_jobs = pd.DataFrame(columns=['OkupasiID', 'Deskripsi_Pekerjaan', 'Posisi', 'Perusahaan']) # Buat kosong jika tidak ada

        # 3. Buat "Embedding" (Simulasi dengan TF-IDF)
        # Di dunia nyata: Ganti TfidfVectorizer dengan SentenceTransformer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        # Gabungkan teks dari PON TIK untuk "dipelajari" oleh model
        pon_corpus = df_pon['Okupasi'] + ' ' + df_pon['Unit_Kompetensi'] + ' ' + df_pon['Kuk_Keywords']
        job_corpus = df_jobs['Posisi'] + ' ' + df_jobs['Deskripsi_Pekerjaan'] + ' ' + df_jobs['Keterampilan_Dibutuhkan']

        # Latih model-nya (fit) pada semua data teks yang ada
        if pon_corpus.empty and job_corpus.empty:
             st.error("Data PON dan Lowongan kosong, tidak bisa melatih model AI.")
             return False
        
        full_corpus = pd.concat([pon_corpus, job_corpus])
        vectorizer.fit(full_corpus)

        # 4. Ubah data PON TIK menjadi vektor dan simpan
        if not pon_corpus.empty:
            st.session_state.pon_vectors = vectorizer.transform(pon_corpus)
            st.session_state.pon_data = df_pon
        
        # 5. Ubah data Lowongan menjadi vektor dan simpan
        if not job_corpus.empty:
            st.session_state.job_vectors = vectorizer.transform(job_corpus)
            st.session_state.job_data = df_jobs

        st.session_state.vectorizer = vectorizer
        st.session_state.ai_initialized = True
        print("--- AI Engine Berhasil Diinisialisasi (Simulasi Vector DB) ---")
        return True

    except Exception as e:
        st.error(f"Error saat inisialisasi AI Engine: {e}")
        st.session_state.ai_initialized = False
        return False

# --- TAHAP 1: Input Profil Talenta (Ekstraksi) ---
def extract_profile_entities(raw_cv: str):
    """
    SIMULASI: Ekstraksi entitas (NER/LLM) dari CV mentah.
    Di dunia nyata: Ini akan memanggil LLM (OpenAI/Llama) atau model NER (spaCy)
    untuk mengekstrak 'skills', 'experience', 'education' secara terstruktur.
    
    Untuk demo ini, kita hanya akan mengekstrak kata-kata kunci.
    """
    # Simulasi sederhana: ambil semua kata unik yang panjangnya > 3
    words = set(re.findall(r'\b\w{4,}\b', raw_cv.lower()))
    profile_text = ' '.join(words)
    
    # Di dunia nyata, outputnya bisa berupa dict:
    # return {
    #     "skills": ["Python", "SQL", "Data Analysis"],
    #     "experience": ["Data Analyst at PT ABC (2 years)"],
    #     "education": ["S1 Teknik Informatika UGM"]
    # }
    
    print(f"Hasil Ekstraksi (Simulasi): {profile_text[:100]}...")
    return profile_text # Mengembalikan string yang sudah dibersihkan


# --- TAHAP 2: Pemetaan Awal ke PON TIK (Semantic Search) ---
def map_profile_to_pon(profile_text: str):
    """
    SIMULASI: Mencocokkan profil ke PON TIK menggunakan Semantic Search (Vector DB).
    Di dunia nyata: Ini akan menggunakan FAISS/Milvus + SentenceTransformer.
    Kita simulasi pakai TF-IDF + Cosine Similarity.
    """
    print(f"Memetakan profil (Tahap 2): {profile_text[:50]}...")
    
    if not st.session_state.ai_initialized:
        st.error("AI Engine belum siap. Coba refresh.")
        return None, None, 0, ""

    try:
        # 1. Ubah query (profil) menjadi vektor
        query_vector = st.session_state.vectorizer.transform([profile_text])
        
        # 2. Hitung skor kecocokan (Cosine Similarity)
        # Ini adalah inti dari "Semantic Search"
        scores = cosine_similarity(query_vector, st.session_state.pon_vectors)
        
        # 3. Dapatkan hasil terbaik
        best_match_index = scores.argmax()
        best_score = scores[0, best_match_index]
        
        # 4. Ambil data okupasi dari hasil terbaik
        pon_data = st.session_state.pon_data.iloc[best_match_index]
        okupasi_id = pon_data['OkupasiID']
        okupasi_nama = pon_data['Okupasi']
        
        # 5. Simulasi RAG (Retrieval-Augmented Generation) untuk Skill Gap
        # Di dunia nyata: LLM akan membandingkan 'profile_text' dengan 'Kuk_Keywords'
        # dan 'Unit_Kompetensi' dari 'pon_data' untuk mencari gap.
        # Simulasi: Kita anggap saja ada gap
        gap_keterampilan = "Cloud Computing (AWS/GCP), CI/CD Pipelines, Manajemen Proyek Agile"
        
        print(f"Hasil Pemetaan: {okupasi_nama} (Skor: {best_score:.2f})")
        
        return okupasi_id, okupasi_nama, best_score, gap_keterampilan

    except Exception as e:
        st.error(f"Error di Tahap 2 (Pemetaan): {e}. Mungkin data PON TIK kosong?")
        return None, None, 0, ""

# --- TAHAP 3: Asesmen Kompetensi (AQG) ---
def generate_assessment_questions(okupasi_id: str):
    """
    SIMULASI: Membuat soal asesmen berbasis AI (AQG).
    Di dunia nyata: Ini akan memanggil LLM + Few-Shot Prompting.
    Contoh Prompt: "Kamu adalah asesor. Buat 3 soal pilihan ganda
    berbasis skenario kerja nyata untuk Unit Kompetensi [ambil dari Excel]..."
    """
    print(f"Membuat soal (Tahap 3) untuk Okupasi ID: {okupasi_id}...")
    
    # Kita tetap pakai data simulasi, tapi logikanya sudah dijelaskan
    questions = [
        {"id": "q1", "teks": f"Skenario {okupasi_id}: Anda diminta mengoptimalkan query database. Apa langkah pertama Anda?", "tipe": "pilihan_ganda", "opsi": ["Menambah Indeks", "Mengecek Query Plan", "Denormalisasi", "Upgrade Server"], "jawaban_benar": "Mengecek Query Plan"},
        {"id": "q2", "teks": "Bagaimana Anda menangani konflik dependensi library Python di proyek tim?", "tipe": "pilihan_ganda", "opsi": ["Pakai Docker", "Pakai Virtual Environment (venv)", "Force install", "Semua benar tergantung konteks"], "jawaban_benar": "Semua benar tergantung konteks"},
        {"id": "q3", "teks": "Jelaskan arsitektur microservices yang Anda usulkan untuk kasus e-commerce.", "tipe": "esai_singkat", "jawaban_benar": None}
    ]
    return questions

# --- TAHAP 4: Validasi Level & Probing (Adaptive) ---
def validate_assessment(answers: dict):
    """
    SIMULASI: Menilai jawaban dan validasi level.
    Di dunia nyata: Ini akan jadi Adaptive Assessment Engine.
    Jika skor > 90, AI akan memicu 'Probing Loop' dengan soal
    (dari LLM-based generator) yang lebih sulit (level di atasnya).
    Jika skor < 50, AI akan memberi soal yang lebih mudah.
    """
    print(f"Memvalidasi jawaban (Tahap 4): {answers}...")
    
    # Simulasi: Cukup hitung skor acak
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

# --- TAHAP 5: Rekomendasi Terpersonalisasi (Hybrid) ---
def get_recommendations(okupasi_id: str, gap_keterampilan: str, profil_teks: str):
    """
    SIMULASI: Hybrid Recommendation System (LLM + Rule-based).
    Kita akan simulasi Content-Based Filtering (pakai TF-IDF) untuk
    lowongan kerja.
    """
    print(f"Mencari rekomendasi (Tahap 5) untuk {okupasi_id}...")
    
    rekomendasi_pekerjaan = []
    rekomendasi_pelatihan = []

    if not st.session_state.ai_initialized:
        st.error("AI Engine belum siap.")
        return [], []

    # 1. Rekomendasi Pekerjaan (Content-Based Filtering)
    try:
        if st.session_state.job_vectors is not None and st.session_state.job_vectors.shape[0] > 0:
            # Ubah profil talenta menjadi vektor
            query_vector = st.session_state.vectorizer.transform([profil_teks])
            
            # Cari lowongan yang paling mirip dengan profil
            scores = cosine_similarity(query_vector, st.session_state.job_vectors)
            
            # Ambil 3 lowongan terbaik (indeksnya)
            top_3_indices = scores.argsort()[0][-3:][::-1]
            
            rekomendasi_pekerjaan = st.session_state.job_data.iloc[top_3_indices].to_dict('records')
        else:
            print("Tidak ada data lowongan untuk direkomendasikan.")
            
    except Exception as e:
        st.error(f"Error saat mencari rekomendasi pekerjaan: {e}")

    # 2. Rekomendasi Pelatihan (Rule-Based dari Skill Gap)
    # Di dunia nyata: Ini bisa memanggil LLM ("Beri 3 link kursus
    # untuk skill gap: [gap_keterampilan]")
    try:
        gaps = [g.strip() for g in gap_keterampilan.split(',')]
        for gap in gaps:
            rekomendasi_pelatihan.append(
                f"Kursus Intensif: {gap} (dicari dari database pelatihan)"
            )
    except Exception as e:
        st.error(f"Error saat membuat rekomendasi pelatihan: {e}")

    return rekomendasi_pekerjaan, rekomendasi_pelatihan

# --- TAHAP 6 & 7: Pemetaan Talenta & Dashboard Publik ---
def get_national_dashboard_data():
    """
    SIMULASI: Clustering, Agregasi, dan Analisis Tren (Tahap 6 & 7).
    Ini sekarang akan membaca data *aktual* dari sheet 'Hasil' dan 'Talenta'
    untuk membuat agregasi.
    """
    print("Mengambil data dashboard (Tahap 6 & 7)...")
    
    df_hasil = load_excel_sheet(EXCEL_PATH, SHEET_HASIL)
    df_talenta = load_excel_sheet(EXCEL_PATH, SHEET_TALENTA)
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)

    if df_hasil is None or df_talenta is None or df_pon is None:
        st.error("Gagal memuat data untuk dashboard.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # --- 1. Distribusi Okupasi ---
    # Gabungkan hasil mapping dengan data PON untuk dapat NAMA okupasi
    if 'OkupasiID_Mapped' in df_hasil.columns and 'OkupasiID' in df_pon.columns:
        merged_data = pd.merge(df_hasil, df_pon, left_on='OkupasiID_Mapped', right_on='OkupasiID', how='left')
        distribusi_okupasi = merged_data['Okupasi'].value_counts().reset_index()
        distribusi_okupasi.columns = ['Okupasi', 'Jumlah_Talenta']
        distribusi_okupasi = distribusi_okupasi.set_index('Okupasi')
    else:
        distribusi_okupasi = pd.DataFrame(columns=['Okupasi', 'Jumlah_Talenta']).set_index('Okupasi')

    # --- 2. Sebaran Lokasi (Simulasi Clustering) ---
    # Di dunia nyata: Kita akan cluster (K-Means) lat/lon.
    # Simulasi: Kita hitung saja jumlah talenta per lokasi
    if 'Lokasi' in df_talenta.columns:
        lokasi_counts = df_talenta['Lokasi'].value_counts().reset_index()
        lokasi_counts.columns = ['Lokasi', 'Jumlah']
        # Simulasi Lat/Lon untuk peta
        # (Ini data dummy, idealnya ada tabel master Lokasi -> Lat/Lon)
        lokasi_map = {
            "Jakarta": {"lat": -6.20, "lon": 106.81},
            "Bandung": {"lat": -6.91, "lon": 107.61},
            "Surabaya": {"lat": -7.25, "lon": 112.75},
            "Yogyakarta
