# pages/1_👤_Profil_Talenta.py
import streamlit as st
import pandas as pd
import re
import io
from pypdf import PdfReader
import docx

from config import EXCEL_PATH, SHEET_TALENTA, SHEET_HASIL
from ai_engine import initialize_ai_engine, extract_profile_entities, map_profile_to_pon
import datetime

st.set_page_config(page_title="Profil Talenta", page_icon="👤", layout="wide")

# --- Fungsi helper untuk ekstraksi teks ---
def extract_text_from_pdf(file_io):
    reader = PdfReader(file_io)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_io):
    doc = docx.Document(file_io)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_cv_data(cv_text):
    """Simulasi AI sederhana untuk mem-parsing data dari teks CV."""
    data = {
        "email": "",
        "nama": "",
        "linkedin": "",
        "lokasi": "",
        "full_text": cv_text
    }
    
    # 1. Ekstrak Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
    if email_match:
        data["email"] = email_match.group(0)
        
    # 2. Ekstrak LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/([\w-]+)', cv_text, re.IGNORECASE)
    if linkedin_match:
        data["linkedin"] = f"https://www.linkedin.com/in/{linkedin_match.group(1)}"
        
    # 3. Ekstrak Nama
    first_line = cv_text.split('\n')[0].strip()
    if first_line and '@' not in first_line and 'linkedin.com' not in first_line and len(first_line.split()) < 5: 
        data["nama"] = first_line.title()
        
    # 4. Lokasi
    lokasi_match = re.search(
        r'(Jakarta|Bandung|Surabaya|Yogyakarta|Jogja|Medan|Semarang|Makassar|Palembang|Denpasar|Depok|Tangerang|Bekasi)', 
        cv_text, 
        re.IGNORECASE
    )
    if lokasi_match:
        lokasi_ditemukan = lokasi_match.group(0).title()
        if lokasi_ditemukan == "Jogja":
            lokasi_ditemukan = "Yogyakarta"
        data["lokasi"] = lokasi_ditemukan
    
    return data


# --- Memuat AI Engine ---
ai_engine_ready = False
with st.spinner("Memuat AI Engine (Simulasi Vector DB)..."):
    if not st.session_state.get('ai_initialized', False):
        if initialize_ai_engine():
            ai_engine_ready = True
        else:
            st.error("Gagal menginisialisasi AI Engine. Pastikan file 'DTP_Database (2).xlsx' ada di folder 'data/' dan semua sheet ada.")
            ai_engine_ready = False
    else:
        ai_engine_ready = True
    
st.title("👤 1. Profil Talenta")
st.markdown("Masukkan data diri dan profil Anda. AI akan menganalisis teks CV Anda untuk dipetakan ke PON TIK.")


# --- Inisialisasi session state untuk form ---
if 'form_email' not in st.session_state:
    st.session_state.form_email = ""
if 'form_nama' not in st.session_state:
    st.session_state.form_nama = ""
if 'form_lokasi' not in st.session_state:
    st.session_state.form_lokasi = ""
if 'form_linkedin' not in st.session_state:
    st.session_state.form_linkedin = ""
if 'form_cv_text' not in st.session_state:
    st.session_state.form_cv_text = ""


# --- File Uploader untuk CV ---
st.subheader("Otomatis Isi Data dengan CV")
st.markdown("Unggah CV Anda (PDF, DOCX, TXT), dan AI akan mencoba mengisi form di bawah ini.")
uploaded_file = st.file_uploader(
    "Upload CV Anda", 
    type=["pdf", "docx", "txt"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    with st.spinner("Memproses CV (Simulasi AI)..."):
        try:
            # Baca file berdasarkan tipenya
            if uploaded_file.type == "application/pdf":
                file_io = io.BytesIO(uploaded_file.getvalue())
                raw_text = extract_text_from_pdf(file_io)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_io = io.BytesIO(uploaded_file.getvalue())
                raw_text = extract_text_from_docx(file_io)
            else:
                raw_text = uploaded_file.getvalue().decode("utf-8")
            
            # Panggil AI parser
            parsed_data = parse_cv_data(raw_text)
            
            # Update session state
            st.session_state.form_email = parsed_data["email"]
            st.session_state.form_nama = parsed_data["nama"]
            st.session_state.form_lokasi = parsed_data["lokasi"]
            st.session_state.form_linkedin = parsed_data["linkedin"]
            st.session_state.form_cv_text = parsed_data["full_text"]
            
            st.success("CV berhasil diproses! Silakan periksa dan lengkapi data di bawah.")
        except Exception as e:
            st.error(f"Gagal memproses file: {e}")

st.markdown("---")

# --- FORM ---
with st.form("profil_form"):
    
    st.subheader("Data Akun")
    # PERBAIKAN: Hapus parameter value, gunakan hanya key
    email = st.text_input(
        "Email Anda*", 
        value=st.session_state.form_email,  # Gunakan value untuk pre-fill
        help="Email akan digunakan sebagai ID unik Anda.",
        placeholder="contoh@email.com"
    )

    st.subheader("Data Diri")
    
    # PERBAIKAN: Gunakan value untuk pre-fill, bukan key
    nama = st.text_input(
        "Nama Lengkap*", 
        value=st.session_state.form_nama,
        placeholder="Masukkan nama lengkap Anda"
    )
    
    lokasi = st.text_input(
        "Lokasi (Kota, Provinsi)", 
        value=st.session_state.form_lokasi,
        placeholder="Contoh: Jakarta, Bandung, Surabaya, Yogyakarta"
    )
    
    linkedin = st.text_input(
        "URL Profil LinkedIn", 
        value=st.session_state.form_linkedin,
        placeholder="https://www.linkedin.com/in/username"
    )
    
    st.subheader("Profil Profesional")
    raw_cv = st.text_area(
        "Tempelkan (paste) CV atau Deskripsi Diri Anda di Sini*", 
        value=st.session_state.form_cv_text,
        height=250,
        help="AI akan mengekstrak pendidikan, pengalaman, dan keterampilan dari teks ini."
    )
    
    submit_disabled = not ai_engine_ready
    if submit_disabled:
        st.warning("Tombol 'Simpan' dinonaktifkan karena AI Engine gagal dimuat. Periksa error di atas.")
    
    submitted = st.form_submit_button("Simpan & Petakan Profil Saya", disabled=submit_disabled)

# --- Logika pemrosesan form ---
if submitted:
    if email and nama and raw_cv:
        # Update session state dengan nilai terbaru dari form
        st.session_state.form_email = email
        st.session_state.form_nama = nama
        st.session_state.form_lokasi = lokasi
        st.session_state.form_linkedin = linkedin
        st.session_state.form_cv_text = raw_cv
        
        with st.spinner("Menyimpan profil dan menjalankan AI Mapping..."):
            try:
                talent_id = email 
                
                # TAHAP 1: Ekstraksi Informasi dari CV
                st.write("Tahap 1: Mengekstrak entitas dari profil...")
                profile_text_entities = extract_profile_entities(raw_cv) 
                
                # TAHAP 2: Pemetaan Awal ke PON TIK
                st.write("Tahap 2: Memetakan profil ke PON TIK (Simulasi Semantic Search)...")
                okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(profile_text_entities)
                
                if okupasi_id is None:
                    st.error("Gagal memetakan profil. Database PON TIK mungkin kosong atau terjadi error.")
                else:
                    # Simpan ke session state
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
        # Validasi
        if not email:
            st.warning("Email tidak boleh kosong.")
        if not nama:
            st.warning("Nama Lengkap tidak boleh kosong.")
        if not raw_cv:
            st.warning("Deskripsi CV tidak boleh kosong.")
