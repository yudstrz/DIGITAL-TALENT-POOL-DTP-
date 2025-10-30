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

# --- PERBAIKAN: Generate soal hanya sekali dan simpan di session state ---
if 'questions' not in st.session_state or st.session_state.questions is None:
    with st.spinner("🤖 AI sedang membuat soal asesmen..."):
        try:
            questions = generate_assessment_questions(st.session_state.mapped_okupasi_id)
            st.session_state.questions = questions  # ✅ Simpan di session state
            st.success(f"✅ Berhasil membuat {len(questions)} soal asesmen!")
        except Exception as e:
            st.error(f"❌ Gagal membuat soal: {e}")
            st.stop()
else:
    questions = st.session_state.questions
    st.success(f"📋 Soal asesmen sudah tersedia ({len(questions)} soal)")

# Simpan jawaban di dictionary
answers = {}

with st.form("assessment_form"):
    for i, q in enumerate(questions):
        st.subheader(f"Pertanyaan {i+1}")
        st.markdown(f"**{q['teks']}**")
        
        if q['tipe'] == 'pilihan_ganda':
            answers[q['id']] = st.radio(
                "Pilih jawaban:", 
                q['opsi'], 
                key=q['id'], 
                label_visibility="collapsed"
            )
        elif q['tipe'] == 'esai_singkat':
            answers[q['id']] = st.text_area(
                "Jawaban Anda:", 
                key=q['id'], 
                label_visibility="collapsed"
            )
    
    submit_assessment = st.form_submit_button("🚀 Kirim Jawaban Asesmen")

if submit_assessment:
    with st.spinner("🔍 Memvalidasi jawaban Anda (Tahap 4)..."):
        try:
            # --- PERBAIKAN: Pass 2 parameters (answers dan questions) ---
            skor, level = validate_assessment(answers, st.session_state.questions)
            
            # Simpan hasil ke session state
            st.session_state.assessment_score = skor
            st.session_state.assessment_level = level
            st.session_state.assessment_date = datetime.datetime.now()
            
            # TODO: Update skor & level ini ke Excel 'SHEET_HASIL'
            # ... (Logic untuk update Excel)
            
            st.success("✅ Asesmen Selesai!")
            st.balloons()
            
            st.subheader("📊 Hasil Validasi Kompetensi:")
            
            col1, col2 = st.columns(2)
            col1.metric("Skor Asesmen", f"{skor} / 100")
            col2.metric("Perkiraan Level", level)
            
            # Tampilkan detail jawaban
            with st.expander("📝 Lihat Detail Jawaban"):
                correct_count = 0
                for q in st.session_state.questions:
                    user_answer = answers.get(q['id'], 'Tidak dijawab')
                    is_correct = user_answer == q['jawaban_benar']
                    
                    if is_correct:
                        correct_count += 1
                        st.success(f"**{q['teks']}**\n\n✅ Benar: {user_answer}")
                    else:
                        st.error(f"**{q['teks']}**\n\n❌ Salah: {user_answer}\n\n✅ Jawaban benar: {q['jawaban_benar']}")
                
                st.info(f"Total benar: {correct_count}/{len(st.session_state.questions)}")
            
            st.info("💡 Langkah selanjutnya: Lihat rekomendasi karier dan pelatihan di halaman berikutnya.")
            
        except Exception as e:
            st.error(f"❌ Error saat validasi asesmen: {e}")
