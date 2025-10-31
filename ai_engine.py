# ai_engine.py - Mesin AI untuk DTP
"""
ANALOGI: Ini adalah OTAK dan SISTEM SARAF sistem.
Tugas utama:
1. Membaca database Excel
2. Mengekstrak informasi dari CV
3. Memetakan profil ke okupasi PON TIK
4. Membuat soal asesmen dengan AI
5. Menilai jawaban asesmen
6. Memberikan rekomendasi karier
"""

import pandas as pd
import random
import re
import json
import requests
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    EXCEL_PATH, SHEET_PON, SHEET_LOWONGAN, 
    SHEET_HASIL, SHEET_TALENTA
)

# ========================================
# BAGIAN 1: KONFIGURASI API
# ========================================
"""
ANALOGI: Ini seperti KUNCI untuk membuka pintu ke AI Gemini.
API Key adalah password rahasia yang memberi kita akses.
"""

GEMINI_API_KEY = "AIzaSyCR8xgDIv5oYBaDmMyuGGWjqpFi7U8SGA4"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-flash-latest"

JUMLAH_SOAL = 5  # Berapa soal yang akan dibuat AI


def get_api_keys():
    """
    FUNGSI: Mengambil API key dari secrets atau hardcoded
    ANALOGI: Seperti mencari kunci di laci rahasia
    """
    gemini_key = GEMINI_API_KEY
    
    # Coba ambil dari Streamlit secrets (lebih aman)
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        gemini_key = st.secrets['GEMINI_API_KEY']
    
    return gemini_key


# ========================================
# BAGIAN 2: FUNGSI KOMUNIKASI DENGAN AI
# ========================================

def call_gemini_api(prompt: str) -> str:
    """
    FUNGSI: Mengirim pertanyaan ke AI Gemini dan mendapat jawaban
    
    ANALOGI: Seperti menelepon seorang ahli dan menanyakan sesuatu.
    1. Kita menyiapkan pertanyaan (prompt)
    2. Mengirim melalui internet (POST request)
    3. Menunggu jawaban
    4. Membersihkan jawaban agar bisa dibaca sistem
    
    Args:
        prompt: Pertanyaan/instruksi untuk AI
        
    Returns:
        Jawaban dari AI dalam format teks bersih
    """
    url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    # Instruksi khusus agar AI memberikan JSON yang valid
    json_instruction = """
PENTING: Anda HARUS merespons dengan JSON yang valid.
Format yang diharapkan:
{
  "questions": [
    {"id": "q1", "teks": "...", "opsi": ["...", "..."], "jawaban_benar": "..."}
  ]
}
"""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt + json_instruction}]
        }],
        "generationConfig": {
            "temperature": 0.7,        # Kreativitas (0-1, makin tinggi makin kreatif)
            "maxOutputTokens": 3000    # Panjang maksimal jawaban
        }
    }
    
    try:
        print(f"🔄 Memanggil Gemini API...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Ekstrak teks dari response
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Bersihkan markdown code fence (```json ... ```)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        print(f"✅ Berhasil mendapat response dari Gemini")
        return content
        
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {e}")


# ========================================
# BAGIAN 3: FUNGSI DATABASE
# ========================================

def load_excel_sheet(file_path, sheet_name):
    """
    FUNGSI: Membaca satu sheet dari file Excel
    
    ANALOGI: Seperti membuka buku dan membaca satu bab tertentu.
    Excel = buku, Sheet = bab.
    
    Returns:
        DataFrame pandas (seperti tabel Excel di Python)
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        df.columns = df.columns.str.strip()  # Hapus spasi di nama kolom
        df = df.fillna('')  # Isi sel kosong dengan string kosong
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan: '{file_path}'")
        return None
    except Exception as e:
        st.error(f"Gagal memuat sheet '{sheet_name}': {e}")
        return None


# ========================================
# BAGIAN 4: INISIALISASI AI ENGINE
# ========================================

def initialize_ai_engine():
    """
    FUNGSI: Menyalakan mesin AI untuk pertama kali
    
    ANALOGI: Seperti menyalakan mesin mobil dan memanaskan.
    1. Membaca semua database
    2. Membuat "peta pencarian" (vector database)
    3. Siap untuk dipakai
    
    TEKNIS: Menggunakan TF-IDF Vectorizer untuk semantic search
    - TF-IDF mengubah teks menjadi angka
    - Cosine similarity mencari teks yang mirip
    """
    if st.session_state.get('ai_initialized', False):
        return True

    try:
        # 1. Muat database PON TIK
        df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
        if df_pon is None or df_pon.empty:
            st.error(f"Data '{SHEET_PON}' kosong")
            return False
        
        # 2. Muat database lowongan
        df_jobs = load_excel_sheet(EXCEL_PATH, SHEET_LOWONGAN)
        if df_jobs is None:
            df_jobs = pd.DataFrame(columns=[
                'OkupasiID', 'Deskripsi_Pekerjaan', 
                'Posisi', 'Perusahaan', 'Keterampilan_Dibutuhkan'
            ])

        # 3. Buat vectorizer (pengubah teks jadi angka)
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        # 4. Gabungkan semua teks PON menjadi satu corpus
        pon_corpus = (
            df_pon['Okupasi'] + ' ' + 
            df_pon['Unit_Kompetensi'] + ' ' + 
            df_pon['Kuk_Keywords']
        )
        
        # 5. Gabungkan semua teks lowongan
        job_corpus = (
            df_jobs['Posisi'] + ' ' + 
            df_jobs['Deskripsi_Pekerjaan'] + ' ' + 
            df_jobs['Keterampilan_Dibutuhkan']
        )

        # 6. Gabungkan semua untuk training vectorizer
        full_corpus = pd.concat([pon_corpus, job_corpus])
        vectorizer.fit(full_corpus)

        # 7. Ubah teks PON dan Jobs menjadi vector (angka)
        if not pon_corpus.empty:
            st.session_state.pon_vectors = vectorizer.transform(pon_corpus)
            st.session_state.pon_data = df_pon
        
        if not job_corpus.empty:
            st.session_state.job_vectors = vectorizer.transform(job_corpus)
            st.session_state.job_data = df_jobs

        # 8. Simpan vectorizer untuk dipakai nanti
        st.session_state.vectorizer = vectorizer
        st.session_state.ai_initialized = True
        
        print("✅ AI Engine Berhasil Diinisialisasi")
        return True

    except Exception as e:
        st.error(f"Error inisialisasi AI Engine: {e}")
        return False


# ========================================
# BAGIAN 5: EKSTRAKSI PROFIL
# ========================================

def extract_profile_entities(raw_cv: str):
    """
    FUNGSI: Mengekstrak kata-kata penting dari CV
    
    ANALOGI: Seperti membaca CV dan menggarisbawahi skill penting.
    Contoh: "Python, Machine Learning, 5 tahun pengalaman"
    
    TEKNIS: Named Entity Recognition (NER) sederhana
    - Ambil kata dengan panjang >= 4 huruf
    - Ubah jadi lowercase
    - Gabungkan jadi satu teks
    """
    words = set(re.findall(r'\b\w{4,}\b', raw_cv.lower()))
    profile_text = ' '.join(words)
    print(f"Hasil Ekstraksi: {profile_text[:100]}...")
    return profile_text


# ========================================
# BAGIAN 6: PEMETAAN PROFIL KE PON
# ========================================

def map_profile_to_pon(profile_text: str):
    """
    FUNGSI: Mencari okupasi PON TIK yang paling cocok dengan profil
    
    ANALOGI: Seperti memasukkan puzzle piece ke tempat yang pas.
    1. Profil user = puzzle piece
    2. Database PON = puzzle board
    3. Cari mana yang paling cocok
    
    TEKNIS: Cosine Similarity
    - Hitung jarak antara vector profil dan semua vector PON
    - Pilih yang paling dekat (skor tertinggi)
    
    Returns:
        (okupasi_id, okupasi_nama, skor, gap_keterampilan)
    """
    print(f"Memetakan profil: {profile_text[:50]}...")
    
    if not st.session_state.get('ai_initialized'):
        st.error("AI Engine belum siap")
        return None, None, 0, ""

    try:
        # 1. Ubah profil user jadi vector
        query_vector = st.session_state.vectorizer.transform([profile_text])
        
        # 2. Hitung similarity dengan semua okupasi PON
        scores = cosine_similarity(query_vector, st.session_state.pon_vectors)
        
        # 3. Ambil yang paling cocok
        best_match_index = scores.argmax()
        best_score = scores[0, best_match_index]
        
        # 4. Ambil data okupasi
        pon_data = st.session_state.pon_data.iloc[best_match_index]
        okupasi_id = pon_data['OkupasiID']
        okupasi_nama = pon_data['Okupasi']
        
        # 5. Identifikasi gap (simulasi)
        gap_keterampilan = "Cloud Computing (AWS/GCP), CI/CD Pipelines, Agile"
        
        print(f"Hasil: {okupasi_nama} (Skor: {best_score:.2f})")
        return okupasi_id, okupasi_nama, best_score, gap_keterampilan

    except Exception as e:
        st.error(f"Error di Pemetaan: {e}")
        return None, None, 0, ""


# ========================================
# BAGIAN 7: GENERATE SOAL ASESMEN
# ========================================

def sanitize_json_response(text: str) -> str:
    """
    FUNGSI: Membersihkan response JSON dari AI
    
    ANALOGI: Seperti membersihkan teks yang berantakan.
    AI kadang memberikan karakter aneh yang bikin error.
    """
    # Hapus escape sequence invalid
    text = re.sub(r'\\(?![ntr"\\/bfuU])', '', text)
    text = text.replace("\\'", "'")
    
    # Hapus control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Fix missing commas
    text = re.sub(r'\}\s*\{', '},{', text)
    text = re.sub(r'\]\s*"', '],"', text)
    
    return text.strip()


def generate_assessment_questions(okupasi_id: str):
    """
    FUNGSI: Membuat soal asesmen menggunakan AI Gemini
    
    ANALOGI: Seperti meminta guru untuk membuat soal ujian.
    1. Beri tahu guru topiknya (okupasi)
    2. Guru membuat 5 soal pilihan ganda
    3. Kita validasi soalnya sudah benar
    
    TEKNIS: Prompt Engineering + JSON Parsing
    - Buat prompt detail untuk AI
    - Kirim ke Gemini API
    - Parse response JSON
    - Validasi struktur soal
    
    Returns:
        List of dict dengan 5 soal pilihan ganda
    """
    print(f"🤖 Membuat {JUMLAH_SOAL} soal dengan AI...")
    
    # 1. Ambil data okupasi dari database
    if not st.session_state.get('ai_initialized'):
        raise Exception("AI Engine belum diinisialisasi")
    
    try:
        pon_data = st.session_state.pon_data[
            st.session_state.pon_data['OkupasiID'] == okupasi_id
        ]
        if pon_data.empty:
            raise Exception(f"Okupasi ID {okupasi_id} tidak ditemukan")
        
        okupasi_info = pon_data.iloc[0]
        okupasi_nama = okupasi_info['Okupasi']
        unit_kompetensi = okupasi_info['Unit_Kompetensi']
        kuk_keywords = okupasi_info['Kuk_Keywords']
        
    except Exception as e:
        raise Exception(f"Error mengambil data okupasi: {e}")
    
    # 2. Buat prompt untuk AI
    prompt = f"""Anda adalah expert TIK Indonesia yang membuat soal asesmen.

Buat TEPAT {JUMLAH_SOAL} soal pilihan ganda untuk okupasi:

**Okupasi:** {okupasi_nama}
**Unit Kompetensi:** {unit_kompetensi}
**Keterampilan Kunci:** {kuk_keywords}

**Kriteria Soal:**
1. Relevan dengan unit kompetensi
2. Tingkat: Menengah - Ahli
3. Fokus skenario praktis
4. TEPAT 4 opsi per soal
5. 1 jawaban benar
6. Bahasa Indonesia profesional
7. HINDARI karakter khusus yang merusak JSON

**Format Output JSON:**
{{
  "questions": [
    {{
      "id": "q1",
      "teks": "Pertanyaan lengkap",
      "opsi": ["Opsi A", "Opsi B", "Opsi C", "Opsi D"],
      "jawaban_benar": "Opsi A"
    }}
  ]
}}

ATURAN:
- TEPAT {JUMLAH_SOAL} soal (q1-q{JUMLAH_SOAL})
- Pisahkan dengan koma
- jawaban_benar harus sama persis dengan salah satu opsi
- Output HANYA JSON valid
"""

    try:
        # 3. Kirim ke API
        with st.spinner(f"🤖 Gemini AI membuat soal..."):
            response_text = call_gemini_api(prompt)
        
        print(f"Raw Response: {response_text[:500]}")
        
        # 4. Bersihkan dan parse JSON
        response_text = sanitize_json_response(response_text)
        response_json = json.loads(response_text)
        
        # 5. Ekstrak questions
        if isinstance(response_json, dict) and "questions" in response_json:
            questions = response_json["questions"]
        elif isinstance(response_json, list):
            questions = response_json
        else:
            raise ValueError("Format response tidak dikenali")
        
        # 6. Validasi jumlah soal
        if len(questions) != JUMLAH_SOAL:
            st.warning(f"AI buat {len(questions)} soal, bukan {JUMLAH_SOAL}")
            # Tambahkan dummy jika kurang
            while len(questions) < JUMLAH_SOAL:
                questions.append({
                    "id": f"q{len(questions)+1}",
                    "teks": f"[Soal tambahan] Dalam {okupasi_nama}, bagaimana menangani darurat?",
                    "opsi": ["Eskalasi", "Konsultasi", "Dokumentasi", "Trial-error"],
                    "jawaban_benar": "Konsultasi"
                })
            questions = questions[:JUMLAH_SOAL]
        
        # 7. Validasi struktur setiap soal
        for i, q in enumerate(questions):
            # Cek field wajib
            if not all(k in q for k in ["id", "teks", "opsi", "jawaban_benar"]):
                raise ValueError(f"Soal {i+1} struktur tidak lengkap")
            
            # Cek 4 opsi
            if len(q["opsi"]) != 4:
                raise ValueError(f"Soal {i+1} tidak punya 4 opsi")
            
            # Cek jawaban benar ada di opsi
            if q["jawaban_benar"] not in q["opsi"]:
                raise ValueError(f"Soal {i+1}: Jawaban tidak ada di opsi")
            
            # Set ID dan tipe
            q["id"] = f"q{i+1}"
            q["tipe"] = "pilihan_ganda"
        
        print(f"✅ Berhasil generate {len(questions)} soal")
        return questions
        
    except json.JSONDecodeError as e:
        # Retry dengan cleaning lebih agresif
        error_msg = f"❌ Error parsing JSON: {e}\nResponse: {response_text[:2000]}"
        st.error(error_msg)
        raise Exception(error_msg)
        
    except Exception as e:
        st.error(f"❌ Error generate soal: {e}")
        raise Exception(e)


# ========================================
# BAGIAN 8: VALIDASI ASESMEN
# ========================================

def validate_assessment(answers: dict, questions: list):
    """
    FUNGSI: Menilai jawaban asesmen
    
    ANALOGI: Seperti guru mengoreksi ujian.
    1. Bandingkan jawaban siswa dengan kunci jawaban
    2. Hitung berapa yang benar
    3. Konversi ke skor 0-100
    4. Tentukan level kompetensi
    
    Returns:
        (skor, level): Skor 0-100 dan level kompetensi
    """
    print(f"Memvalidasi {len(answers)} jawaban...")
    
    if not questions:
        st.error("Tidak ada soal untuk divalidasi")
        return 0, "Error"
    
    total_questions = len(questions)
    correct_answers = 0
    
    # Bandingkan jawaban
    for q in questions:
        q_id = q['id']
        correct = q['jawaban_benar']
        
        if q_id in answers:
            user_answer = answers[q_id]
            if user_answer == correct:
                correct_answers += 1
    
    # Hitung skor (0-100)
    skor = int((correct_answers / total_questions) * 100)
    
    # Tentukan level
    if skor >= 90:
        level = "Ahli (Rekomendasi Asesmen Lanjutan)"
    elif skor >= 70:
        level = "Menengah (Kompeten)"
    elif skor >= 50:
        level = "Junior (Perlu Pelatihan)"
    else:
        level = "Pemula (Perlu Pelatihan Intensif)"
        
    print(f"Hasil: {correct_answers}/{total_questions} = {skor}/100, {level}")
    return skor, level


# ========================================
# BAGIAN 9: ANALISIS KARIER AI
# ========================================

def analyze_career_profile_ai(profil_teks):
    """
    FUNGSI: Analisis profil karier dengan AI
    
    ANALOGI: Seperti konsultasi dengan career counselor.
    AI membaca profil dan memberikan saran karier.
    
    CATATAN: Saat ini return dummy data untuk testing
    """
    return {
        "career_analysis": {
            "profil_input": profil_teks,
            "analisis_profesional": [
                {
                    "judul": "Rekomendasi Jalur Karier",
                    "konten": [
                        {
                            "okupasi": "Data Analyst",
                            "alasan": "Kesesuaian tinggi dengan minat analisis"
                        },
                        {
                            "okupasi": "ML Engineer",
                            "alasan": "Cocok karena pengalaman statistik"
                        }
                    ]
                }
            ],
            "saran_aktivitas": {
                "Langkah Pengembangan": "Pelajari cloud computing",
                "Kegiatan Disarankan": "Ikuti bootcamp Data Engineering"
            }
        }
    }


# ========================================
# BAGIAN 10: REKOMENDASI
# ========================================

def get_recommendations(mapped_okupasi_id, skill_gap, profil_teks):
    """
    FUNGSI: Memberikan rekomendasi pekerjaan dan pelatihan
    
    Returns:
        (jobs, trainings): List pekerjaan dan pelatihan
    """
    # Dummy data
    job_samples = [
        {
            "Posisi": "Data Analyst",
            "Perusahaan": "Tech Innovate",
            "Lokasi": "Jakarta",
            "Keterampilan_Dibutuhkan": "Python, SQL, Power BI",
            "Deskripsi_Pekerjaan": "Menganalisis data bisnis"
        },
        {
            "Posisi": "ML Engineer",
            "Perusahaan": "AI Labs",
            "Lokasi": "Bandung",
            "Keterampilan_Dibutuhkan": "Python, TensorFlow, AWS",
            "Deskripsi_Pekerjaan": "Membangun model AI"
        }
    ]

    training_samples = [
        "Pelatihan Cloud Computing (AWS/GCP)",
        "Kursus CI/CD Pipelines",
        "Workshop Agile Project Management",
        "Bootcamp Machine Learning"
    ]

    return random.sample(job_samples, 2), random.sample(training_samples, 2)


# ========================================
# BAGIAN 11: DASHBOARD DATA
# ========================================

def get_national_dashboard_data():
    """
    FUNGSI: Mengambil data untuk dashboard nasional
    
    Returns:
        (distribusi_okupasi, sebaran_lokasi, skill_gap_umum)
    """
    print("📊 Mengambil data dashboard...")
    
    df_hasil = load_excel_sheet(EXCEL_PATH, SHEET_HASIL)
    df_talenta = load_excel_sheet(EXCEL_PATH, SHEET_TALENTA)
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)

    # Distribusi Okupasi (dummy)
    distribusi_okupasi = pd.DataFrame({
        'Okupasi': ['Data Analyst', 'DevOps', 'AI Engineer'],
        'Jumlah_Talenta': [45, 32, 28]
    }).set_index('Okupasi')

    # Sebaran Lokasi
    sebaran_lokasi = pd.DataFrame({
        'Lokasi': ['Jakarta', 'Bandung', 'Surabaya'],
        'Jumlah': [50, 30, 25],
        'lat': [-6.20, -6.91, -7.25],
        'lon': [106.81, 107.61, 112.75],
        'size': [50, 30, 25]
    })
    
    # Skill Gap
    skill_gap_umum = pd.DataFrame({
        'Keterampilan': ['Cloud', 'AI/ML', 'PM', 'Data Governance'],
        'Jumlah_Gap': [120, 95, 80, 65]
    }).set_index('Keterampilan')

    return distribusi_okupasi, sebaran_lokasi, skill_gap_umum
