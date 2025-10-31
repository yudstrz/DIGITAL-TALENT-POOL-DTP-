# pages/3_💡_Rekomendasi_Karier.py
"""
HALAMAN REKOMENDASI - ALL IN ONE
Analisis profil + rekomendasi pekerjaan & pelatihan
"""

import streamlit as st
import json
import random
import requests

from config import (
    EXCEL_PATH, SHEET_LOWONGAN,
    GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL
)

# ========================================
# KONFIGURASI
# ========================================
st.set_page_config(
    page_title="Rekomendasi Karier", 
    page_icon="💡", 
    layout="wide"
)


# ========================================
# FUNGSI 1: CALL GEMINI API
# ========================================
def call_gemini_api(prompt: str) -> str:
    """Kirim request ke Gemini API"""
    url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        content = result['candidates'][0]['content']['parts'][0]['text']
        return content.strip()
        
    except Exception as e:
        raise Exception(f"Error calling Gemini: {e}")


# ========================================
# FUNGSI 2: ANALISIS PROFIL AI
# ========================================
def analyze_career_profile_ai(profil_teks: str):
    """
    Analisis profil karier dengan AI Gemini
    Return: Markdown text hasil analisis
    """
    prompt = f"""Anda adalah career coach profesional.
Analisis profil berikut dan berikan insight karier.

=== PROFIL ===
{profil_teks}

Buat analisis dalam format Markdown:

## 1. Ringkasan Profil
- Ringkas kekuatan utama

## 2. Potensi Karier
- 2-3 bidang okupasi TIK yang cocok
- Alasan pemilihan

## 3. Rekomendasi Pengembangan
- Skill yang perlu ditingkatkan
- Platform belajar yang disarankan

## 4. Catatan Motivasi
- Pesan motivasi singkat

Bahasa Indonesia profesional, ringkas, inspiratif.
"""

    try:
        ai_response = call_gemini_api(prompt)
        return ai_response
    except Exception as e:
        st.error(f"❌ Gagal analisis: {e}")
        return "⚠️ Terjadi kesalahan saat menganalisis profil."


# ========================================
# FUNGSI 3: REKOMENDASI PEKERJAAN & PELATIHAN
# ========================================
def get_recommendations(okupasi_id, skill_gap, profil_teks):
    """
    Return: (jobs, trainings)
    Untuk demo, pakai data dummy
    """
    # Data dummy pekerjaan
    job_samples = [
        {
            "Posisi": "Data Analyst",
            "Perusahaan": "Tech Innovate",
            "Lokasi": "Jakarta",
            "Keterampilan_Dibutuhkan": "Python, SQL, Power BI",
            "Deskripsi_Pekerjaan": "Menganalisis data untuk mendukung keputusan bisnis."
        },
        {
            "Posisi": "Machine Learning Engineer",
            "Perusahaan": "AI Labs",
            "Lokasi": "Bandung",
            "Keterampilan_Dibutuhkan": "Python, TensorFlow, AWS",
            "Deskripsi_Pekerjaan": "Membangun model AI untuk produksi."
        },
        {
            "Posisi": "DevOps Engineer",
            "Perusahaan": "CloudTech",
            "Lokasi": "Jakarta",
            "Keterampilan_Dibutuhkan": "Docker, Kubernetes, CI/CD",
            "Deskripsi_Pekerjaan": "Mengelola infrastruktur cloud dan automation."
        }
    ]

    # Data dummy pelatihan
    training_samples = [
        "Pelatihan Cloud Computing (AWS/GCP Fundamentals)",
        "Kursus CI/CD Pipelines untuk DevOps",
        "Workshop Manajemen Proyek Agile",
        "Bootcamp Machine Learning Intermediate",
        "Sertifikasi Data Engineering Professional"
    ]

    # Random sampling untuk demo
    jobs = random.sample(job_samples, k=min(2, len(job_samples)))
    trainings = random.sample(training_samples, k=min(3, len(training_samples)))

    return jobs, trainings


# ========================================
# JUDUL
# ========================================
st.title("💡 3. Rekomendasi Karier Terpersonalisasi")
st.markdown("""
Temukan **jalur karier** dan **pelatihan terbaik** 
berdasarkan profil & asesmen Anda.
""")


# ========================================
# ANALISIS PROFIL AI
# ========================================
st.markdown("### 🔍 Analisis Profil Karier Otomatis")

user_profile = st.text_area(
    "Deskripsi singkat pengalaman & minat:",
    placeholder="Contoh: Saya tertarik analisis data, punya pengalaman Python..."
)

if user_profile:
    st.session_state["profil_teks"] = user_profile

if st.button("🔎 Analisis dengan AI"):
    if user_profile.strip():
        with st.spinner("🤖 AI sedang menganalisis..."):
            hasil_analisis = analyze_career_profile_ai(user_profile)
            st.success("✅ Analisis berhasil!")
            
            st.markdown("### 🧭 Hasil Analisis Karier")
            st.markdown(hasil_analisis)
    else:
        st.warning("⚠️ Isi deskripsi profil terlebih dahulu")

st.divider()


# ========================================
# VALIDASI ASESMEN
# ========================================
if 'assessment_score' not in st.session_state:
    st.error("""
    ⚠️ Anda harus selesai **Asesmen Kompetensi** dulu!
    """)
    st.stop()

if 'mapped_okupasi_id' not in st.session_state:
    st.error("⚠️ Data okupasi belum tersedia.")
    st.stop()

if 'profil_teks' not in st.session_state:
    st.warning("⚠️ Isi deskripsi profil di atas dulu.")
    st.stop()


# ========================================
# INFO PROFIL
# ========================================
st.markdown("### 👤 Profil Anda")

col1, col2, col3 = st.columns(3)
col1.metric(
    "Talent ID", 
    st.session_state.get('talent_id', '-')
)
col2.metric(
    "Okupasi", 
    st.session_state.get('mapped_okupasi_nama', '-')
)
col3.metric(
    "Skor", 
    f"{st.session_state.assessment_score}/100"
)

st.divider()


# ========================================
# AMBIL REKOMENDASI
# ========================================
with st.spinner("🤖 AI sedang memproses rekomendasi..."):
    try:
        jobs, trainings = get_recommendations(
            st.session_state.get('mapped_okupasi_id', ''),
            st.session_state.get('skill_gap', []),
            st.session_state.get('profil_teks', '')
        )
    except Exception as e:
        st.error(f"❌ Gagal ambil rekomendasi: {e}")
        jobs, trainings = [], []


# ========================================
# LAYOUT HASIL (2 KOLOM)
# ========================================
col1, col2 = st.columns(2)

# KOLOM 1: PEKERJAAN
with col1:
    st.markdown("## 💼 Rekomendasi Lowongan")
    
    if not jobs:
        st.info("Belum ada lowongan yang sesuai.")
    else:
        for job in jobs:
            with st.container():
                st.markdown(f"### 🧩 {job['Posisi']}")
                st.caption(f"🏢 {job['Perusahaan']} — 📍 {job['Lokasi']}")
                st.markdown(f"**Skill:** {job['Keterampilan_Dibutuhkan']}")
                
                with st.expander("📘 Deskripsi"):
                    st.write(job['Deskripsi_Pekerjaan'])
                    
                st.markdown("---")

# KOLOM 2: PELATIHAN
with col2:
    st.markdown("## 🎯 Rekomendasi Pelatihan")
    st.markdown(f"""
    **Skill Gap Anda:** 
    `{st.session_state.get('skill_gap', '-')}`
    """)

    if not trainings:
        st.info("Belum ada rekomendasi pelatihan.")
    else:
        for training in trainings:
            st.success(f"📚 {training}")
