# pages/4_📊_Dashboard_Nasional.py
import streamlit as st
from ai_engine import get_national_dashboard_data

st.set_page_config(page_title="Dashboard Nasional", page_icon="📊", layout="wide")
st.title("📊 4. Dashboard Talenta Digital Nasional")
st.markdown("Visualisasi data agregat (Tahap 6 & 7) untuk pemangku kepentingan (Pemerintah, Industri, EduTech).")

with st.spinner("Mengagregasi data nasional (Simulasi)..."):
    dist_okupasi, sebaran_lokasi, skill_gap = get_national_dashboard_data()

# --- Visualisasi ---

st.header("Distribusi Okupasi Talenta")
st.bar_chart(dist_okupasi)

st.header("Sebaran Talenta Nasional (Berdasarkan Lokasi)")
st.map(sebaran_lokasi, size='size', zoom=4)

st.header("Identifikasi Skill Gap Nasional (Top 4)")
st.bar_chart(skill_gap)

st.info("Data di atas adalah hasil simulasi agregasi dari seluruh talenta yang terdaftar dan terpetakan.")
