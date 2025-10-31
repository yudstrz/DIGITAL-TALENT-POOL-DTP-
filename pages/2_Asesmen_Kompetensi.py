# pages/2_🧠_Asesmen_Kompetensi.py
"""
HALAMAN 2: ASESMEN KOMPETENSI

ANALOGI: Ini adalah RUANG UJIAN.
User mengerjakan soal yang dibuat AI untuk validasi kompetensi.

ALUR:
1. Cek apakah user sudah input profil (session state)
2. Tampilkan okupasi hasil mapping
3. Generate soal dengan AI Gemini (hanya sekali)
4. User jawab soal
5. Klik "Kirim" → AI menilai jawaban
6. Tampilkan skor dan level kompetensi
"""

import streamlit as st
from ai_engine import generate_assessment_questions, validate_assessment
import datetime

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="Asesmen Kompetensi", 
    page_icon="🧠", 
    layout="wide"
)


# ========================================
# VALIDASI USER SUDAH INPUT PROFIL
# ========================================
"""
PENTING: User HARUS isi profil dulu sebelum bisa asesmen.
Seperti tidak bisa ikut ujian kalau belum daftar.
"""

st.title("🧠 2. Asesmen Kompetensi")

if not st.session_state.get('talent_id'):
    st.error("""
    ❌ Anda harus mengisi **'Profil Talenta'** terlebih dahulu 
    sebelum mengambil asesmen.
    """)
    st.stop()  # Hentikan eksekusi halaman


# ========================================
# INFO TALENTA
# ========================================

st.info(f"👤 Login sebagai: **{st.session_state.talent_id}**")
st.header(f"📝 Asesmen untuk: {st.session_state.mapped_okupasi_nama}")
st.markdown("""
AI telah menghasilkan soal-soal asesmen berdasarkan okupasi Anda.
Kerjakan dengan teliti untuk validasi kompetensi.
""")


# ========================================
# GENERATE SOAL (HANYA SEKALI)
# ========================================
"""
PENTING: Soal hanya di-generate SEKALI dan disimpan di session state.
Jika user refresh halaman, soal tetap sama (tidak berubah).

Mengapa? Agar:
1. Tidak boros API call (hemat biaya)
2. Konsisten (soal tidak berubah-ubah)
3. User bisa review jawaban nanti
"""

if 'questions' not in st.session_state or st.session_state.questions is None:
    with st.spinner("🤖 AI sedang membuat soal asesmen..."):
        try:
            questions = generate_assessment_questions(
                st.session_state.mapped_okupasi_id
            )
            
            # ✅ SIMPAN DI SESSION STATE
            st.session_state.questions = questions
            st.success(f"✅ Berhasil membuat {len(questions)} soal!")
            
        except Exception as e:
            st.error(f"❌ Gagal membuat soal: {e}")
            st.stop()
else:
    # Soal sudah ada, ambil dari session state
    questions = st.session_state.questions
    st.success(f"📋 Soal sudah tersedia ({len(questions)} soal)")


# ========================================
# FORM ASESMEN
# ========================================
"""
Dictionary 'answers' akan menyimpan jawaban user.
Format: {question_id: selected_answer}
Contoh: {"q1": "Opsi A", "q2": "Opsi C"}
"""

answers = {}

with st.form("assessment_form"):
    
    # Loop untuk setiap soal
    for i, q in enumerate(questions):
        st.subheader(f"❓ Pertanyaan {i+1}")
        st.markdown(f"**{q['teks']}**")
        
        if q['tipe'] == 'pilihan_ganda':
            # Radio button untuk pilihan ganda
            answers[q['id']] = st.radio(
                "Pilih jawaban:", 
                q['opsi'], 
                key=q['id'],  # Unique key untuk setiap radio
                label_visibility="collapsed"
            )
            
        elif q['tipe'] == 'esai_singkat':
            # Text area untuk esai
            answers[q['id']] = st.text_area(
                "Jawaban Anda:", 
                key=q['id'], 
                label_visibility="collapsed"
            )
    
    # Tombol submit
    submit_assessment = st.form_submit_button("🚀 Kirim Jawaban Asesmen")


# ========================================
# PROSES SUBMISSION
# ========================================

if submit_assessment:
    with st.spinner("🔍 AI sedang menilai jawaban Anda..."):
        try:
            # Validasi jawaban
            skor, level = validate_assessment(
                answers, 
                st.session_state.questions
            )
            
            # Simpan hasil ke session state
            st.session_state.assessment_score = skor
            st.session_state.assessment_level = level
            st.session_state.assessment_date = datetime.datetime.now()
            
            # TODO: Simpan ke Excel SHEET_HASIL
            # (Implementasi nanti jika perlu persistence)
            
            # Tampilkan hasil
            st.success("✅ Asesmen Selesai!")
            st.balloons()
            
            st.subheader("📊 Hasil Validasi Kompetensi:")
            
            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("Skor Asesmen", f"{skor} / 100")
            col2.metric("Level Kompetensi", level)
            
            # Detail jawaban (expandable)
            with st.expander("📝 Lihat Detail Jawaban"):
                correct_count = 0
                
                for q in st.session_state.questions:
                    user_answer = answers.get(q['id'], 'Tidak dijawab')
                    is_correct = user_answer == q['jawaban_benar']
                    
                    if is_correct:
                        correct_count += 1
                        st.success(f"""
                        **{q['teks']}**
                        
                        ✅ Benar: {user_answer}
                        """)
                    else:
                        st.error(f"""
                        **{q['teks']}**
                        
                        ❌ Jawaban Anda: {user_answer}
                        
                        ✅ Jawaban Benar: {q['jawaban_benar']}
                        """)
                
                st.info(f"""
                📊 **Ringkasan:**
                Total benar: {correct_count}/{len(st.session_state.questions)}
                """)
            
            # Instruksi next step
            st.info("""
            💡 **Langkah Selanjutnya:**
            Lihat rekomendasi karier dan pelatihan di halaman berikutnya!
            """)
            
        except Exception as e:
            st.error(f"❌ Error saat validasi: {e}")
