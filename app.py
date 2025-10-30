# app.py
import streamlit as st

st.set_page_config(
    page_title="Digital Talent Pool (DTP) Nasional",
    page_icon="🇮🇩",
    layout="wide"
)

st.title("🇮🇩 Selamat Datang di Digital Talent Pool (DTP) Nasional")

st.markdown("""
Berdasarkan studi kasus **KOMDIGI: DIGITAL TALENT POOL (DTP)**, platform ini adalah
prototipe yang dirancang untuk menjembatani kesenjangan antara talenta digital Indonesia
dengan kebutuhan industri, menggunakan **Peta Okupasi Nasional (PON) TIK** sebagai standar.

Platform ini menggunakan simulasi Kecerdasan Artifisial (AI) untuk:
1.  **Memetakan** profil Anda secara otomatis ke PON TIK.
2.  Memberikan **asesmen** kompetensi yang adaptif.
3.  Menyajikan **rekomendasi** pelatihan dan pekerjaan yang terpersonalisasi.

---

### 🧭 Alur Penggunaan

1.  **👤 Profil Talenta**: Mulai dengan mengisi data dan profil Anda. AI akan langsung memetakan Anda ke okupasi yang paling relevan.
2.  **🧠 Asesmen Kompetensi**: Ambil asesmen berbasis skenario untuk memvalidasi level kompetensi Anda.
3.  **💡 Rekomendasi Karier**: Lihat lowongan kerja dan rekomendasi pelatihan yang dirancang khusus untuk Anda.
4.  **📊 Dashboard Nasional**: (Untuk Publik/Industri) Lihat peta sebaran talenta dan *skill gap* nasional.

**Silakan pilih halaman di sidebar kiri untuk memulai.**
""")

st.info("Ini adalah prototipe. Fungsi AI disimulasikan untuk menunjukkan alur kerja.", icon="ℹ️")

# Inisialisasi session state (untuk menyimpan data antar halaman)
if 'talent_id' not in st.session_state:
    st.session_state.talent_id = None
    st.session_state.mapped_okupasi_id = None
    st.session_state.mapped_okupasi_nama = None
    st.session_state.assessment_score = None
    st.session_state.skill_gap = None