# pages/1_👤_Profil_Talenta.py
import streamlit as st
import pandas as pd
import re # --- TAMBAHAN: Untuk Regex (Simulasi AI) ---
import io # --- TAMBAHAN: Untuk membaca file ---
from pypdf import PdfReader # --- TAMBAHAN: Untuk membaca PDF ---
import docx # --- TAMBAHAN: Untuk membaca DOCX ---

# --- Gunakan config untuk .xlsx ---
from config import EXCEL_PATH, SHEET_TALENTA, SHEET_HASIL
# ---------------------------------
from ai_engine import initialize_ai_engine, extract_profile_entities, map_profile_to_pon
import datetime

st.set_page_config(page_title="Profil Talenta", page_icon="👤", layout="wide")

# --- TAMBAHAN: Fungsi helper untuk ekstraksi teks ---
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
    
    # 1. Ekstrak Email (Regex)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
    if email_match:
        data["email"] = email_match.group(0)
        
    # 2. Ekstrak LinkedIn (Regex)
    linkedin_match = re.search(r'linkedin\.com/in/([\w-]+)', cv_text, re.IGNORECASE)
    if linkedin_match:
        data["linkedin"] = f"https://www.linkedin.com/in/{linkedin_match.group(1)}"
        
    # 3. Ekstrak Nama (Heuristik sederhana: ambil baris pertama)
    first_line = cv_text.split('\n')[0].strip()
    # Hindari mengambil email sebagai nama jika itu baris pertama
    if first_line and '@' not in first_line and 'linkedin.com' not in first_line and len(first_line.split()) < 5: # Asumsi nama tidak terlalu panjang
        data["nama"] = first_line.title()
        
    # --- PERBAIKAN: Menambahkan parser lokasi sederhana ---
    # 4. Lokasi (Simulasi Regex sederhana)
    # Cari kota-kota besar di Indonesia
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
    # --- AKHIR PERBAIKAN ---
    
    return data
# --- AKHIR TAMBAHAN ---


# --- Memuat AI Engine (Semantic Search) ---
ai_engine_ready = False
with st.spinner("Memuat AI Engine (Simulasi Vector DB)..."):
    if not st.session_state.get('ai_initialized', False):
        if initialize_ai_engine():
            ai_engine_ready = True
        else:
            st.error("Gagal menginisialisasi AI Engine. Pastikan file 'DTP_Database (2).xlsx' ada di folder 'data/' dan semua sheet (terutama 'PON_TIK_Master' & 'Hasil_Pemetaan_Asesmen') ada dan memiliki header di BARIS KEDUA.")
            ai_engine_ready = False
    else:
        ai_engine_ready = True
    
st.title("👤 1. Profil Talenta")
st.markdown("Masukkan data diri dan profil Anda. AI akan menganalisis teks CV Anda untuk dipetakan ke PON TIK.")


# --- MODIFIKASI: Inisialisasi session state untuk form ---
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
# --- AKHIR MODIFIKASI ---


# --- TAMBAHAN: File Uploader untuk CV ---
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
            else: # .txt
                raw_text = uploaded_file.getvalue().decode("utf-8")
            
            # Panggil "AI" parser
            parsed_data = parse_cv_data(raw_text)
            
            # --- PERBAIKAN: Lengkapi update session state ---
            st.session_state.form_email = parsed_data["email"]
            st.session_state.form_nama = parsed_data["nama"]
            st.session_state.form_lokasi = parsed_data["lokasi"] # <-- INI YANG KURANG
            st.session_state.form_linkedin = parsed_data["linkedin"]
            st.session_state.form_cv_text = parsed_data["full_text"]
            # --- AKHIR PERBAIKAN ---
            
            st.success("CV berhasil diproses! Silakan periksa dan lengkapi data di bawah.")
        except Exception as e:
            st.error(f"Gagal memproses file: {e}")
# --- AKHIR TAMBAHAN ---

st.markdown("---")
email_input_disabled = bool(st.session_state.form_email) # Kunci email jika sudah terisi
email = st.text_input(
    "Email Anda*", 
    help="Email akan digunakan sebagai ID unik Anda.",
    key='form_email', # MODIFIKASI: Gunakan key
    disabled=email_input_disabled
)
if email_input_disabled:
    st.caption("Email Anda (yang diekstrak dari CV) digunakan sebagai ID unik dan tidak dapat diubah.")


with st.form("profil_form"):
    st.subheader("Data Diri")
    
    # --- MODIFIKASI: Hubungkan field ke session state ---
    # Widget ini TIDAK di-disable, sehingga bisa diedit.
    nama = st.text_input("Nama Lengkap*", key='form_nama')
    lokasi = st.text_input("Lokasi (Kota, Provinsi)", placeholder="Contoh: Jakarta, Bandung, Surabaya, Yogyakarta", key='form_lokasi')
    linkedin = st.text_input("URL Profil LinkedIn", key='form_linkedin')
    
    st.subheader("Profil Profesional")
    raw_cv = st.text_area("Tempelkan (paste) CV atau Deskripsi Diri Anda di Sini*", height=250,
                            help="AI akan mengekstrak pendidikan, pengalaman, dan keterampilan dari teks ini.",
                            key='form_cv_text')
    # --- AKHIR MODIFIKASI ---
    
    submit_disabled = not ai_engine_ready
    if submit_disabled:
        st.warning("Tombol 'Simpan' dinaktifkan karena AI Engine gagal dimuat. Periksa error di atas.")
    
    submitted = st.form_submit_button("Simpan & Petakan Profil Saya", disabled=submit_disabled)

# --- MODIFIKASI: Baca data dari session state saat submit ---
if submitted and st.session_state.form_email and st.session_state.form_nama and st.session_state.form_cv_text:
    
    # --- PERBAIKAN: Ambil SEMUA data yang sudah diedit pengguna ---
    email = st.session_state.form_email
    nama = st.session_state.form_nama
    lokasi = st.session_state.form_lokasi       # <-- TAMBAHAN
    linkedin = st.session_state.form_linkedin # <-- TAMBAHAN
    raw_cv_text = st.session_state.form_cv_text
    # --- AKHIR PERBAIKAN ---
    
    with st.spinner("Menyimpan profil dan menjalankan AI Mapping..."):
        try:
            talent_id = email 
            
            # TAHAP 1: Ekstraksi Informasi dari CV (NER/LLM)
            st.write("Tahap 1: Mengekstrak entitas dari profil...")
            # Gunakan fungsi ai_engine Anda yang asli
            profile_text_entities = extract_profile_entities(raw_cv_text) 
            
            # TAHAP 2: Pemetaan Awal ke PON TIK (Semantic Search)
            st.write("Tahap 2: Memetakan profil ke PON TIK (Simulasi Semantic Search)...")
            okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(profile_text_entities)
            
            if okupasi_id is None:
                st.error("Gagal memetakan profil. Database PON TIK mungkin kosong atau terjadi error.")
            else:
                # TODO: Simpan data ke Excel (termasuk 'lokasi' dan 'linkedin')
                # ... 
                
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
        # --- MODIFIKASI: Sesuaikan pesan error ---
        if not st.session_state.form_email:
            st.warning("Email tidak boleh kosong.")
        elif not st.session_state.form_nama:
            st.warning("Nama Lengkap tidak boleh kosong.")
        elif not st.session_state.form_cv_text:
            st.warning("Deskripsi CV tidak boleh kosong.")
        # --- AKHIR MODIFIKASI ---
