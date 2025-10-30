# pages/1_👤_Profil_Talenta.py
import streamlit as st
import pandas as pd
# --- Gunakan config untuk .xlsx ---
from config import EXCEL_PATH, SHEET_TALENTA, SHEET_HASIL
# ---------------------------------
from ai_engine import initialize_ai_engine, extract_profile_entities, map_profile_to_pon
import datetime

st.set_page_config(page_title="Profil Talenta", page_icon="👤", layout="wide")

# --- PERBAIKAN LOGIC: Jangan gunakan st.stop() ---
# Ini memastikan form Anda akan selalu tampil
ai_engine_ready = False
with st.spinner("Memuat AI Engine (Simulasi Vector DB)..."):
    if not st.session_state.get('ai_initialized', False):
        if initialize_ai_engine():
            # st.success("AI Engine Siap!") # Bisa di-uncomment jika perlu
            ai_engine_ready = True
        else:
            st.error("Gagal menginisialisasi AI Engine. Pastikan file 'DTP_Database (2).xlsx' ada di folder 'data/' dan semua sheet (terutama 'PON_TIK_Master' & 'Hasil_Pemetaan_Asesmen') ada dan memiliki header di BARIS KEDUA.")
            ai_engine_ready = False
    else:
        ai_engine_ready = True
# -----------------------------------------------
    
st.title("👤 1. Profil Talenta")
st.markdown("Masukkan data diri dan profil Anda. AI akan menganalisis teks CV Anda untuk dipetakan ke PON TIK.")

email = st.text_input("Email Anda*", help="Email akan digunakan sebagai ID unik Anda.")

with st.form("profil_form"):
    st.subheader("Data Diri")
    nama = st.text_input("Nama Lengkap*")
    lokasi = st.text_input("Lokasi (Kota, Provinsi)", placeholder="Contoh: Jakarta, Bandung, Surabaya, Yogyakarta")
    linkedin = st.text_input("URL Profil LinkedIn")
    
    st.subheader("Profil Profesional")
    raw_cv = st.text_area("Tempelkan (paste) CV atau Deskripsi Diri Anda di Sini*", height=250,
                            help="AI akan mengekstrak pendidikan, pengalaman, dan keterampilan dari teks ini.")
    
    # --- PERBAIKAN: Nonaktifkan tombol jika AI gagal ---
    submit_disabled = not ai_engine_ready
    if submit_disabled:
        st.warning("Tombol 'Simpan' dinonaktifkan karena AI Engine gagal dimuat. Periksa error di atas.")
    # -------------------------------------------------
    
    submitted = st.form_submit_button("Simpan & Petakan Profil Saya", disabled=submit_disabled)

if submitted and email and nama and raw_cv:
    with st.spinner("Menyimpan profil dan menjalankan AI Mapping..."):
        try:
            talent_id = email 
            
            # TAHAP 1: Ekstraksi Informasi dari CV (NER/LLM)
            st.write("Tahap 1: Mengekstrak entitas dari profil...")
            profile_text_entities = extract_profile_entities(raw_cv)
            
            # TAHAP 2: Pemetaan Awal ke PON TIK (Semantic Search)
            st.write("Tahap 2: Memetakan profil ke PON TIK (Simulasi Semantic Search)...")
            okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(profile_text_entities)
            
            if okupasi_id is None:
                st.error("Gagal memetakan profil. Database PON TIK mungkin kosong atau terjadi error.")
            else:
                # TODO: Simpan data ke Excel 'SHEET_HASIL' dan 'SHEET_TALENTA'
                # ... (Logic ini perlu dibuat jika Anda ingin menyimpan data permanen) ...
                
                st.session_state.talent_id = talent_id
                st.session_state.mapped_okupasi_id = okupasi_id
                st.session_state.mapped_okupasi_nama = okupasi_nama
                st.session_state.skill_gap = gap
                st.session_state.assessment_score = None 
                st.session_state.profile_text = profile_text_entities

                st.success(f"Profil Berhasil Dipetakan!")
                st.subheader("Hasil Pemetaan Awal (AI):")
                st.metric(label="Okupasi Paling Sesuai (PON TIK)", value=okupasi_nama)
                st.metric(label="Tingkat Kecocokan Profil", value=f"{skor*100:.2f}%")
                st.warning(f"**Identifikasi Kesenjangan Keterampilan (Simulasi):**\n\n{gap}")
                
                st.info("Langkah selanjutnya: Validasi kompetensi Anda melalui Asesmen di halaman berikutnya. 🧠")
        
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
else:
    if submitted:
        st.warning("Harap isi semua kolom yang bertanda *.")
