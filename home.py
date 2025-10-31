# Home.py
"""
HALAMAN UTAMA: LANDING PAGE

ANALOGI: Ini adalah PINTU DEPAN atau LOBBY sistem.
User pertama kali masuk akan melihat halaman ini.

FUNGSI:
1. Menyambut user
2. Menjelaskan sistem
3. Mengarahkan user ke halaman yang sesuai
"""

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
        background-color: #f0f2f6;
        padding: 1.5em;
        border-radius: 10px;
        margin: 1em 0;
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

Sistem ini menggunakan **PON TIK (Profil Okupasi Nasional Teknologi Informasi dan Komunikasi)** 
sebagai standar kompetensi.
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
```
1️⃣ PROFIL TALENTA
   ↓ Upload CV → AI ekstraksi → Mapping ke PON TIK
   
2️⃣ ASESMEN KOMPETENSI
   ↓ AI generate soal → User jawab → Scoring otomatis
   
3️⃣ REKOMENDASI KARIER
   ↓ Analisis profil + asesmen → Rekomendasi pekerjaan & pelatihan
   
4️⃣ DASHBOARD NASIONAL
   ↓ Agregasi data → Visualisasi untuk stakeholder
```
""")

st.markdown("---")


# ========================================
# TEKNOLOGI
# ========================================

st.markdown("## 🛠️ Teknologi yang Digunakan")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Frontend:**
    - Streamlit
    - Plotly
    - Pandas
    """)

with col2:
    st.markdown("""
    **AI/ML:**
    - Google Gemini API
    - Scikit-learn (TF-IDF)
    - Cosine Similarity
    """)

with col3:
    st.markdown("""
    **Database:**
    - Excel (PON TIK)
    - Session State (temp)
    - Future: PostgreSQL
    """)

st.markdown("---")


# ========================================
# STATISTIK (SIMULASI)
# ========================================

st.markdown("## 📈 Statistik Platform")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="🎓 Total Talenta",
    value="1,245",
    delta="12 hari ini"
)

col2.metric(
    label="🏢 Okupasi PON TIK",
    value="38",
    delta="Standar Nasional"
)

col3.metric(
    label="✅ Asesmen Selesai",
    value="892",
    delta="71.6%"
)

col4.metric(
    label="⭐ Rata-rata Skor",
    value="74.2",
    delta="+2.3"
)

st.markdown("---")


# ========================================
# CALL TO ACTION
# ========================================

st.markdown("## 🚀 Mulai Sekarang!")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 2em;">
        <h3>Siap memvalidasi kompetensi Anda?</h3>
        <p>Klik tombol di sidebar untuk memulai:</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 Mulai dari Profil Talenta", use_container_width=True):
        st.switch_page("pages/1_👤_Profil_Talenta.py")

st.markdown("---")


# ========================================
# FOOTER
# ========================================

st.markdown("### 📞 Kontak & Dukungan")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📧 Email:**
    support@dtp.co.id
    """)

with col2:
    st.markdown("""
    **🌐 Website:**
    www.digitaltalentplatform.id
    """)

with col3:
    st.markdown("""
    **💬 Telegram:**
    @DTPSupport
    """)

st.markdown("---")

st.markdown("""
<div style="text-align: center; color: #999; padding: 2em;">
    <p>© 2025 Digital Talent Platform | Powered by AI 🤖</p>
    <p>Standar PON TIK | Kementerian Komunikasi dan Informatika</p>
</div>
""", unsafe_allow_html=True)


# ========================================
# SIDEBAR INFO
# ========================================

with st.sidebar:
    st.markdown("## 📚 Panduan Navigasi")
    
    st.markdown("""
    **Untuk Talenta:**
    1. 👤 Profil Talenta
    2. 🧠 Asesmen Kompetensi
    3. 💡 Rekomendasi Karier
    
    **Untuk Stakeholder:**
    4. 📊 Dashboard Nasional
    """)
    
    st.markdown("---")
    
    st.markdown("## ℹ️ Status Sistem")
    st.success("✅ AI Engine: Online")
    st.success("✅ Database: Connected")
    st.info("📊 Versi: 1.0.0")
    
    st.markdown("---")
    
    st.markdown("## 🆘 Bantuan")
    st.markdown("""
    Butuh bantuan?
    - 📖 [Dokumentasi](https://docs.dtp.id)
    - 🎥 [Video Tutorial](https://youtube.com/dtp)
    - 💬 [FAQ](https://dtp.id/faq)
    """)
