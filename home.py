# Home.py
# HALAMAN UTAMA: LANDING PAGE

# ANALOGI: Ini adalah PINTU DEPAN atau LOBBY sistem.
# User pertama kali masuk akan melihat halaman ini.

# FUNGSI:
# 1. Menyambut user
# 2. Menjelaskan sistem
# 3. Mengarahkan user ke halaman yang sesuai

import streamlit as st

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="Digital Talent Platform", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========================================
# CUSTOM CSS (STYLING)
# ========================================
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 0.5em;
    }
    .sub-header {
        font-size: 1.5em;
        text-align: center;
        color: #666;
        margin-bottom: 2em;
    }
    .feature-box {
        background-color: #f0f2f6; /* Latar belakang terang */
        padding: 1.5em;
        border-radius: 10px;
        margin: 1em 0;
        color: #333333; /* <-- PERBAIKAN: Warna teks gelap agar terbaca */
    }
    .metric-box {
        text-align: center;
        padding: 1em;
    }
</style>
""", unsafe_allow_html=True)


# ========================================
# HEADER
# ========================================
st.markdown('<p class="main-header">🚀 Digital Talent Platform</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Platform AI-Powered untuk Pemetaan & Validasi Talenta Digital Indonesia</p>', unsafe_allow_html=True)

st.markdown("---")


# ========================================
# PENJELASAN SISTEM
# ========================================

st.markdown("## 🎯 Apa itu Digital Talent Platform?")

st.markdown("""
**Digital Talent Platform (DTP)** adalah sistem berbasis AI yang membantu:

- 👤 **Talenta Digital**: Validasi kompetensi & rekomendasi karier
- 🏢 **Perusahaan**: Temukan talenta yang sesuai kebutuhan
- 🏛️ **Pemerintah**: Monitoring SDM digital nasional
- 📚 **EduTech**: Desain kurikulum berbasis data real

Sistem ini menggunakan **PON TIK (Profil Okupasi Nasional Teknologi Informasi dan Komunikasi)** sebagai standar kompetensi.
""")

st.markdown("---")


# ========================================
# FITUR UTAMA
# ========================================

st.markdown("## ✨ Fitur Utama")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>🤖 AI-Powered Mapping</h3>
        <p>AI menganalisis CV Anda dan memetakan ke okupasi PON TIK yang sesuai menggunakan semantic search.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>🧠 Asesmen Kompetensi</h3>
        <p>AI generate soal asesmen otomatis sesuai okupasi Anda. Validasi kompetensi dengan scoring objektif.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>💡 Rekomendasi Karier</h3>
        <p>Dapatkan rekomendasi lowongan pekerjaan dan pelatihan yang sesuai dengan profil & skill gap Anda.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>📊 Dashboard Nasional</h3>
        <p>Visualisasi data agregat untuk pemangku kepentingan: distribusi okupasi, sebaran lokasi, skill gap.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ========================================
# ALUR KERJA SISTEM
# ========================================

st.markdown("## 🔄 Alur Kerja Sistem")

st.markdown("""
