# pages/3_💡_Rekomendasi_Karier.py
"""
HALAMAN 3: REKOMENDASI KARIER

ANALOGI: Ini adalah KANTOR KONSULTASI KARIER.
User mendapat rekomendasi pekerjaan dan pelatihan berdasarkan profil & asesmen.

ALUR:
1. User input deskripsi profil tambahan
2. AI analisis profil dengan Gemini
3. Tampilkan hasil analisis karier
4. Cek apakah user sudah asesmen
5. Ambil rekomendasi pekerjaan & pelatihan
6. Tampilkan dalam 2 kolom
"""

import streamlit as st
import json
from ai_engine import get_recommendations, analyze_career_profile_ai

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="Rekomendasi Karier", 
    page_icon="💡", 
    layout="wide"
)


# ========================================
# JUDUL
# ========================================
st.title("💡 3. Rekomendasi Karier Terpersonalisasi")
st.markdown("""
Temukan **jalur karier** dan **pelatihan terbaik** berdasarkan 
profil serta hasil asesmen Anda.
""")


# ========================================
# ANALISIS PROFIL KARIER AI
# ========================================

st.markdown("### 🔍 Analisis Profil Karier Otomatis")

user_profile = st.text_area(
    "Masukkan deskripsi singkat tentang pengalaman & minat:",
    placeholder="Contoh: Saya tertarik analisis data dan telah belajar Python..."
)

# Simpan ke session state
if user_profile:
    st.session_state["profil_teks"] = user_profile

if st.button("🔎 Analisis dengan AI"):
    if user_profile.strip():
        with st.spinner("🤖 AI sedang menganalisis profil..."):
            hasil_analisis = analyze_career_profile_ai(user_profile)
            st.success("✅ Analisis berhasil!")

            try:
                # Parse hasil (bisa dict atau JSON string)
                if isinstance(hasil_analisis, dict):
                    data = hasil_analisis
                else:
                    data = json.loads(hasil_analisis)
            
                analisis = data.get("career_analysis", {})

                # Tampilkan hasil
                st.markdown("### 🧭 Hasil Analisis Karier")
                st.markdown(f"""
                **Profil Input:** {analisis.get('profil_input', '-')}
                """)
                st.divider()

                # Analisis Profesional
                if "analisis_profesional" in analisis:
                    for bagian in analisis["analisis_profesional"]:
                        st.markdown(f"#### 📘 {bagian.get('judul', '')}")
                        konten = bagian.get("konten", [])

                        if isinstance(konten, list):
                            for item in konten:
                                if isinstance(item, dict):
                                    if "okupasi" in item:
                                        st.markdown(f"""
                                        **Okupasi:** {item['okupasi']}
                                        """)
                                    if "alasan" in item:
                                        st.markdown(f"""
                                        **Alasan:** {item['alasan']}
                                        """)
                                    if "skill_utama" in item:
                                        st.markdown(f"""
                                        **Skill Utama:** {item['skill_utama']}
                                        """)
                                else:
                                    st.write(f"- {item}")
                        else:
                            st.write(konten)
                        st.markdown("---")

                # Saran Aktivitas
                if "saran_aktivitas" in analisis:
                    st.markdown("### 🚀 Saran Aktivitas & Langkah Pengembangan")
                    for key, val in analisis["saran_aktivitas"].items():
                        st.markdown(f"""
                        **{key.replace('_',' ').title()}**: {val}
                        """)

            except json.JSONDecodeError:
                # Jika gagal parse, tampilkan raw
                st.markdown("**Hasil AI (teks mentah):**")
                st.code(hasil_analisis, language="json")
    else:
        st.warning("⚠️ Mohon isi deskripsi profil terlebih dahulu")

st.divider()


# ========================================
# VALIDASI ASESMEN
# ========================================
"""
User HARUS sudah selesai asesmen untuk melihat rekomendasi.
Seperti harus lulus ujian dulu sebelum dapat sertifikat.
"""

if 'assessment_score' not in st.session_state:
    st.error("""
    ⚠️ Anda harus menyelesaikan **Asesmen Kompetensi** 
    terlebih dahulu untuk melihat rekomendasi.
    """)
    st.stop()

if 'mapped_okupasi_id' not in st.session_state or 'skill_gap' not in st.session_state:
    st.error("""
    ⚠️ Data okupasi atau skill gap belum tersedia. 
    Selesaikan tahap asesmen terlebih dahulu.
    """)
    st.stop()

if 'profil_teks' not in st.session_state:
    st.warning("""
    ⚠️ Deskripsi profil belum dimasukkan. 
    Silakan isi bagian atas terlebih dahulu.
    """)
    st.stop()


# ========================================
# INFO PROFIL USER
# ========================================

st.markdown(f"### 👤 Profil Anda")

col1, col2, col3 = st.columns(3)
col1.metric(
    "Talent ID", 
    st.session_state.get('talent_id', 'Tidak diketahui')
)
col2.metric(
    "Okupasi", 
    st.session_state.get('mapped_okupasi_nama', 'Belum diatur')
)
col3.metric(
    "Skor Asesmen", 
    f"{st.session_state.assessment_score} / 100"
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
        st.error(f"❌ Gagal mengambil rekomendasi: {e}")
        jobs, trainings = [], []


# ========================================
# LAYOUT HASIL (2 KOLOM)
# ========================================

col1, col2 = st.columns(2)

# KOLOM 1: REKOMENDASI PEKERJAAN
with col1:
    st.markdown("## 💼 Rekomendasi Lowongan Pekerjaan")
    
    if not jobs:
        st.info("Belum ada lowongan yang sesuai saat ini.")
    else:
        for job in jobs:
            with st.container():
                st.markdown(f"### 🧩 {job['Posisi']}")
                st.caption(f"""
                🏢 {job['Perusahaan']} — 📍 {job['Lokasi']}
                """)
                st.markdown(f"""
                **Keterampilan Dibutuhkan:** 
                {job['Keterampilan_Dibutuhkan']}
                """)
                
                with st.expander("📘 Lihat Deskripsi Pekerjaan"):
                    st.write(job['Deskripsi_Pekerjaan'])
                    
                st.markdown("---")

# KOLOM 2: REKOMENDASI PELATIHAN
with col2:
    st.markdown("## 🎯 Rekomendasi Pelatihan")
    st.markdown(f"""
    **Skill Gap Anda:** 
    `{st.session_state.get('skill_gap', 'Tidak tersedia')}`
    """)

    if not trainings:
        st.info("Belum ada rekomendasi pelatihan yang sesuai.")
    else:
        for training in trainings:
            st.success(f"📚 {training}")
