# pages/1_👤_Profil_Talenta.py
"""
HALAMAN 1: INPUT PROFIL TALENTA

ANALOGI: Ini adalah PINTU MASUK sistem.
User mengisi formulir dan upload CV seperti mendaftar pekerjaan.

ALUR:
1. User upload CV (PDF/DOCX/TXT)
2. AI membaca CV dan otomatis isi form
3. User melengkapi data yang kurang
4. Klik "Simpan" → AI memetakan ke okupasi PON TIK
5. Hasil mapping ditampilkan
"""

import streamlit as st
import pandas as pd
import re
import io
from pypdf import PdfReader
import docx

from config import EXCEL_PATH, SHEET_TALENTA, SHEET_HASIL
from ai_engine import initialize_ai_engine, extract_profile_entities, map_profile_to_pon

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="Profil Talenta", 
    page_icon="👤", 
    layout="wide"
)


# ========================================
# FUNGSI EKSTRAKSI FILE
# ========================================

def extract_text_from_pdf(file_io):
    """Baca teks dari file PDF"""
    reader = PdfReader(file_io)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file_io):
    """Baca teks dari file DOCX"""
    doc = docx.Document(file_io)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def parse_cv_data(cv_text):
    """
    FUNGSI: AI sederhana untuk parsing CV
    
    ANALOGI: Seperti membaca CV dan mencatat info penting:
    - Email
    - Nama (baris pertama biasanya)
    - LinkedIn URL
    - Lokasi (kota yang disebutkan)
    
    TEKNIS: Menggunakan Regex (pattern matching)
    """
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
    linkedin_match = re.search(
        r'linkedin\.com/in/([\w-]+)', 
        cv_text, 
        re.IGNORECASE
    )
    if linkedin_match:
        data["linkedin"] = f"https://www.linkedin.com/in/{linkedin_match.group(1)}"
        
    # 3. Ekstrak Nama (baris pertama biasanya nama)
    first_line = cv_text.split('\n')[0].strip()
    if first_line and '@' not in first_line and len(first_line.split()) < 5: 
        data["nama"] = first_line.title()
        
    # 4. Ekstrak Lokasi
    lokasi_match = re.search(
        r'(Jakarta|Bandung|Surabaya|Yogyakarta|Jogja|Medan|Semarang|Makassar)', 
        cv_text, 
        re.IGNORECASE
    )
    if lokasi_match:
        lokasi = lokasi_match.group(0).title()
        if lokasi == "Jogja":
            lokasi = "Yogyakarta"
        data["lokasi"] = lokasi
    
    return data


# ========================================
# INISIALISASI AI ENGINE
# ========================================
"""
PENTING: AI Engine harus diinisialisasi dulu sebelum bisa dipakai.
Seperti menyalakan mesin mobil sebelum jalan.
"""

ai_engine_ready = False
with st.spinner("Memuat AI Engine (Vector DB)..."):
    if not st.session_state.get('ai_initialized', False):
        if initialize_ai_engine():
            ai_engine_ready = True
        else:
            st.error("""
            ❌ Gagal menginisialisasi AI Engine. 
            Pastikan file 'DTP_Database (2).xlsx' ada di folder 'data/'
            """)
            ai_engine_ready = False
    else:
        ai_engine_ready = True


# ========================================
# JUDUL HALAMAN
# ========================================

st.title("👤 1. Profil Talenta")
st.markdown("""
Masukkan data diri dan profil Anda. 
AI akan menganalisis CV Anda dan memetakan ke PON TIK.
""")


# ========================================
# INISIALISASI SESSION STATE
# ========================================
"""
Session State = memori sementara untuk menyimpan data user.
Seperti clipboard yang bisa diakses di semua halaman.
"""

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


# ========================================
# FILE UPLOADER CV
# ========================================

st.subheader("🤖 Otomatis Isi Data dengan CV")
st.markdown("Unggah CV Anda (PDF/DOCX/TXT), AI akan mengisi form di bawah.")

uploaded_file = st.file_uploader(
    "Upload CV Anda", 
    type=["pdf", "docx", "txt"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    with st.spinner("Memproses CV dengan AI..."):
        try:
            # Baca file berdasarkan tipe
            if uploaded_file.type == "application/pdf":
                file_io = io.BytesIO(uploaded_file.getvalue())
                raw_text = extract_text_from_pdf(file_io)
                
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_io = io.BytesIO(uploaded_file.getvalue())
                raw_text = extract_text_from_docx(file_io)
                
            else:  # TXT
                raw_text = uploaded_file.getvalue().decode("utf-8")
            
            # Panggil AI parser
            parsed_data = parse_cv_data(raw_text)
            
            # Update session state
            st.session_state.form_email = parsed_data["email"]
            st.session_state.form_nama = parsed_data["nama"]
            st.session_state.form_lokasi = parsed_data["lokasi"]
            st.session_state.form_linkedin = parsed_data["linkedin"]
            st.session_state.form_cv_text = parsed_data["full_text"]
            
            st.success("✅ CV berhasil diproses! Periksa data di bawah.")
            
        except Exception as e:
            st.error(f"❌ Gagal memproses file: {e}")

st.markdown("---")


# ========================================
# FORM INPUT PROFIL
# ========================================

with st.form("profil_form"):
    
    st.subheader("📧 Data Akun")
    email = st.text_input(
        "Email Anda*", 
        value=st.session_state.form_email,
        help="Email akan digunakan sebagai ID unik Anda",
        placeholder="contoh@email.com"
    )

    st.subheader("👤 Data Diri")
    
    nama = st.text_input(
        "Nama Lengkap*", 
        value=st.session_state.form_nama,
        placeholder="Masukkan nama lengkap"
    )
    
    lokasi = st.text_input(
        "Lokasi (Kota, Provinsi)", 
        value=st.session_state.form_lokasi,
        placeholder="Contoh: Jakarta, Bandung, Surabaya"
    )
    
    linkedin = st.text_input(
        "URL Profil LinkedIn", 
        value=st.session_state.form_linkedin,
        placeholder="https://www.linkedin.com/in/username"
    )
    
    st.subheader("💼 Profil Profesional")
    raw_cv = st.text_area(
        "Tempelkan CV atau Deskripsi Diri*", 
        value=st.session_state.form_cv_text,
        height=250,
        help="AI akan ekstrak pendidikan, pengalaman, keterampilan"
    )
    
    # Disable tombol jika AI Engine gagal
    submit_disabled = not ai_engine_ready
    if submit_disabled:
        st.warning("⚠️ Tombol disabled karena AI Engine gagal dimuat")
    
    submitted = st.form_submit_button(
        "💾 Simpan & Petakan Profil Saya", 
        disabled=submit_disabled
    )


# ========================================
# PROSES FORM SUBMISSION
# ========================================

if submitted:
    # Validasi input wajib
    if not email or not nama or not raw_cv:
        st.warning("⚠️ Email, Nama, dan CV wajib diisi!")
        
    else:
        # Update session state
        st.session_state.form_email = email
        st.session_state.form_nama = nama
        st.session_state.form_lokasi = lokasi
        st.session_state.form_linkedin = linkedin
        st.session_state.form_cv_text = raw_cv
        
        with st.spinner("🤖 AI sedang memetakan profil Anda..."):
            try:
                talent_id = email  # Email sebagai unique ID
                
                # TAHAP 1: Ekstraksi entitas dari CV
                st.write("📝 Tahap 1: Mengekstrak entitas dari CV...")
                profile_text_entities = extract_profile_entities(raw_cv)
                
                # TAHAP 2: Mapping ke PON TIK
                st.write("🎯 Tahap 2: Memetakan ke PON TIK...")
                okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(
                    profile_text_entities
                )
                
                if okupasi_id is None:
                    st.error("❌ Gagal memetakan profil. Database PON TIK kosong.")
                    
                else:
                    # Simpan ke session state
                    st.session_state.talent_id = talent_id
                    st.session_state.mapped_okupasi_id = okupasi_id
                    st.session_state.mapped_okupasi_nama = okupasi_nama
                    st.session_state.skill_gap = gap
                    st.session_state.assessment_score = None
                    st.session_state.profile_text = profile_text_entities

                    # Tampilkan hasil
                    st.success("✅ Profil Berhasil Dipetakan!")
                    
                    st.subheader("📊 Hasil Pemetaan AI:")
                    
                    col1, col2 = st.columns(2)
                    col1.metric(
                        "Okupasi Paling Sesuai", 
                        okupasi_nama
                    )
                    col2.metric(
                        "Tingkat Kecocokan", 
                        f"{skor*100:.2f}%"
                    )
                    
                    st.warning(f"""
                    **⚠️ Identifikasi Kesenjangan Keterampilan:**
                    
                    {gap}
                    """)
                    
                    st.info("""
                    💡 **Langkah Selanjutnya:**
                    Validasi kompetensi Anda melalui Asesmen di halaman berikutnya!
                    """)
            
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
