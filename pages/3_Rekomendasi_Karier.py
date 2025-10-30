# pages/3_💡_Rekomendasi_Karier.py
import streamlit as st
# --- PERBAIKAN: Import KEDUA fungsi ---
from ai_engine import get_recommendations, get_personalized_career_path

st.set_page_config(page_title="Rekomendasi Karier", page_icon="💡", layout="wide")
st.title("💡 3. Rekomendasi Karier Terpersonalisasi (Tahap 5)")

# --- PERBAIKAN: Cek prasyarat lebih lengkap ---
if (not st.session_state.get('assessment_score') 
    or not st.session_state.get('profile_text')
    or not st.session_state.get('skill_gap')):
    st.error("Anda harus menyelesaikan 'Profil Talenta' dan 'Asesmen Kompetensi' terlebih dahulu.")
    st.stop()

# Tampilkan info header
st.info(f"Menampilkan rekomendasi untuk: **{st.session_state.talent_id}**")
col_info1, col_info2 = st.columns(2)
col_info1.header(f"Okupasi Anda: {st.session_state.mapped_okupasi_nama}")
col_info2.metric("Skor Asesmen", f"{st.session_state.assessment_score} / 100")
st.divider()


# --- BAGIAN 1: Roadmap Karier dari AI (TAMBAHAN ANDA) ---
st.header("🚀 Roadmap Karier Terpersonalisasi (dari AI)")

# Generate roadmap AI hanya sekali per sesi
if 'career_path_recommendation' not in st.session_state:
    with st.spinner("🤖 AI sedang membuat roadmap karier terpersonalisasi untuk Anda..."):
        try:
            # Kumpulkan semua data yang diperlukan untuk prompt AI
            recommendation_md = get_personalized_career_path(
                okupasi_nama=st.session_state.mapped_okupasi_nama,
                skor=st.session_state.assessment_score,
                skill_gap=st.session_state.skill_gap,
                profile_text=st.session_state.profile_text
            )
            # Simpan ke session state
            st.session_state.career_path_recommendation = recommendation_md
            st.success("Roadmap AI berhasil dibuat!")
        
        except Exception as e:
            st.error(f"❌ Gagal membuat rekomendasi AI: {e}")
            # Simpan pesan error agar tidak dicoba lagi
            st.session_state.career_path_recommendation = "Gagal memuat rekomendasi AI."

# Tampilkan roadmap AI yang sudah disimpan
with st.container(border=True):
    st.markdown(
        st.session_state.get('career_path_recommendation', 'Memuat...'), 
        unsafe_allow_html=True
    )

st.divider()


# --- BAGIAN 2: Rekomendasi Spesifik (Kode Asli Anda) ---
st.header("📋 Rekomendasi Spesifik (Lowongan & Pelatihan)")

# Panggil fungsi rekomendasi (rule-based & semantic)
# Juga simpan di session state agar tidak dipanggil ulang
if 'specific_recommendations' not in st.session_state:
    with st.spinner("Mengambil rekomendasi pekerjaan dan pelatihan..."):
        # --- PERBAIKAN: Kirim semua 4 parameter ---
        jobs, trainings = get_recommendations(
            okupasi_id=st.session_state.mapped_okupasi_id,
            gap_keterampilan=st.session_state.skill_gap,
            profil_teks=st.session_state.profile_text,
            assessment_score=st.session_state.assessment_score
        )
        st.session_state.specific_recommendations = (jobs, trainings)
else:
    jobs, trainings = st.session_state.specific_recommendations


col1, col2 = st.columns(2)

# Kolom 1: Rekomendasi Pekerjaan
with col1:
    st.subheader("Rekomendasi Lowongan Pekerjaan")
    if not jobs:
        st.warning("Belum ada lowongan yang sesuai saat ini.")
    else:
        # Loop dengan aman menggunakan .get() untuk menghindari error jika data kurang
        for job in jobs:
            with st.container(border=True):
                st.markdown(f"**{job.get('Posisi', 'Tanpa Judul')}**")
                st.markdown(f"*{job.get('Perusahaan', 'Rahasia')} - {job.get('Lokasi', 'N/A')}*")
                st.caption(f"Keterampilan: {job.get('Keterampilan_Dibutuhkan', 'N/A')}")
                with st.expander("Lihat Deskripsi"):
                    st.write(job.get('Deskripsi_Pekerjaan', 'Tidak ada deskripsi.'))

# Kolom 2: Rekomendasi Pelatihan (untuk menutup gap)
with col2:
    st.subheader("Rekomendasi Pelatihan (Penutup Skill Gap)")
    st.warning(f"**Skill Gap Anda:** {st.session_state.skill_gap}")
    
    if not trainings:
        st.info("Tidak ada rekomendasi pelatihan spesifik.")
    else:
        for training in trainings:
            st.success(f"**{training}**\n\n*Direkomendasikan untuk menutup gap Anda.*")
