# pages/4_📊_Dashboard_Nasional.py
"""
HALAMAN DASHBOARD - TANPA AI
Visualisasi data agregat (data dummy untuk demo)
"""

import streamlit as st
import pandas as pd

# ========================================
# KONFIGURASI
# ========================================
st.set_page_config(
    page_title="Dashboard Nasional", 
    page_icon="📊", 
    layout="wide"
)


# ========================================
# FUNGSI: GET DASHBOARD DATA (DUMMY)
# ========================================
def get_national_dashboard_data():
    """
    Return data dummy untuk visualisasi
    Dalam produksi, ini akan ambil dari database
    """
    # 1. Distribusi Okupasi (dummy)
    distribusi_okupasi = pd.DataFrame({
        'Okupasi': ['Data Analyst', 'DevOps Engineer', 'AI Engineer', 'UI/UX Designer'],
        'Jumlah_Talenta': [45, 32, 28, 20]
    }).set_index('Okupasi')

    # 2. Sebaran Lokasi (dummy)
    sebaran_lokasi = pd.DataFrame({
        'Lokasi': ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Medan'],
        'Jumlah': [50, 30, 25, 20, 15],
        'lat': [-6.20, -6.91, -7.25, -7.79, 3.59],
        'lon': [106.81, 107.61, 112.75, 110.36, 98.67],
        'size': [50, 30, 25, 20, 15]
    })
    
    # 3. Skill Gap (dummy)
    skill_gap_umum = pd.DataFrame({
        'Keterampilan': ['Cloud Computing', 'AI/ML', 'Project Management', 'Data Governance'],
        'Jumlah_Gap': [120, 95, 80, 65]
    }).set_index('Keterampilan')

    return distribusi_okupasi, sebaran_lokasi, skill_gap_umum


# ========================================
# JUDUL
# ========================================
st.title("📊 4. Dashboard Talenta Digital Nasional")
st.markdown("""
Visualisasi data agregat untuk pemangku kepentingan.

**Catatan:** Data ini adalah simulasi untuk demo.
""")


# ========================================
# AMBIL DATA
# ========================================
with st.spinner("📡 Mengagregasi data..."):
    dist_okupasi, sebaran_lokasi, skill_gap = get_national_dashboard_data()


# ========================================
# VISUALISASI 1: DISTRIBUSI OKUPASI
# ========================================
st.header("📊 Distribusi Okupasi Talenta")
st.markdown("Berapa banyak talenta di setiap okupasi PON TIK")

if not dist_okupasi.empty:
    st.bar_chart(dist_okupasi)
    
    top_okupasi = dist_okupasi.idxmax()[0]
    st.info(f"💡 **Insight:** Okupasi terbanyak: **{top_okupasi}**")
else:
    st.warning("⚠️ Belum ada data")

st.markdown("---")


# ========================================
# VISUALISASI 2: SEBARAN LOKASI
# ========================================
st.header("🗺️ Sebaran Talenta Nasional")
st.markdown("Peta interaktif lokasi talenta digital Indonesia")

if not sebaran_lokasi.empty:
    st.map(sebaran_lokasi, size='size', zoom=4)
    
    top_lokasi = sebaran_lokasi.nlargest(1, 'Jumlah')
    if not top_lokasi.empty:
        st.info(f"""
        💡 **Insight:** Kota terbanyak: 
        **{top_lokasi.iloc[0]['Lokasi']}** 
        ({top_lokasi.iloc[0]['Jumlah']} talenta)
        """)
else:
    st.warning("⚠️ Belum ada data")

st.markdown("---")


# ========================================
# VISUALISASI 3: SKILL GAP
# ========================================
st.header("📉 Skill Gap Nasional (Top 4)")
st.markdown("Keterampilan yang paling banyak kurang dikuasai")

if not skill_gap.empty:
    st.bar_chart(skill_gap)
    
    top_gap = skill_gap.idxmax()[0]
    st.warning(f"""
    ⚠️ **Insight:** Gap terbesar: **{top_gap}**
    
    **Rekomendasi:**
    - Pemerintah: Fokus pelatihan di skill ini
    - EduTech: Buat kursus untuk skill ini
    - Industri: In-house training
    """)
else:
    st.warning("⚠️ Belum ada data")

st.markdown("---")


# ========================================
# METRICS TAMBAHAN
# ========================================
st.markdown("### 📈 Metrics Tambahan")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Talenta", 
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
# EXPORT (PLACEHOLDER)
# ========================================
st.markdown("### 📥 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Export Excel"):
        st.info("Fitur akan segera hadir!")
        
with col2:
    if st.button("📊 Generate Report"):
        st.info("Fitur akan segera hadir!")
        
with col3:
    if st.button("📧 Email Dashboard"):
        st.info("Fitur akan segera hadir!")


# ========================================
# FOOTER
# ========================================
st.info("""
📌 **Catatan:**
Data adalah agregasi dari talenta yang:
1. Terdaftar di sistem
2. Dipetakan ke okupasi PON TIK
3. Selesai asesmen kompetensi
""")
