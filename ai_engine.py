# File: ai_engine.py

import google.generativeai as genai
import streamlit as st
import json
import logging # Baik untuk debugging

# --- Konfigurasi API ---
# Ambil API key dari Streamlit secrets
# Pastikan Anda sudah menambahkannya di file .streamlit/secrets.toml
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except (KeyError, FileNotFoundError):
    logging.error("❌ GOOGLE_API_KEY tidak ditemukan di st.secrets.")
    st.error("Konfigurasi API Key Gemini tidak ditemukan. Harap set di st.secrets.")

# Konstanta untuk model
MODEL_NAME = "gemini-flash-latest"
JUMLAH_SOAL = 5 # Tentukan jumlah soal yang ingin Anda buat

def generate_assessment_questions(okupasi_id: str):
    """
    Menghasilkan daftar soal asesmen menggunakan Gemini API.
    Fungsi ini adalah TAHAP 3.
    """
    
    # 1. Konfigurasi Generasi (PERBAIKAN UTAMA)
    # Ini adalah kunci untuk memperbaiki error 'Unterminated string'
    generation_config = {
        "temperature": 0.4,
        "max_output_tokens": 8192,         # ✅ Memberi ruang yang SANGAT besar agar JSON tidak terpotong
        "response_mime_type": "application/json", # ✅ Memaksa output HANYA sebagai JSON valid
    }

    # 2. Inisialisasi Model
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=generation_config
        )
    except Exception as e:
        logging.error(f"Gagal inisialisasi model: {e}")
        raise ValueError(f"Gagal inisialisasi model Gemini: {e}")

    # 3. Prompt Engineering (Sangat Penting)
    # Menjelaskan struktur JSON yang HARUS diikuti oleh AI
    prompt = f"""
    Anda adalah seorang ahli pembuat soal asesmen teknis.
    Tugas Anda adalah membuat {JUMLAH_SOAL} pertanyaan asesmen untuk okupasi: "{okupasi_id}".
    
    Tolong hasilkan respons dalam format JSON yang valid.
    Struktur JSON harus berupa object dengan satu key "questions".
    "questions" adalah sebuah LIST dari object pertanyaan.
    
    Setiap object pertanyaan HARUS memiliki struktur sebagai berikut:
    1.  "id": string (Contoh: "q1", "q2", ..., "q{JUMLAH_SOAL}")
    2.  "teks": string (Teks pertanyaan yang jelas)
    3.  "tipe": string (Hanya boleh 'pilihan_ganda' atau 'esai_singkat')
    4.  "opsi": list[string] (Harus berisi 4 string opsi jawaban jika tipe='pilihan_ganda'. Boleh list kosong [] jika tipe='esai_singkat')
    5.  "jawaban_benar": string (Jawaban yang benar. Jika 'pilihan_ganda', nilainya HARUS SAMA PERSIS dengan salah satu string di 'opsi')

    Contoh untuk 'pilihan_ganda':
    {{
      "id": "q1",
      "teks": "Manakah dari berikut ini yang merupakan library visualisasi data di Python?",
      "tipe": "pilihan_ganda",
      "opsi": ["Matplotlib", "NumPy", "Pandas", "SciPy"],
      "jawaban_benar": "Matplotlib"
    }}
    
    Contoh untuk 'esai_singkat':
    {{
      "id": "q2",
      "teks": "Jelaskan secara singkat apa itu 'overfitting' dalam machine learning.",
      "tipe": "esai_singkat",
      "opsi": [],
      "jawaban_benar": "Overfitting terjadi ketika model belajar terlalu detail dari data training, termasuk noise, sehingga performanya buruk pada data baru."
    }}
    
    Pastikan semua string valid, tidak terpotong, dan JSON-nya lengkap.
    Hasilkan {JUMLAH_SOAL} soal sekarang untuk okupasi "{okupasi_id}".
    """

    # 4. Panggil API dan Tangani Respons
    try:
        logging.info(f"Mengirim request ke Gemini untuk okupasi: {okupasi_id}")
        response = model.generate_content(prompt)
        
        # 5. Parsing JSON
        # Karena kita pakai response_mime_type, response.text adalah JSON mentah
        data = json.loads(response.text)
        
        # Validasi sederhana
        if "questions" not in data or not isinstance(data["questions"], list):
            raise ValueError("Struktur JSON tidak valid. Key 'questions' tidak ditemukan.")
            
        questions = data["questions"]
        
        # Pastikan jumlah soal sesuai
        if len(questions) != JUMLAH_SOAL:
            logging.warning(f"AI menghasilkan {len(questions)} soal, bukan {JUMLAH_SOAL}")

        logging.info(f"Berhasil membuat {len(questions)} soal.")
        return questions # Mengembalikan LIST dari soal

    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}. Respons mentah: {response.text}")
        raise ValueError(f"AI mengembalikan JSON tidak valid. Error: {e}")
    except Exception as e:
        logging.error(f"Error saat generate soal: {e}")
        raise

# -------------------------------------------------------------------

def validate_assessment(answers: dict, questions: list):
    """
    Memvalidasi jawaban user dan menghitung skor.
    Fungsi ini adalah TAHAP 4.
    
    NOTE: Ini adalah implementasi sederhana. 
    Validasi 'esai_singkat' di sini hanya mencocokkan string eksak.
    Untuk validasi esai yang lebih canggih, Anda perlu memanggil AI lagi.
    """
    
    if not questions:
        return 0, "N/A"

    correct_count = 0
    total_questions = len(questions)

    for q in questions:
        q_id = q.get('id')
        correct_answer = q.get('jawaban_benar')
        user_answer = answers.get(q_id)

        if not q_id or not correct_answer:
            logging.warning(f"Soal {q.get('teks')} tidak memiliki ID atau jawaban benar.")
            continue
        
        # Perbandingan sederhana, hilangkan spasi di awal/akhir
        if user_answer and user_answer.strip() == correct_answer.strip():
            correct_count += 1
            
    # Hitung Skor
    try:
        score = (correct_count / total_questions) * 100
    except ZeroDivisionError:
        return 0, "N/A"

    # Tentukan Level (Logika sederhana, bisa disesuaikan)
    level = "Pemula"
    if score >= 85:
        level = "Ahli"
    elif score >= 70:
        level = "Mahir"
    elif score >= 50:
        level = "Menengah"

    logging.info(f"Validasi selesai: {correct_count}/{total_questions} benar. Skor: {score}, Level: {level}")
    
    # Kembalikan skor (int) dan level (str)
    return int(score), level
