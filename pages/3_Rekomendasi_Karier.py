# pages/3_💡_Rekomendasi_Karier.py
import streamlit as st
from ai_engine import get_recommendations

st.set_page_config(page_title="Rekomendasi Karier", page_icon="💡", layout="wide")
st.title("💡 3. Rekomendasi Karier Terpersonalisasi (Tahap 5)")

# Cek apakah pengguna sudah asesmen
if not st.session_state.get('assessment_score'):
    st.error("Anda harus menyelesaikan 'Asesmen Kompetensi' terlebih dahulu untuk melihat rekomendasi.")
    st.stop()

# Cek data profil
if not st.session_state.get('profile_text'):
    st.error("Data profil Anda tidak ditemukan. Harap isi kembali di halaman 'Profil Talenta'.")
    st.stop()
    
st.info(f"Menampilkan rekomendasi untuk: **{st.session_state.talent_id}**")
st.header(f"Okupasi Anda: {st.session_state.mapped_okupasi_nama}")
st.metric("Skor Asesmen", f"{st.session_state.assessment_score} / 100")

with st.spinner("Mengambil rekomendasi pekerjaan dan pelatihan (Simulasi AI)..."):
    # --- PERUBAHAN DI SINI ---
    jobs, trainings = get_recommendations(
        st.session_state.mapped_okupasi_id,
        st.session_state.skill_gap,
        st.session_state.profile_text  # Mengirim profil untuk matching lowongan
    )
    # -------------------------

col1, col2 = st.columns(2)

# Kolom 1: Rekomendasi Pekerjaan (Content-Based)
with col1:
    st.subheader("Rekomendasi Lowongan (Paling Mirip Profil Anda)")
    if not jobs:
        st.warning("Belum ada lowongan yang sesuai saat ini.")
    else:
        for job in jobs:
            with st.container(border=True):
                st.markdown(f"**{job['Posisi']}**")
                st.markdown(f"*{job['Perusahaan']} - {job.get('Lokasi', 'N/A')}*")
                st.caption(f"Keterampilan: {job['Keterampilan_Dibutuhkan']}")
                with st.expander("Lihat Deskripsi"):
                    st.write(job['Deskripsi_Pekerjaan'])

# Kolom 2: Rekomendasi Pelatihan (Rule-Based)
with col2:
    st.subheader("Rekomendasi Pelatihan (Penutup Skill Gap)")
    st.warning(f"**Skill Gap (Simulasi):** {st.session_state.skill_gap}")
    
    if not trainings:
        st.info("Tidak ada rekomendasi pelatihan.")
    else:
        for training in trainings:
            st.success(f"**{training}**")
