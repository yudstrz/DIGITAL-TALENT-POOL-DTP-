"""
HALAMAN PROFIL TALENTA - ALL IN ONE (FIXED VERSION)
Perbaikan: konsistensi nama sheet dan error handling
"""

import streamlit as st
import pandas as pd
import re
import io
import os
from pypdf import PdfReader
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import EXCEL_PATH, SHEET_PON, SHEET_TALENTA

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="Profil Talenta", 
    page_icon="👤", 
    layout="wide"
)


# ========================================
# FUNGSI 1: LOAD EXCEL
# ========================================
@st.cache_data
def load_excel_sheet(file_path, sheet_name):
    """Membaca sheet dari Excel dengan error handling lengkap"""
    try:
        # Cek apakah file ada
        if not os.path.exists(file_path):
            st.error(f"❌ File tidak ditemukan: '{file_path}'")
            return None
        
        # Baca Excel tanpa header dulu untuk debug
        xls = pd.ExcelFile(file_path)
        available_sheets = xls.sheet_names
        
        # Debug: tampilkan sheet yang tersedia
        with st.expander("🔍 Debug: Sheet tersedia di Excel"):
            st.write(f"📂 File: `{file_path}`")
            st.write(f"📋 Sheet yang dicari: `{sheet_name}`")
            st.write(f"📊 Sheet tersedia:")
            for s in available_sheets:
                st.write(f"  - {s}")
        
        # Cek apakah sheet ada
        if sheet_name not in available_sheets:
            st.error(f"❌ Sheet '{sheet_name}' tidak ditemukan!")
            st.info(f"💡 Sheet tersedia: {', '.join(available_sheets)}")
            return None
        
        # Baca sheet dengan header di baris ke-2 (index 1)
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        df.columns = df.columns.str.strip()
        df = df.fillna('')
        
        st.success(f"✅ Sheet '{sheet_name}' berhasil dimuat ({len(df)} baris)")
        return df
        
    except Exception as e:
        st.error(f"❌ Error memuat sheet '{sheet_name}': {str(e)}")
        import traceback
        with st.expander("🐛 Detail Error"):
            st.code(traceback.format_exc())
        return None


# ========================================
# FUNGSI 2: EKSTRAK FILE
# ========================================
def extract_text_from_pdf(file_io):
    """Ekstrak teks dari PDF"""
    reader = PdfReader(file_io)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file_io):
    """Ekstrak teks dari DOCX"""
    doc = docx.Document(file_io)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


# ========================================
# FUNGSI 3: PARSING CV (AI Sederhana)
# ========================================
def parse_cv_data(cv_text):
    """
    AI sederhana untuk parsing CV menggunakan Regex
    Ekstrak: email, nama, lokasi, LinkedIn
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
        
    # 3. Ekstrak Nama (baris pertama biasanya)
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
# FUNGSI 4: EKSTRAK ENTITAS (NER Sederhana)
# ========================================
def extract_profile_entities(raw_cv: str):
    """
    Named Entity Recognition sederhana
    Ambil kata-kata penting (panjang >= 4 huruf)
    """
    words = set(re.findall(r'\b\w{4,}\b', raw_cv.lower()))
    profile_text = ' '.join(words)
    return profile_text


# ========================================
# FUNGSI 5: INISIALISASI VECTORIZER
# ========================================
@st.cache_resource
def initialize_vectorizer():
    """
    Inisialisasi TF-IDF Vectorizer dan training dengan data PON
    FIXED: Menggunakan SHEET_PON dari config.py
    """
    st.info("⚙️ Inisialisasi AI Vectorizer...")
    
    # PENTING: Gunakan konstanta dari config.py
    df_pon = load_excel_sheet(EXCEL_PATH, SHEET_PON)
    
    if df_pon is None or df_pon.empty:
        st.error("❌ Data PON TIK tidak bisa dimuat atau kosong")
        return None, None, None
    
    # Validasi kolom yang dibutuhkan
    required_cols = ['Okupasi', 'Unit_Kompetensi', 'Kuk_Keywords']
    missing_cols = [col for col in required_cols if col not in df_pon.columns]
    
    if missing_cols:
        st.error(f"❌ Kolom tidak ditemukan: {missing_cols}")
        with st.expander("📋 Kolom tersedia"):
            st.write(list(df_pon.columns))
        return None, None, None
    
    # Gabungkan teks okupasi
    pon_corpus = (
        df_pon['Okupasi'].astype(str) + ' ' + 
        df_pon['Unit_Kompetensi'].astype(str) + ' ' + 
        df_pon['Kuk_Keywords'].astype(str)
    )
    
    # Training vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    pon_vectors = vectorizer.fit_transform(pon_corpus)
    
    st.success(f"✅ Vectorizer siap ({len(df_pon)} okupasi)")
    
    return vectorizer, pon_vectors, df_pon


# ========================================
# FUNGSI 6: MAPPING KE PON TIK
# ========================================
def map_profile_to_pon(profile_text: str):
    """
    Semantic search: cari okupasi PON yang paling cocok
    Menggunakan Cosine Similarity
    """
    # Ambil vectorizer yang sudah di-training
    vectorizer, pon_vectors, df_pon = initialize_vectorizer()
    
    if vectorizer is None:
        return None, None, 0, ""
    
    try:
        # Ubah profil jadi vector
        query_vector = vectorizer.transform([profile_text])
        
        # Hitung similarity dengan semua okupasi
        scores = cosine_similarity(query_vector, pon_vectors)
        
        # Ambil yang paling cocok
        best_match_index = scores.argmax()
        best_score = scores[0, best_match_index]
        
        # Ambil data okupasi
        pon_data = df_pon.iloc[best_match_index]
        okupasi_id = pon_data.get('OkupasiID', 'N/A')
        okupasi_nama = pon_data.get('Okupasi', 'N/A')
        
        # Simulasi skill gap
        gap_keterampilan = "Cloud Computing, CI/CD, Agile"
        
        return okupasi_id, okupasi_nama, best_score, gap_keterampilan
        
    except Exception as e:
        st.error(f"❌ Error mapping: {str(e)}")
        import traceback
        with st.expander("🐛 Detail Error"):
            st.code(traceback.format_exc())
        return None, None, 0, ""


# ========================================
# INISIALISASI SESSION STATE
# ========================================
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
# UI: JUDUL
# ========================================
st.title("👤 1. Profil Talenta")
st.markdown("""
Masukkan data diri dan profil Anda. 
AI akan menganalisis CV Anda dan memetakan ke PON TIK.
""")


# ========================================
# UI: FILE UPLOADER
# ========================================
st.subheader("🤖 Otomatis Isi Data dengan CV")
st.markdown("Unggah CV Anda (PDF/DOCX/TXT), AI akan mengisi form.")

uploaded_file = st.file_uploader(
    "Upload CV", 
    type=["pdf", "docx", "txt"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    with st.spinner("🤖 AI sedang membaca CV..."):
        try:
            # Baca file
            if uploaded_file.type == "application/pdf":
                file_io = io.BytesIO(uploaded_file.getvalue())
                raw_text = extract_text_from_pdf(file_io)
                
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_io = io.BytesIO(uploaded_file.getvalue())
                raw_text = extract_text_from_docx(file_io)
                
            else:  # TXT
                raw_text = uploaded_file.getvalue().decode("utf-8")
            
            # Parse dengan AI
            parsed_data = parse_cv_data(raw_text)
            
            # Update session state
            st.session_state.form_email = parsed_data["email"]
            st.session_state.form_nama = parsed_data["nama"]
            st.session_state.form_lokasi = parsed_data["lokasi"]
            st.session_state.form_linkedin = parsed_data["linkedin"]
            st.session_state.form_cv_text = parsed_data["full_text"]
            
            st.success("✅ CV berhasil diproses!")
            
        except Exception as e:
            st.error(f"❌ Gagal memproses: {e}")

st.markdown("---")


# ========================================
# UI: FORM INPUT
# ========================================
with st.form("profil_form"):
    
    st.subheader("📧 Data Akun")
    email = st.text_input(
        "Email Anda*", 
        value=st.session_state.form_email,
        placeholder="contoh@email.com"
    )

    st.subheader("👤 Data Diri")
    nama = st.text_input(
        "Nama Lengkap*", 
        value=st.session_state.form_nama,
        placeholder="Nama lengkap"
    )
    
    lokasi = st.text_input(
        "Lokasi", 
        value=st.session_state.form_lokasi,
        placeholder="Jakarta, Bandung, dll"
    )
    
    linkedin = st.text_input(
        "LinkedIn", 
        value=st.session_state.form_linkedin,
        placeholder="https://linkedin.com/in/..."
    )
    
    st.subheader("💼 Profil Profesional")
    raw_cv = st.text_area(
        "CV atau Deskripsi Diri*", 
        value=st.session_state.form_cv_text,
        height=250,
        help="AI akan ekstrak skill dari teks ini"
    )
    
    submitted = st.form_submit_button("💾 Simpan & Petakan Profil")


# ========================================
# PROSES FORM
# ========================================
if submitted:
    if not email or not nama or not raw_cv:
        st.warning("⚠️ Email, Nama, dan CV wajib diisi!")
    else:
        # Update session state
        st.session_state.form_email = email
        st.session_state.form_nama = nama
        st.session_state.form_lokasi = lokasi
        st.session_state.form_linkedin = linkedin
        st.session_state.form_cv_text = raw_cv
        
        with st.spinner("🤖 AI sedang memetakan profil..."):
            try:
                talent_id = email
                
                # Ekstrak entitas
                st.write("📝 Mengekstrak entitas...")
                profile_entities = extract_profile_entities(raw_cv)
                
                # Mapping ke PON
                st.write("🎯 Memetakan ke PON TIK...")
                okupasi_id, okupasi_nama, skor, gap = map_profile_to_pon(profile_entities)
                
                if okupasi_id is None:
                    st.error("❌ Gagal mapping. Periksa debug info di atas.")
                else:
                    # Simpan hasil
                    st.session_state.talent_id = talent_id
                    st.session_state.mapped_okupasi_id = okupasi_id
                    st.session_state.mapped_okupasi_nama = okupasi_nama
                    st.session_state.skill_gap = gap
                    st.session_state.profile_text = profile_entities
                    
                    # Tampilkan hasil
                    st.success("✅ Profil Berhasil Dipetakan!")
                    
                    st.subheader("📊 Hasil Pemetaan AI:")
                    col1, col2 = st.columns(2)
                    col1.metric("Okupasi Sesuai", okupasi_nama)
                    col2.metric("Kecocokan", f"{skor*100:.2f}%")
                    
                    st.warning(f"⚠️ **Skill Gap:** {gap}")
                    
                    st.info("""
                    💡 **Next Step:**
                    Lanjut ke **Asesmen Kompetensi** untuk validasi!
                    """)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("🐛 Detail Error"):
                    st.code(traceback.format_exc())
