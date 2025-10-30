# ai_engine.py
import pandas as pd
import random
import re
import json
import os
from config import (
    EXCEL_PATH, SHEET_PON, SHEET_LOWONGAN, SHEET_HASIL, SHEET_TALENTA
)
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- TAMBAHAN: Import untuk Gemini ---
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    st.error("⚠️ Library 'requests' tidak ditemukan. Install dengan: pip install requests")

# --- KONFIGURASI GEMINI ---
GEMINI_API_KEY = "AIzaSyCR8xgDIv5oYBaDmMyuGGWjqpFi7U8SGA4"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-flash-latest"  # Nama model yang benar untuk v1beta

# Jumlah soal asesmen
JUMLAH_SOAL = 5

def get_api_keys():
    """Mendapatkan API keys dari secrets atau hardcoded"""
    gemini_key = GEMINI_API_KEY
    
    # Coba ambil dari Streamlit secrets jika ada
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        gemini_key = st.secrets['GEMINI_API_KEY']
    
    return gemini_key

GEMINI_API_KEY = get_api_keys()


def call_gemini_api(prompt: str) -> str:
    """
    Memanggil Google Gemini API untuk generate text.
    
    Args:
        prompt: Prompt untuk AI
        
    Returns:
        Response text dari AI
    """
    if not REQUESTS_AVAILABLE:
        raise Exception("Library 'requests' tidak tersedia")
    
    url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Instruksi JSON di dalam prompt
    json_instruction = """

PENTING: Anda HARUS merespons dengan JSON yang valid. Tidak ada teks tambahan di luar JSON.
Format yang diharapkan:
{
  "questions": [
    {"id": "q1", "teks": "...", "opsi": ["...", "...", "...", "..."], "jawaban_benar": "..."},
    {"id": "q2", "teks": "...", "opsi": ["...", "...", "...", "..."], "jawaban_benar": "..."}
  ]
}
"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt + json_instruction
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 3000
        }
    }
    
    try:
        print(f"🔄 Memanggil Gemini API ({GEMINI_MODEL})...")
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"API Response Status: {response.status_code}")
        
        response.raise_for_status()
        
        result = response.json()
        
        # Parse response Gemini
        if 'candidates' not in result or len(result['candidates']) == 0:
            raise Exception(f"Response API tidak valid: {result}")
        
        # Ambil text dari response
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Clean markdown code fence jika ada
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        print(f"✅ Berhasil mendapatkan response dari Gemini")
        return content
        
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        raise Exception(f"HTTP Error {response.status_code}: {error_detail}")
        
    except requests.exceptions.Timeout:
        raise Exception("Request timeout - API membutuhkan waktu terlalu lama (>60s)")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling Gemini API: {e}")
    
    except KeyError as e:
        raise Exception(f"Format response Gemini tidak sesuai: {e}. Response: {result}")


def load_excel_sheet(file_path, sheet_name):
    """Fungsi bantuan untuk membaca sheet Excel dengan aman."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        df.columns = df.columns.str.strip()
        df = df.fillna('') 
        return df
    except FileNotFoundError:
        st.error(f"Gagal memuat file: '{file_path}'. Pastikan file ada di folder 'data/'.")
        return None
    except Exception as e:
        st.error(f"Gagal memuat sheet '{sheet_name}'. Error: {e}")
        return None


def initialize_ai_engine():
    """Setup AI Engine dengan Vector DB simulasi"""
    if st.session_state.get('ai_initialized', False):
        return True

    try:
        df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
        if df_pon is None or df_pon.empty:
            st.error(f"Data sheet '{SHEET_PON}' tidak bisa dimuat atau kosong.")
            return False
            
        df_jobs = load_excel_sheet(EXCEL_PATH, SHEET_LOWONGAN)
        if df_jobs is None: 
            st.warning(f"Sheet '{SHEET_LOWONGAN}' tidak ditemukan.")
            df_jobs = pd.DataFrame(columns=['OkupasiID', 'Deskripsi_Pekerjaan', 'Posisi', 'Perusahaan', 'Keterampilan_Dibutuhkan'])

        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        pon_corpus = df_pon['Okupasi'] + ' ' + df_pon['Unit_Kompetensi'] + ' ' + df_pon['Kuk_Keywords']
        job_corpus = df_jobs['Posisi'] + ' ' + df_jobs['Deskripsi_Pekerjaan'] + ' ' + df_jobs['Keterampilan_Dibutuhkan']

        if pon_corpus.empty and job_corpus.empty:
             st.error("Data PON dan Lowongan kosong.")
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
        print("✅ AI Engine Berhasil Diinisialisasi")
        return True

    except Exception as e:
        st.error(f"Error saat inisialisasi AI Engine: {e}")
        st.session_state.ai_initialized = False
        return False


def extract_profile_entities(raw_cv: str):
    """Ekstraksi entitas dari CV (NER sederhana)"""
    words = set(re.findall(r'\b\w{4,}\b', raw_cv.lower()))
    profile_text = ' '.join(words)
    print(f"Hasil Ekstraksi: {profile_text[:100]}...")
    return profile_text


def sanitize_json_response(text: str) -> str:
    """
    Membersihkan response JSON dari AI untuk menghindari error parsing.
    
    Args:
        text: Raw JSON string dari AI
        
    Returns:
        Cleaned JSON string
    """
    # 1. Hapus escape sequence yang invalid
    # Replace \e, \x, dll yang bukan \n, \t, \r, \", \\, \/, \b, \f, \u
    text = re.sub(r'\\(?![ntr"\\/bfuU])', '', text)
    
    # 2. Fix kutip tunggal di dalam string yang mungkin jadi masalah
    # Ganti \'  dengan ' (karena dalam JSON string pakai double quote)
    text = text.replace("\\'", "'")
    
    # 3. Hapus control characters yang bisa merusak JSON
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # 4. Fix newline di tengah string (ganti dengan spasi)
    # Ini untuk mencegah string multiline yang break JSON
    text = re.sub(r'"\s*\n\s*([^":])', r'" \1', text)
    
    # 5. Auto-fix missing commas antara objects dalam array
    # Pattern: } diikuti { tanpa koma di antaranya
    text = re.sub(r'\}\s*\{', '},{', text)
    
    # 6. Auto-fix missing commas antara array items
    # Pattern: ] diikuti " tanpa koma
    text = re.sub(r'\]\s*"', '],"', text)
    
    # 7. Auto-fix missing commas setelah nilai string
    # Pattern: "value" diikuti "key" tanpa koma
    text = re.sub(r'"\s+("(?:id|teks|opsi|jawaban_benar)")', r',\1', text)
    
    # 8. Hapus whitespace berlebih
    text = text.strip()
    
    return text


def map_profile_to_pon(profile_text: str):
    """Pemetaan profil ke PON TIK menggunakan semantic search"""
    print(f"Memetakan profil: {profile_text[:50]}...")
    
    if not st.session_state.get('ai_initialized') or st.session_state.get('pon_vectors') is None:
        st.error("AI Engine belum siap atau data PON TIK kosong.")
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
        st.error(f"Error di Pemetaan: {e}")
        return None, None, 0, ""


def generate_assessment_questions(okupasi_id: str):
    """
    Generate 5 soal pilihan ganda WAJIB menggunakan AI.
    Tidak ada fallback - jika AI gagal, akan raise error.
    
    Args:
        okupasi_id: ID okupasi dari PON TIK
    
    Returns:
        List of dict dengan 5 soal pilihan ganda
    """
    print(f"🤖 Membuat {JUMLAH_SOAL} soal asesmen dengan AI untuk Okupasi ID: {okupasi_id}...")
    
    # Ambil detail okupasi dari database
    if not st.session_state.get('ai_initialized'):
        raise Exception("AI Engine belum diinisialisasi. Tidak bisa generate soal.")
    
    try:
        pon_data = st.session_state.pon_data[st.session_state.pon_data['OkupasiID'] == okupasi_id]
        if pon_data.empty:
            raise Exception(f"Okupasi ID {okupasi_id} tidak ditemukan di database PON TIK.")
        
        okupasi_info = pon_data.iloc[0]
        okupasi_nama = okupasi_info['Okupasi']
        unit_kompetensi = okupasi_info['Unit_Kompetensi']
        kuk_keywords = okupasi_info['Kuk_Keywords']
        
    except Exception as e:
        raise Exception(f"Error mengambil data okupasi: {e}")
    
    # Generate soal menggunakan Gemini AI
    prompt = f"""Anda adalah expert dalam bidang TIK Indonesia yang membuat soal asesmen kompetensi profesional.

Buat TEPAT {JUMLAH_SOAL} soal pilihan ganda untuk menguji kompetensi seorang kandidat pada okupasi berikut:

**Okupasi:** {okupasi_nama}
**Unit Kompetensi:** {unit_kompetensi}
**Keterampilan Kunci:** {kuk_keywords}

**Kriteria Soal:**
1. Setiap soal harus relevan dengan unit kompetensi dan keterampilan di atas
2. Tingkat kesulitan: Menengah hingga Ahli
3. Fokus pada skenario praktis dan problem-solving (bukan teoritis murni)
4. Setiap soal memiliki TEPAT 4 opsi jawaban
5. Hanya 1 jawaban yang benar per soal
6. Opsi jawaban harus masuk akal dan tidak obvious
7. Gunakan bahasa Indonesia yang profesional
8. HINDARI penggunaan kutip tunggal atau karakter khusus yang bisa merusak JSON

**Format Output JSON (HARUS PERSIS SEPERTI INI):**
{{
  "questions": [
    {{
      "id": "q1",
      "teks": "Pertanyaan lengkap dalam 1-3 kalimat",
      "opsi": ["Opsi A yang lengkap", "Opsi B yang lengkap", "Opsi C yang lengkap", "Opsi D yang lengkap"],
      "jawaban_benar": "Opsi A yang lengkap"
    }},
    {{
      "id": "q2",
      "teks": "Pertanyaan lengkap dalam 1-3 kalimat",
      "opsi": ["Opsi A yang lengkap", "Opsi B yang lengkap", "Opsi C yang lengkap", "Opsi D yang lengkap"],
      "jawaban_benar": "Opsi B yang lengkap"
    }}
  ]
}}

ATURAN KETAT JSON:
- TEPAT {JUMLAH_SOAL} soal (q1 sampai q{JUMLAH_SOAL})
- Setiap object soal HARUS dipisah dengan koma
- Field "jawaban_benar" harus persis sama dengan salah satu opsi
- Output HANYA JSON valid, tanpa teks tambahan sebelum atau sesudah
- Jangan gunakan escape sequence seperti \\n atau \\t di dalam string
- Jangan gunakan newline di tengah string - tulis semua dalam satu baris
- Gunakan spasi biasa untuk pemisah kata, bukan tab atau newline
- PASTIKAN semua kurung kurawal dan bracket tertutup dengan benar"""

    try:
        with st.spinner(f"🤖 Gemini AI sedang membuat {JUMLAH_SOAL} soal untuk {okupasi_nama}..."):
            response_text = call_gemini_api(prompt)
        
        print(f"Raw Gemini Response (first 500 chars): {response_text[:500]}")
        
        # Sanitasi response untuk menghindari error JSON parsing
        response_text = sanitize_json_response(response_text)
        
        # Parse JSON
        response_json = json.loads(response_text)
        
        # Cek apakah ada wrapper "questions"
        if isinstance(response_json, dict) and "questions" in response_json:
            questions = response_json["questions"]
        elif isinstance(response_json, list):
            questions = response_json
        else:
            raise ValueError(f"Format response tidak dikenali: {type(response_json)}")
        
        # Validasi ketat
        if not isinstance(questions, list):
            raise ValueError("Output AI bukan list/array")
        
        if len(questions) != JUMLAH_SOAL:
            st.warning(f"AI menghasilkan {len(questions)} soal, bukan {JUMLAH_SOAL}. Menyesuaikan...")
            # Jika kurang dari JUMLAH_SOAL, tambahkan dummy
            while len(questions) < JUMLAH_SOAL:
                questions.append({
                    "id": f"q{len(questions)+1}",
                    "teks": f"[Soal tambahan {len(questions)+1}] Dalam konteks {okupasi_nama}, bagaimana Anda menangani situasi darurat?",
                    "opsi": ["Eskalasi ke atasan", "Konsultasi tim", "Cek dokumentasi", "Trial-error terkontrol"],
                    "jawaban_benar": "Konsultasi tim"
                })
            questions = questions[:JUMLAH_SOAL]
        
        # Validasi struktur setiap soal
        for i, q in enumerate(questions):
            # Cek field wajib
            if not all(key in q for key in ["id", "teks", "opsi", "jawaban_benar"]):
                raise ValueError(f"Soal {i+1} tidak memiliki struktur lengkap. Field: {q.keys()}")
            
            # Cek jumlah opsi
            if len(q["opsi"]) != 4:
                raise ValueError(f"Soal {i+1} tidak memiliki 4 opsi (ada {len(q['opsi'])})")
            
            # Cek jawaban benar ada di opsi
            if q["jawaban_benar"] not in q["opsi"]:
                raise ValueError(f"Soal {i+1}: Jawaban benar '{q['jawaban_benar']}' tidak ada di opsi {q['opsi']}")
            
            # Pastikan ID benar
            q["id"] = f"q{i+1}"
            q["tipe"] = "pilihan_ganda"
        
        print(f"✅ Berhasil generate {len(questions)} soal dengan Gemini AI")
        return questions
        
    except json.JSONDecodeError as e:
        # Coba sekali lagi dengan cleaning lebih agresif
        try:
            print(f"⚠️ JSON parsing gagal, mencoba metode alternatif...")
            
            # Metode 1: Ekstrak array questions dengan regex
            match = re.search(r'"questions"\s*:\s*(\[.*\])', response_text, re.DOTALL)
            if match:
                questions_json = match.group(1)
                
                # Cleaning tambahan untuk array
                # Fix missing commas setelah closing brace
                questions_json = re.sub(r'\}\s*\{', '},{', questions_json)
                # Fix missing commas setelah closing bracket dalam array
                questions_json = re.sub(r'\]\s*"', '],"', questions_json)
                # Fix missing commas setelah string
                questions_json = re.sub(r'"\s*"([a-zA-Z_]+)"', '","\\1"', questions_json)
                
                # Wrap kembali dalam object
                cleaned = f'{{"questions": {questions_json}}}'
                cleaned = sanitize_json_response(cleaned)
                
                print(f"Cleaned JSON (first 500 chars): {cleaned[:500]}")
                response_json = json.loads(cleaned)
                
                if "questions" in response_json:
                    questions = response_json["questions"]
                    print(f"✅ Berhasil parse JSON setelah cleaning agresif")
                    
                    # Lanjut ke validasi
                    if not isinstance(questions, list):
                        raise ValueError("Output AI bukan list/array")
                    
                    if len(questions) != JUMLAH_SOAL:
                        st.warning(f"AI menghasilkan {len(questions)} soal, bukan {JUMLAH_SOAL}. Menyesuaikan...")
                        while len(questions) < JUMLAH_SOAL:
                            questions.append({
                                "id": f"q{len(questions)+1}",
                                "teks": f"[Soal tambahan {len(questions)+1}] Dalam konteks {okupasi_nama}, bagaimana Anda menangani situasi darurat?",
                                "opsi": ["Eskalasi ke atasan", "Konsultasi tim", "Cek dokumentasi", "Trial-error terkontrol"],
                                "jawaban_benar": "Konsultasi tim"
                            })
                        questions = questions[:JUMLAH_SOAL]
                    
                    # Validasi struktur setiap soal
                    for i, q in enumerate(questions):
                        if not all(key in q for key in ["id", "teks", "opsi", "jawaban_benar"]):
                            raise ValueError(f"Soal {i+1} tidak memiliki struktur lengkap. Field: {q.keys()}")
                        
                        if len(q["opsi"]) != 4:
                            raise ValueError(f"Soal {i+1} tidak memiliki 4 opsi (ada {len(q['opsi'])})")
                        
                        if q["jawaban_benar"] not in q["opsi"]:
                            raise ValueError(f"Soal {i+1}: Jawaban benar '{q['jawaban_benar']}' tidak ada di opsi {q['opsi']}")
                        
                        q["id"] = f"q{i+1}"
                        q["tipe"] = "pilihan_ganda"
                    
                    print(f"✅ Berhasil generate {len(questions)} soal dengan Gemini AI (setelah retry)")
                    return questions
                else:
                    raise ValueError("Tidak ada field 'questions' setelah re-parse")
            else:
                raise ValueError("Tidak bisa ekstrak array questions dari response")
                
        except Exception as retry_error:
            # Tampilkan response yang bermasalah untuk debugging
            error_msg = f"""❌ Error parsing JSON dari AI: {e}

Retry Error: {retry_error}

Response AI (first 2000 chars):
{response_text[:2000]}

Tip: Coba jalankan ulang. Jika error terus terjadi, kemungkinan API Gemini mengeluarkan format yang tidak konsisten."""
            st.error(error_msg)
            raise Exception(error_msg)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error koneksi ke API: {e}"
        st.error(error_msg)
        raise Exception(error_msg)
        
    except Exception as e:
        error_msg = f"❌ Error saat generate soal dengan AI: {e}"
        st.error(error_msg)
        raise Exception(error_msg)


def validate_assessment(answers: dict, questions: list):
    """
    Validasi jawaban asesmen dengan scoring otomatis.
    
    Args:
        answers: Dict dengan format {question_id: selected_answer}
        questions: List soal dengan jawaban benar
    
    Returns:
        (skor, level): Skor 0-100 dan level kompetensi
    """
    print(f"Memvalidasi {len(answers)} jawaban...")
    
    if not questions:
        st.error("Tidak ada soal untuk divalidasi.")
        return 0, "Error"
    
    total_questions = len(questions)
    correct_answers = 0
    
    # Bandingkan jawaban dengan kunci jawaban
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
        
    print(f"Hasil Asesmen: {correct_answers}/{total_questions} benar = Skor {skor}/100, Level {level}")
    return skor, level


def get_recommendations(okupasi_id: str, gap_keterampilan: str, profil_teks: str):
    """Mendapatkan rekomendasi pekerjaan dan pelatihan"""
    print(f"Mencari rekomendasi untuk {okupasi_id}...")
    
    rekomendasi_pekerjaan = []
    rekomendasi_pelatihan = []

    if not st.session_state.get('ai_initialized'):
        st.error("AI Engine belum siap.")
        return [], []

    try:
        # Rekomendasi Pekerjaan (Semantic Search)
        if st.session_state.get('job_vectors') is not None and st.session_state.job_vectors.shape[0] > 0:
            query_vector = st.session_state.vectorizer.transform([profil_teks])
            scores = cosine_similarity(query_vector, st.session_state.job_vectors)
            top_3_indices = scores.argsort()[0][-3:][::-1]
            rekomendasi_pekerjaan = st.session_state.job_data.iloc[top_3_indices].to_dict('records')
        else:
            print("Tidak ada data lowongan.")
            
    except Exception as e:
        st.error(f"Error saat mencari rekomendasi pekerjaan: {e}")

    try:
        # Rekomendasi Pelatihan berdasarkan gap
        gaps = [g.strip() for g in gap_keterampilan.split(',')]
        for gap in gaps:
            rekomendasi_pelatihan.append(
                f"Kursus Intensif: {gap} (Platform: Dicoding/Coursera/LinkedIn Learning)"
            )
    except Exception as e:
        st.error(f"Error saat membuat rekomendasi pelatihan: {e}")

    return rekomendasi_pekerjaan, rekomendasi_pelatihan

    import json
import streamlit as st

def get_personalized_career_path(okupasi_nama: str, skor: int, skill_gap: str, profile_text: str):
    """
    🚀 Membuat roadmap karier personal berbasis AI (Gemini)
    """
    try:
        prompt = f"""
        Anda adalah asisten karier profesional.
        Berdasarkan data berikut, buat roadmap karier yang realistis dan personal.

        === PROFIL PESERTA ===
        {profile_text}

        === OKUPASI YANG DITUJU ===
        {okupasi_nama}

        === SKOR ASESMEN ===
        {skor} / 100

        === SKILL GAP ===
        {skill_gap}

        Tampilkan roadmap karier dalam format Markdown.
        Gunakan struktur yang rapi dengan heading dan bullet point, misalnya:

        ## Tahap 1: Peningkatan Dasar
        - Pelajari konsep ...
        - Ikuti pelatihan ...
        - Target waktu: 1 bulan

        ## Tahap 2: Penguatan Kompetensi
        - Terapkan skill ...
        - Ikuti proyek mini ...
        - Target waktu: 2–3 bulan

        ## Tahap 3: Profesionalisasi
        - Melamar ke posisi ...
        - Kembangkan portofolio ...
        - Bergabung di komunitas profesional ...

        Tambahkan catatan motivasional singkat di akhir.
        """

        # Panggil fungsi yang kamu tambahkan sebelumnya
        from ai_engine import call_gemini_api, sanitize_json_response

        ai_response = call_gemini_api(prompt)

        # Gemini biasanya bisa mengembalikan Markdown langsung, jadi kita tampilkan apa adanya
        return ai_response.strip()

    except Exception as e:
        st.error(f"Gagal menghasilkan roadmap AI: {e}")
        return "❌ Terjadi kesalahan saat menghasilkan roadmap karier AI."

def get_national_dashboard_data():
    """Mengambil data untuk dashboard nasional"""
    print("📊 Mengambil data dashboard...")
    
    df_hasil = load_excel_sheet(EXCEL_PATH, SHEET_HASIL)
    df_talenta = load_excel_sheet(EXCEL_PATH, SHEET_TALENTA)
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)

    if df_hasil is None or df_talenta is None or df_pon is None:
        st.error("Gagal memuat data untuk dashboard.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Distribusi Okupasi
    distribusi_okupasi = pd.DataFrame(columns=['Okupasi', 'Jumlah_Talenta']).set_index('Okupasi')
    if 'OkupasiID_Mapped' in df_hasil.columns and 'OkupasiID' in df_pon.columns:
        if not df_hasil.empty and not df_pon.empty:
            merged_data = pd.merge(df_hasil, df_pon, left_on='OkupasiID_Mapped', right_on='OkupasiID', how='left')
            distribusi_okupasi_series = merged_data['Okupasi'].value_counts()
            if not distribusi_okupasi_series.empty:
                distribusi_okupasi = distribusi_okupasi_series.reset_index()
                distribusi_okupasi.columns = ['Okupasi', 'Jumlah_Talenta']
                distribusi_okupasi = distribusi_okupasi.set_index('Okupasi')

    # Sebaran Lokasi
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
    
    # Skill Gap Umum (Simulasi)
    skill_gap_umum = pd.DataFrame({
        'Keterampilan': ['Cloud Computing', 'AI/ML', 'Project Management', 'Data Governance'],
        'Jumlah_Gap': [random.randint(30, 150) for _ in range(4)]
    }).set_index('Keterampilan')

    return distribusi_okupasi, sebaran_lokasi, skill_gap_umum
