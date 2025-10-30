# ai_engine.py
import pandas as pd
import random
from config import EXCEL_PATH, SHEET_PON, SHEET_LOWONGAN, SHEET_HASIL

# --- Tahap 1 & 2: Pemetaan Profil ke PON TIK (Simulasi) ---
def map_profile_to_pon(profile_text: str):
    """
    SIMULASI: Memetakan teks profil (CV) ke okupasi di PON TIK.
    Di dunia nyata: Ini akan menggunakan Semantic Search (Vector DB) + LLM RAG.
    Kita akan melakukan matching keyword sederhana.
    """
    print(f"Memetakan profil: {profile_text[:50]}...")
    
    # Membaca data PON TIK sebagai referensi
    df_pon = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_PON)
    
    # Simulasi: Cukup pilih satu okupasi secara acak sebagai hasil
    # TODO: Ganti ini dengan logic semantic search (misal: FAISS + Sentence-Transformers)
    # untuk mencocokkan 'profile_text' dengan 'Kuk_Keywords' di df_pon.
    
    if df_pon.empty:
        return None, 0, "Database PON TIK kosong"
        
    random_row = df_pon.sample(n=1).iloc[0]
    okupasi_id = random_row['OkupasiID']
    okupasi_nama = random_row['Okupasi']
    skor_kecocokan = random.uniform(0.65, 0.95) # Skor acak
    
    # Simulasi Gap Keterampilan
    gap_keterampilan = "Python (Advanced), Manajemen Proyek, Cloud Computing (AWS/GCP)"
    
    print(f"Hasil Pemetaan: {okupasi_nama} (Skor: {skor_kecocokan:.2f})")
    
    return okupasi_id, okupasi_nama, skor_kecocokan, gap_keterampilan

# --- Tahap 3: Pembuatan Soal Asesmen (Simulasi) ---
def generate_assessment_questions(okupasi_id: str):
    """
    SIMULASI: Membuat soal asesmen berdasarkan okupasi.
    Di dunia nyata: Ini akan menggunakan LLM (Automated Question Generation/AQG)
    berdasarkan Unit Kompetensi & KUK dari data PON TIK.
    """
    print(f"Membuat soal untuk Okupasi ID: {okupasi_id}...")
    
    # TODO: Ganti dengan logic AQG berbasis LLM
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
            "jawaban_benar": None # Perlu evaluasi manual atau AI
        }
    ]
    return questions

# --- Tahap 4: Validasi Asesmen (Simulasi) ---
def validate_assessment(answers: dict):
    """
    SIMULASI: Menilai jawaban asesmen.
    Di dunia nyata: Ini akan lebih kompleks, mungkin menggunakan AI untuk menilai esai.
    """
    print(f"Memvalidasi jawaban: {answers}...")
    
    # TODO: Implementasikan logic penilaian yang sebenarnya
    skor = random.randint(60, 95) # Skor acak
    level = "Menengah" if skor > 75 else "Junior"
    
    print(f"Hasil Asesmen: Skor {skor}, Level {level}")
    return skor, level

# --- Tahap 5: Rekomendasi (Simulasi) ---
def get_recommendations(okupasi_id: str, gap_keterampilan: str):
    """
    SIMULASI: Memberikan rekomendasi pekerjaan dan pelatihan.
    Di dunia nyata: Ini akan menggunakan Hybrid Recommendation System (LLM + Collaborative Filtering)
    """
    print(f"Mencari rekomendasi untuk {okupasi_id}...")
    
    # 1. Rekomendasi Pekerjaan
    df_lowongan = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_LOWONGAN)
    
    # TODO: Ganti ini dengan logic matching (bisa semantic search) antara
    # deskripsi lowongan dengan profil/okupasi talenta.
    # Kita hanya ambil 3 lowongan acak untuk demo.
    if df_lowongan.empty:
        rekomendasi_pekerjaan = []
    else:
        rekomendasi_pekerjaan = df_lowongan.sample(n=min(3, len(df_lowongan))).to_dict('records')
        
    # 2. Rekomendasi Pelatihan (berdasarkan gap)
    # TODO: Ganti ini dengan pencarian ke database kursus/pelatihan
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
    Di dunia nyata: Ini akan menjalankan query agregasi (Clustering, Trend Analysis)
    pada sheet 'Hasil_Pemetaan_Asesmen' dan 'Talenta'.
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