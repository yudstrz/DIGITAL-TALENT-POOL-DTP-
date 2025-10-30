# pages/3_💡_Rekomendasi_Karier.py
import streamlit as st
from ai_engine import get_recommendations, analyze_career_profile_ai

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Rekomendasi Karier",
    page_icon="💡",
    layout="wide"
)

# --- Judul Utama ---
st.title("💡 3. Rekomendasi Karier Terpersonalisasi (Tahap 5)")

# --- Seksi Analisis Profil Karier Otomatis ---
st.subheader("🔍 Analisis Profil Karier Otomatis")
user_profile = st.text_area("Masukkan deskripsi singkat tentang pengalaman & minatmu:")

if st.button("Analisis dengan AI"):
    if user_profile.strip():
        with st.spinner("AI sedang menganalisis profil..."):
            hasil_analisis = analyze_career_profile_ai(user_profile)
            st.markdown(hasil_analisis)
    else:
        st.warning("Mohon isi deskripsi profil terlebih dahulu.")

st.markdown("---")

# --- Cek apakah pengguna sudah melakukan asesmen ---
if not st.session_state.get('assessment_score'):
    st.error("Anda harus menyelesaikan 'Asesmen Kompetensi' terlebih dahulu untuk melihat rekomendasi.")
    st.stop()

# --- Informasi Umum ---
st.info(f"Menampilkan rekomendasi untuk: **{st.session_state.talent_id}**")
st.header(f"Okupasi Anda: {st.session_state.mapped_okupasi_nama}")
st.metric("Skor Asesmen", f"{st.session_state.assessment_score} / 100")

# --- Ambil Rekomendasi dari AI Engine ---
with st.spinner("Mengambil rekomendasi pekerjaan dan pelatihan (Simulasi AI)..."):
    jobs, trainings = get_recommendations(
        st.session_state.mapped_okupasi_id,
        st.session_state.skill_gap
    )

# --- Tampilkan Hasil Rekomendasi ---
col1, col2 = st.columns(2)

# Kolom 1: Rekomendasi Pekerjaan
with col1:
    st.subheader("💼 Rekomendasi Lowongan Pekerjaan")
    if not jobs:
        st.warning("Belum ada lowongan yang sesuai saat ini.")
    else:
        for job in jobs:
            with st.container(border=True):
                st.markdown(f"**{job['Posisi']}**")
                st.markdown(f"*{job['Perusahaan']} - {job['Lokasi']}*")
                st.caption(f"Keterampilan: {job['Keterampilan_Dibutuhkan']}")
                with st.expander("Lihat Deskripsi"):
                    st.write(job['Deskripsi_Pekerjaan'])

# Kolom 2: Rekomendasi Pelatihan
with col2:
    st.subheader("🎯 Rekomendasi Pelatihan (Penutup Skill Gap)")
    st.warning(f"**Skill Gap Anda:** {st.session_state.skill_gap}")

    if not trainings:
        st.info("Tidak ada rekomendasi pelatihan.")
    else:
        for training in trainings:
            st.success(f"**{training}**\n\n*Direkomendasikan untuk menutup gap Anda.*")
