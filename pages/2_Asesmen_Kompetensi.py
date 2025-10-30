# pages/2_🧠_Asesmen_Kompetensi.py
import streamlit as st
from ai_engine import generate_assessment_questions, validate_assessment
import datetime

st.set_page_config(page_title="Asesmen Kompetensi", page_icon="🧠", layout="wide")
st.title("🧠 2. Asesmen Kompetensi")

# Cek apakah pengguna sudah input profil
if not st.session_state.get('talent_id'):
    st.error("Anda harus mengisi 'Profil Talenta' terlebih dahulu sebelum mengambil asesmen.")
    st.stop()

# Tampilkan info talenta dan okupasi hasil mapping
st.info(f"Anda login sebagai: **{st.session_state.talent_id}**")
st.header(f"Asesmen untuk Okupasi: {st.session_state.mapped_okupasi_nama}")
st.markdown("AI telah menghasilkan soal-soal asesmen (Tahap 3) berdasarkan okupasi Anda.")

# Panggil AI Engine untuk membuat soal
with st.spinner("Membuat soal asesmen (Simulasi AQG)..."):
    questions = generate_assessment_questions(st.session_state.mapped_okupasi_id)

# Simpan jawaban di dictionary
answers = {}

with st.form("assessment_form"):
    for i, q in enumerate(questions):
        st.subheader(f"Pertanyaan {i+1}: {q['teks']}")
        if q['tipe'] == 'pilihan_ganda':
            answers[q['id']] = st.radio("Pilih jawaban:", q['opsi'], key=q['id'], label_visibility="collapsed")
        elif q['tipe'] == 'esai_singkat':
            answers[q['id']] = st.text_area("Jawaban Anda:", key=q['id'])
    
    submit_assessment = st.form_submit_button("Kirim Jawaban Asesmen")

if submit_assessment:
    with st.spinner("Memvalidasi jawaban Anda (Tahap 4)..."):
        # Panggil AI Engine untuk validasi
        skor, level = validate_assessment(answers)
        
        # Simpan hasil ke session state
        st.session_state.assessment_score = skor
        
        # TODO: Update skor & level ini ke Excel 'SHEET_HASIL'
        # ... (Logic untuk update Excel)
        
        st.success("Asesmen Selesai!")
        st.subheader("Hasil Validasi Kompetensi:")
        
        col1, col2 = st.columns(2)
        col1.metric("Skor Asesmen", f"{skor} / 100")
        col2.metric("Perkiraan Level", level)
        
        st.info("Langkah selanjutnya: Lihat rekomendasi karier dan pelatihan di halaman berikutnya. 💡")
