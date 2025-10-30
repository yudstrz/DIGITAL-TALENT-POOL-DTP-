# pages/1_👤_Profil_Talenta.py
import streamlit as st
import pandas as pd
from config import EXCEL_PATH, SHEET_TALENTA, SHEET_HASIL
# --- PERUBAHAN DI SINI ---
from ai_engine import initialize_ai_engine, extract_profile_entities, map_profile_to_pon
# -------------------------
import datetime

st.set_page_config(page_title="Profil Talenta", page_icon="👤", layout="wide")

# --- PERUBAHAN DI SINI: Inisialisasi AI saat halaman dimuat ---
with st.spinner("Memuat AI Engine (Simulasi Vector DB)..."):
    if not st.session_state.get('ai_initialized', False):
        if not initialize_ai_engine():
            st.error("Gagal menginisialisasi AI Engine. Pastikan file Excel dan sheet (terutama PON_TIK_Master) ada dan tidak kosong.")
            st.stop()
        else:
            st.success("AI Engine Siap!")
    
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
    
    submitted = st.form_submit_button("Simpan & Petakan Profil Saya")

if submitted and email and nama and raw_cv:
    with st.spinner("Menyimpan profil dan menjalankan AI Mapping..."):
        try:
            talent_id = email 
            
            # (Logic untuk simpan 'new_talent_data' ke Excel 'SHEET_TALENTA'
            # bisa ditambahkan di sini jika diperlukan)
            
            # --- PERUBAHAN ALUR KERJA DI SINI ---
            
            # TAHAP 1: Ekstraksi Informasi dari CV (NER/LLM)
            st.write("Tahap 1: Mengekstrak entitas dari profil...")
            profile_text_entities = extract_profile_entities(raw_cv)
            
            # TAHAP 2: Pemetaan Awal ke PON TIK (Semantic Search)
            st.write("Tahap 2: Memetakan profil ke PON TIK (Simulasi Semantic Search)...")
            okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(profile_text_entities)
            
            # -----------------------------------
            
            if okupasi_id is None:
                st.error("Gagal memetakan profil. Database PON TIK mungkin kosong atau terjadi error.")
            else:
                # (Logic untuk simpan 'new_hasil_data' ke Excel 'SHEET_HASIL'
                # bisa ditambahkan di sini jika diperlukan)
                
                # 4. Simpan hasil ke session state untuk halaman lain
                st.session_state.talent_id = talent_id
                st.session_state.mapped_okupasi_id = okupasi_id
                st.session_state.mapped_okupasi_nama = okupasi_nama
                st.session_state.skill_gap = gap
                st.session_state.assessment_score = None # Reset skor asesmen
                
                # --- PERUBAHAN DI SINI: Menyimpan profil untuk rekomendasi ---
                st.session_state.profile_text = profile_text_entities
                # -----------------------------------

                st.success(f"Profil Berhasil Dipetakan!")
                st.subheader("Hasil Pemetaan Awal (AI):")
                st.metric(label="Okupasi Paling Sesuai (PON TIK)", value=okupasi_nama)
                st.metric(label="Tingkat Kecocokan Profil", value=f"{skor*100:.2f}%")
                st.warning(f"**Identifikasi Kesenjangan Keterampilan (Simulasi):**\n\n{gap}")
                
                st.info("Langkah selanjutnya: Validasi kompetensi Anda melalui Asesmen di halaman berikutnya. 🧠")
        
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.error("Pastikan file 'data/DTP_Database.xlsx' dan semua sheet ada.")
else:
    if submitted:
        st.warning("Harap isi semua kolom yang bertanda *.")
