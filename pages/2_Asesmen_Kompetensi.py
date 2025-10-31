# pages/2_🧠_Asesmen_Kompetensi.py
"""
HALAMAN ASESMEN - ALL IN ONE
Generate soal dengan Gemini AI + Validasi jawaban
"""

import streamlit as st
import pandas as pd
import json
import re
import requests
import datetime

from config import (
    EXCEL_PATH, SHEET_PON, 
    GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL,
    JUMLAH_SOAL
)

# ========================================
# KONFIGURASI
# ========================================
st.set_page_config(
    page_title="Asesmen Kompetensi", 
    page_icon="🧠", 
    layout="wide"
)


# ========================================
# FUNGSI 1: LOAD EXCEL
# ========================================
@st.cache_data
def load_excel_sheet(file_path, sheet_name):
    """Membaca sheet dari Excel"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        df.columns = df.columns.str.strip()
        df = df.fillna('')
        return df
    except Exception as e:
        st.error(f"Gagal memuat sheet: {e}")
        return None


# ========================================
# FUNGSI 2: CALL GEMINI API
# ========================================
def call_gemini_api(prompt: str) -> str:
    """
    Kirim request ke Gemini API
    Return: Response text dari AI
    """
    url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    json_instruction = """
PENTING: Respons HARUS JSON valid.
Format:
{
  "questions": [
    {"id": "q1", "teks": "...", "opsi": ["A", "B", "C", "D"], "jawaban_benar": "A"}
  ]
}
"""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt + json_instruction}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 3000
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # Ekstrak text
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Clean markdown fence
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return content
        
    except Exception as e:
        raise Exception(f"Error calling Gemini: {e}")


# ========================================
# FUNGSI 3: SANITIZE JSON
# ========================================
def sanitize_json_response(text: str) -> str:
    """Bersihkan JSON dari karakter aneh"""
    # Hapus escape sequence invalid
    text = re.sub(r'\\(?![ntr"\\/bfuU])', '', text)
    text = text.replace("\\'", "'")
    
    # Hapus control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Fix missing commas
    text = re.sub(r'\}\s*\{', '},{', text)
    text = re.sub(r'\]\s*"', '],"', text)
    
    return text.strip()


# ========================================
# FUNGSI 4: GENERATE SOAL
# ========================================
def generate_assessment_questions(okupasi_id: str):
    """
    Generate soal dengan AI Gemini
    Return: List of dict (5 soal)
    """
    # Load data okupasi
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
    
    if df_pon is None:
        raise Exception("Gagal load data PON TIK")
    
    # Cari okupasi
    pon_data = df_pon[df_pon['OkupasiID'] == okupasi_id]
    
    if pon_data.empty:
        raise Exception(f"Okupasi {okupasi_id} tidak ditemukan")
    
    okupasi_info = pon_data.iloc[0]
    okupasi_nama = okupasi_info['Okupasi']
    unit_kompetensi = okupasi_info['Unit_Kompetensi']
    kuk_keywords = okupasi_info['Kuk_Keywords']
    
    # Buat prompt
    prompt = f"""Anda adalah expert TIK Indonesia.

Buat TEPAT {JUMLAH_SOAL} soal pilihan ganda untuk:

**Okupasi:** {okupasi_nama}
**Unit Kompetensi:** {unit_kompetensi}
**Keterampilan:** {kuk_keywords}

**Kriteria:**
1. Relevan dengan kompetensi
2. Tingkat: Menengah-Ahli
3. Skenario praktis
4. TEPAT 4 opsi per soal
5. 1 jawaban benar
6. Bahasa Indonesia
7. HINDARI karakter khusus

**Format JSON:**
{{
  "questions": [
    {{
      "id": "q1",
      "teks": "Pertanyaan...",
      "opsi": ["Opsi A", "Opsi B", "Opsi C", "Opsi D"],
      "jawaban_benar": "Opsi A"
    }}
  ]
}}

ATURAN:
- {JUMLAH_SOAL} soal (q1-q{JUMLAH_SOAL})
- Pisahkan dengan koma
- jawaban_benar = salah satu opsi
- Output HANYA JSON
"""

    try:
        # Call API
        response_text = call_gemini_api(prompt)
        
        # Sanitize & parse
        response_text = sanitize_json_response(response_text)
        response_json = json.loads(response_text)
        
        # Ekstrak questions
        if isinstance(response_json, dict) and "questions" in response_json:
            questions = response_json["questions"]
        elif isinstance(response_json, list):
            questions = response_json
        else:
            raise ValueError("Format tidak dikenali")
        
        # Validasi jumlah
        if len(questions) != JUMLAH_SOAL:
            st.warning(f"AI buat {len(questions)} soal, bukan {JUMLAH_SOAL}")
            # Tambah dummy jika kurang
            while len(questions) < JUMLAH_SOAL:
                questions.append({
                    "id": f"q{len(questions)+1}",
                    "teks": f"[Soal tambahan] Bagaimana menangani darurat di {okupasi_nama}?",
                    "opsi": ["Eskalasi", "Konsultasi", "Dokumentasi", "Trial"],
                    "jawaban_benar": "Konsultasi"
                })
            questions = questions[:JUMLAH_SOAL]
        
        # Validasi struktur
        for i, q in enumerate(questions):
            if not all(k in q for k in ["id", "teks", "opsi", "jawaban_benar"]):
                raise ValueError(f"Soal {i+1} struktur tidak lengkap")
            
            if len(q["opsi"]) != 4:
                raise ValueError(f"Soal {i+1} tidak punya 4 opsi")
            
            if q["jawaban_benar"] not in q["opsi"]:
                raise ValueError(f"Soal {i+1}: Jawaban tidak di opsi")
            
            q["id"] = f"q{i+1}"
            q["tipe"] = "pilihan_ganda"
        
        return questions
        
    except json.JSONDecodeError as e:
        error_msg = f"❌ Error parsing JSON: {e}\n\nResponse: {response_text[:2000]}"
        st.error(error_msg)
        raise Exception(error_msg)
        
    except Exception as e:
        st.error(f"❌ Error generate soal: {e}")
        raise


# ========================================
# FUNGSI 5: VALIDASI JAWABAN
# ========================================
def validate_assessment(answers: dict, questions: list):
    """
    Validasi jawaban user
    Return: (skor, level)
    """
    if not questions:
        return 0, "Error"
    
    total = len(questions)
    correct = 0
    
    for q in questions:
        q_id = q['id']
        correct_answer = q['jawaban_benar']
        
        if q_id in answers:
            user_answer = answers[q_id]
            if user_answer == correct_answer:
                correct += 1
    
    # Hitung skor
    skor = int((correct / total) * 100)
    
    # Tentukan level
    if skor >= 90:
        level = "Ahli"
    elif skor >= 70:
        level = "Menengah"
    elif skor >= 50:
        level = "Junior"
    else:
        level = "Pemula"
    
    return skor, level


# ========================================
# VALIDASI USER
# ========================================
st.title("🧠 2. Asesmen Kompetensi")

if not st.session_state.get('talent_id'):
    st.error("❌ Anda harus isi **Profil Talenta** dulu!")
    st.stop()


# ========================================
# INFO TALENTA
# ========================================
st.info(f"👤 Login: **{st.session_state.talent_id}**")
st.header(f"📝 Asesmen: {st.session_state.mapped_okupasi_nama}")
st.markdown("AI telah generate soal sesuai okupasi Anda.")


# ========================================
# GENERATE SOAL (SEKALI SAJA)
# ========================================
if 'questions' not in st.session_state or st.session_state.questions is None:
    with st.spinner("🤖 AI sedang membuat soal..."):
        try:
            questions = generate_assessment_questions(
                st.session_state.mapped_okupasi_id
            )
            st.session_state.questions = questions
            st.success(f"✅ {len(questions)} soal siap!")
        except Exception as e:
            st.error(f"❌ Gagal: {e}")
            st.stop()
else:
    questions = st.session_state.questions
    st.success(f"📋 {len(questions)} soal tersedia")


# ========================================
# FORM ASESMEN
# ========================================
answers = {}

with st.form("assessment_form"):
    for i, q in enumerate(questions):
        st.subheader(f"❓ Pertanyaan {i+1}")
        st.markdown(f"**{q['teks']}**")
        
        if q['tipe'] == 'pilihan_ganda':
            answers[q['id']] = st.radio(
                "Pilih:", 
                q['opsi'], 
                key=q['id'],
                label_visibility="collapsed"
            )
    
    submit = st.form_submit_button("🚀 Kirim Jawaban")


# ========================================
# PROSES SUBMISSION
# ========================================
if submit:
    with st.spinner("🔍 AI sedang menilai..."):
        try:
            skor, level = validate_assessment(
                answers, 
                st.session_state.questions
            )
            
            # Simpan hasil
            st.session_state.assessment_score = skor
            st.session_state.assessment_level = level
            st.session_state.assessment_date = datetime.datetime.now()
            
            # Tampilkan hasil
            st.success("✅ Asesmen Selesai!")
            st.balloons()
            
            st.subheader("📊 Hasil Validasi:")
            col1, col2 = st.columns(2)
            col1.metric("Skor", f"{skor}/100")
            col2.metric("Level", level)
            
            # Detail jawaban
            with st.expander("📝 Detail Jawaban"):
                correct_count = 0
                
                for q in st.session_state.questions:
                    user_ans = answers.get(q['id'], '-')
                    is_correct = user_ans == q['jawaban_benar']
                    
                    if is_correct:
                        correct_count += 1
                        st.success(f"""
                        **{q['teks']}**
                        ✅ Benar: {user_ans}
                        """)
                    else:
                        st.error(f"""
                        **{q['teks']}**
                        ❌ Anda: {user_ans}
                        ✅ Benar: {q['jawaban_benar']}
                        """)
                
                st.info(f"Total: {correct_count}/{len(st.session_state.questions)}")
            
            st.info("""
            💡 **Next:** Lihat rekomendasi di halaman berikutnya!
            """)
            
        except Exception as e:
            st.error(f"❌ Error validasi: {e}")
