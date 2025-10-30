# pages/1_👤_Profil_Talenta.py
import streamlit as st
import pandas as pd
from config import EXCEL_PATH, SHEET_TALENTA, SHEET_HASIL
from ai_engine import map_profile_to_pon
import datetime

st.set_page_config(page_title="Profil Talenta", page_icon="👤", layout="wide")
st.title("👤 1. Profil Talenta")
st.markdown("Masukkan data diri dan profil Anda. AI akan menganalisis teks CV Anda untuk dipetakan ke PON TIK.")

# TODO: Idealnya, buat sistem login. Untuk demo, kita gunakan input nama/email.
email = st.text_input("Email Anda*", help="Email akan digunakan sebagai ID unik Anda.")

with st.form("profil_form"):
    st.subheader("Data Diri")
    nama = st.text_input("Nama Lengkap*")
    lokasi = st.text_input("Lokasi (Kota, Provinsi)")
    linkedin = st.text_input("URL Profil LinkedIn")
    
    st.subheader("Profil Profesional")
    # Teks ini adalah input utama untuk AI (Tahap 1)
    raw_cv = st.text_area("Tempelkan (paste) CV atau Deskripsi Diri Anda di Sini*", height=250,
                            help="AI akan mengekstrak pendidikan, pengalaman, dan keterampilan dari teks ini.")
    
    submitted = st.form_submit_button("Simpan & Petakan Profil Saya")

if submitted and email and nama and raw_cv:
    with st.spinner("Menyimpan profil dan menjalankan AI Mapping (Tahap 1 & 2)..."):
        try:
            # 1. SIMULASI: Simpan data talenta ke Excel
            # TODO: Tambahkan logic untuk update jika email sudah ada
            talent_id = email # Gunakan email sebagai ID unik sementara
            new_talent_data = pd.DataFrame([{
                "TalentID": talent_id,
                "Nama": nama,
                "Email": email,
                "Lokasi": lokasi,
                "LinkedIn_URL": linkedin,
                "Raw_CV_Text": raw_cv
            }])
            
            # (Logic untuk append ke Excel, butuh 'openpyxl')
            # ... (Untuk demo, kita lewati penulisan ke Excel agar sederhana)
            # ... (Kita fokus pada alur AI)
            
            # 2. PANGGIL AI ENGINE: Petakan profil ke PON TIK
            okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(raw_cv)
            
            if okupasi_id is None:
                st.error("Gagal memetakan profil. Database PON TIK mungkin kosong.")
            else:
                # 3. SIMULASI: Simpan hasil pemetaan ke Excel
                new_hasil_data = pd.DataFrame([{
                    "HasilID": f"HASIL-{talent_id}",
                    "TalentID": talent_id,
                    "OkupasiID_Mapped": okupasi_id,
                    "Skor_Kecocokan_Awal": skor,
                    "Gap_Keterampilan": gap,
                    "Tanggal_Update": datetime.datetime.now()
                }])
                # ... (Logic untuk append/update 'SHEET_HASIL' di Excel)
                
                # 4. Simpan hasil ke session state untuk halaman lain
                st.session_state.talent_id = talent_id
                st.session_state.mapped_okupasi_id = okupasi_id
                st.session_state.mapped_okupasi_nama = okupasi_nama
                st.session_state.skill_gap = gap
                st.session_state.assessment_score = None # Reset skor asesmen

                st.success(f"Profil Berhasil Dipetakan!")
                st.subheader("Hasil Pemetaan Awal (AI):")
                st.metric(label="Okupasi Paling Sesuai (PON TIK)", value=okupasi_nama)
                st.metric(label="Tingkat Kecocokan Profil", value=f"{skor*100:.2f}%")
                st.warning(f"**Identifikasi Kesenjangan Keterampilan (Skill Gap):**\n\n{gap}")
                
                st.info("Langkah selanjutnya: Validasi kompetensi Anda melalui Asesmen di halaman berikutnya. 🧠")
        
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.error("Pastikan file 'data/DTP_Database.xlsx' dan sheet 'PON_TIK_Master' ada.")
else:
    st.warning("Harap isi semua kolom yang bertanda *.")