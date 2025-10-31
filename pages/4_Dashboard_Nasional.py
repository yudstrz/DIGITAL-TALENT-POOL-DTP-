# pages/4_📊_Dashboard_Nasional.py
"""
HALAMAN 4: DASHBOARD NASIONAL

ANALOGI: Ini adalah PUSAT KOMANDO atau CONTROL ROOM.
Pemangku kepentingan (Pemerintah, Industri, EduTech) bisa melihat
data agregat talenta digital nasional.

ALUR:
1. Ambil data agregat dari database
2. Tampilkan 3 visualisasi utama:
   - Distribusi Okupasi (Bar Chart)
   - Sebaran Lokasi (Map)
   - Skill Gap Nasional (Bar Chart)

TARGET USER:
- Pemerintah: Untuk kebijakan SDM
- Industri: Untuk perencanaan rekrutmen
- EduTech: Untuk desain kurikulum
"""

import streamlit as st
from ai_engine import get_national_dashboard_data

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="Dashboard Nasional", 
    page_icon="📊", 
    layout="wide"
)


# ========================================
# JUDUL
# ========================================
st.title("📊 4. Dashboard Talenta Digital Nasional")
st.markdown("""
Visualisasi data agregat untuk pemangku kepentingan 
(Pemerintah, Industri, EduTech).

**Data ini adalah simulasi** - dalam produksi, data diambil dari:
- Hasil pemetaan profil (Tahap 2)
- Hasil asesmen (Tahap 4)
- Database talenta nasional
""")


# ========================================
# AMBIL DATA
# ========================================

with st.spinner("📡 Mengagregasi data nasional..."):
    dist_okupasi, sebaran_lokasi, skill_gap = get_national_dashboard_data()


# ========================================
# VISUALISASI 1: DISTRIBUSI OKUPASI
# ========================================
"""
ANALOGI: Seperti melihat berapa banyak dokter, insinyur, guru di Indonesia.

INSIGHT:
- Okupasi mana yang paling banyak talenta?
- Okupasi mana yang langka?
- Untuk perencanaan kurikulum EduTech
"""

st.header("📊 Distribusi Okupasi Talenta")
st.markdown("""
Menampilkan berapa banyak talenta di setiap okupasi PON TIK.
""")

if not dist_okupasi.empty:
    st.bar_chart(dist_okupasi)
    
    # Insight otomatis
    top_okupasi = dist_okupasi.idxmax()[0]
    st.info(f"""
    💡 **Insight:**
    Okupasi dengan talenta terbanyak: **{top_okupasi}**
    """)
else:
    st.warning("⚠️ Belum ada data distribusi okupasi")

st.markdown("---")


# ========================================
# VISUALISASI 2: SEBARAN LOKASI
# ========================================
"""
ANALOGI: Seperti melihat peta persebaran penduduk Indonesia.

INSIGHT:
- Kota mana yang paling banyak talenta digital?
- Daerah mana yang perlu perhatian khusus?
- Untuk kebijakan pemerataan SDM
"""

st.header("🗺️ Sebaran Talenta Nasional (Berdasarkan Lokasi)")
st.markdown("""
Peta interaktif menampilkan lokasi talenta digital di Indonesia.
Ukuran bubble = jumlah talenta.
""")

if not sebaran_lokasi.empty:
    st.map(sebaran_lokasi, size='size', zoom=4)
    
    # Insight otomatis
    top_lokasi = sebaran_lokasi.nlargest(1, 'Jumlah')
    if not top_lokasi.empty:
        st.info(f"""
        💡 **Insight:**
        Kota dengan talenta terbanyak: 
        **{top_lokasi.iloc[0]['Lokasi']}** 
        ({top_lokasi.iloc[0]['Jumlah']} talenta)
        """)
else:
    st.warning("⚠️ Belum ada data sebaran lokasi")

st.markdown("---")


# ========================================
# VISUALISASI 3: SKILL GAP NASIONAL
# ========================================
"""
ANALOGI: Seperti melihat kekurangan vitamin di populasi.

INSIGHT:
- Keterampilan apa yang paling langka?
- Prioritas pelatihan nasional
- Untuk desain kurikulum dan kebijakan pelatihan
"""

st.header("📉 Identifikasi Skill Gap Nasional (Top 4)")
st.markdown("""
Menampilkan keterampilan yang paling banyak kurang dikuasai 
oleh talenta digital Indonesia.
""")

if not skill_gap.empty:
    st.bar_chart(skill_gap)
    
    # Insight otomatis
    top_gap = skill_gap.idxmax()[0]
    st.warning(f"""
    ⚠️ **Insight:**
    Skill dengan gap terbesar: **{top_gap}**
    
    **Rekomendasi:**
    - Pemerintah: Fokuskan program pelatihan di skill ini
    - EduTech: Buat kursus untuk skill ini
    - Industri: Pertimbangkan in-house training
    """)
else:
    st.warning("⚠️ Belum ada data skill gap")

st.markdown("---")


# ========================================
# FOOTER INFO
# ========================================

st.info("""
📌 **Catatan:**
Data di atas adalah hasil agregasi dari seluruh talenta yang:
1. Telah terdaftar di sistem
2. Telah dipetakan ke okupasi PON TIK
3. Telah menyelesaikan asesmen kompetensi

**Untuk Akses Penuh:**
- Hubungi admin untuk akses API dashboard
- Data real-time tersedia via REST API
- Export data dalam format Excel/CSV
""")


# ========================================
# ADDITIONAL METRICS (BONUS)
# ========================================

st.markdown("### 📈 Metrics Tambahan")

col1, col2, col3, col4 = st.columns(4)

# Simulasi metrics
col1.metric(
    "Total Talenta Terdaftar", 
    "1,245",
    delta="12 hari ini"
)
col2.metric(
    "Okupasi Terpetakan", 
    "38",
    delta="PON TIK"
)
col3.metric(
    "Asesmen Selesai", 
    "892",
    delta="71.6%"
)
col4.metric(
    "Rata-rata Skor", 
    "74.2",
    delta="+2.3"
)

st.markdown("---")


# ========================================
# EXPORT DATA (PLACEHOLDER)
# ========================================

st.markdown("### 📥 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Export to Excel"):
        st.info("Fitur export akan segera hadir!")
        
with col2:
    if st.button("📊 Generate Report"):
        st.info("Fitur generate report akan segera hadir!")
        
with col3:
    if st.button("📧 Email Dashboard"):
        st.info("Fitur email dashboard akan segera hadir!")
