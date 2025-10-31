"""
HALAMAN REKOMENDASI - CHATBOT VERSION
Chatbot AI untuk analisis profil & rekomendasi karier
"""

import streamlit as st
import json
import random
import requests
from datetime import datetime

from config import (
    EXCEL_PATH, SHEET_LOWONGAN,
    GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL
)

# ========================================
# KONFIGURASI
# ========================================
st.set_page_config(
    page_title="Rekomendasi Karier", 
    page_icon="💡", 
    layout="wide"
)


# ========================================
# CUSTOM CSS - WHATSAPP STYLE CHAT
# ========================================
st.markdown("""
<style>
/* Chat Container */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: linear-gradient(to bottom, #e5ddd5 0%, #e5ddd5 100%);
    border-radius: 10px;
    height: 500px;
    overflow-y: auto;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* User Message Bubble */
.user-bubble {
    background: #dcf8c6;
    color: #000;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    margin-left: auto;
    max-width: 70%;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    position: relative;
    animation: slideInRight 0.3s ease;
}

/* AI Message Bubble */
.ai-bubble {
    background: #fff;
    color: #000;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    margin-right: auto;
    max-width: 70%;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    position: relative;
    animation: slideInLeft 0.3s ease;
}

/* Message Metadata */
.message-time {
    font-size: 0.7em;
    color: #667;
    margin-top: 4px;
    text-align: right;
}

/* Animations */
@keyframes slideInRight {
    from { transform: translateX(50px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideInLeft {
    from { transform: translateX(-50px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Input Area */
.input-container {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}

/* Typing Indicator */
.typing-indicator {
    display: inline-block;
    padding: 10px 15px;
    background: #fff;
    border-radius: 15px;
    margin: 8px 0;
}

.typing-indicator span {
    height: 8px;
    width: 8px;
    background-color: #90949c;
    border-radius: 50%;
    display: inline-block;
    margin: 0 2px;
    animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}
</style>
""", unsafe_allow_html=True)


# ========================================
# INISIALISASI SESSION STATE
# ========================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    # Welcome message dari AI
    st.session_state.chat_history.append({
        "role": "ai",
        "content": "👋 Halo! Saya **Career Assistant AI**.\n\nSaya akan membantu Anda menemukan jalur karier yang tepat! Ceritakan tentang:\n\n✅ Pengalaman kerja Anda\n✅ Skill yang Anda kuasai\n✅ Minat karier Anda\n\nYuk mulai! 🚀",
        "timestamp": datetime.now().strftime("%H:%M")
    })

if 'waiting_response' not in st.session_state:
    st.session_state.waiting_response = False


# ========================================
# FUNGSI: CALL GEMINI API
# ========================================
def call_gemini_api(prompt: str) -> str:
    """Kirim request ke Gemini API"""
    url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 1500
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        content = result['candidates'][0]['content']['parts'][0]['text']
        return content.strip()
        
    except Exception as e:
        return f"❌ Maaf, terjadi kesalahan: {str(e)}"


# ========================================
# FUNGSI: ANALISIS KARIER AI
# ========================================
def get_career_analysis(user_message: str, chat_history: list) -> str:
    """Generate response dari AI berdasarkan context chat"""
    
    # Build context dari chat history
    context = "\n".join([
        f"{'User' if msg['role']=='user' else 'AI'}: {msg['content']}" 
        for msg in chat_history[-5:]  # Ambil 5 pesan terakhir
    ])
    
    prompt = f"""Anda adalah Career Coach AI yang ramah dan profesional untuk bidang Teknologi Informasi dan Komunikasi (TIK).

=== CONTEXT PERCAKAPAN ===
{context}

=== PESAN USER TERBARU ===
{user_message}

=== INSTRUKSI ===
1. Jawab dengan ramah dan supportif seperti chat WhatsApp
2. Gunakan emoji yang sesuai (jangan berlebihan)
3. Berikan analisis spesifik tentang karier TIK
4. Jika user cerita pengalaman: identifikasi skill & okupasi yang cocok
5. Jika user tanya pelatihan: rekomendasikan kursus/sertifikasi
6. Jika user tanya lowongan: rekomendasikan jenis pekerjaan yang sesuai
7. Maksimal 4-5 kalimat, singkat dan padat
8. Gunakan bahasa Indonesia informal tapi profesional

Jawab sekarang:"""

    return call_gemini_api(prompt)


# ========================================
# FUNGSI: RENDER CHAT BUBBLE
# ========================================
def render_chat_bubble(message: dict):
    """Render chat bubble berdasarkan role"""
    if message['role'] == 'user':
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="user-bubble">
                {message['content']}
                <div class="message-time">{message['timestamp']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start;">
            <div class="ai-bubble">
                <strong>🤖 Career AI</strong><br>
                {message['content'].replace('\n', '<br>')}
                <div class="message-time">{message['timestamp']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ========================================
# FUNGSI: REKOMENDASI PEKERJAAN & PELATIHAN
# ========================================
def get_recommendations(okupasi_id, skill_gap, profil_teks):
    """Return: (jobs, trainings)"""
    job_samples = [
        {
            "Posisi": "Data Analyst",
            "Perusahaan": "Tech Innovate",
            "Lokasi": "Jakarta",
            "Keterampilan_Dibutuhkan": "Python, SQL, Power BI",
            "Deskripsi_Pekerjaan": "Menganalisis data untuk mendukung keputusan bisnis."
        },
        {
            "Posisi": "Machine Learning Engineer",
            "Perusahaan": "AI Labs",
            "Lokasi": "Bandung",
            "Keterampilan_Dibutuhkan": "Python, TensorFlow, AWS",
            "Deskripsi_Pekerjaan": "Membangun model AI untuk produksi."
        },
        {
            "Posisi": "DevOps Engineer",
            "Perusahaan": "CloudTech",
            "Lokasi": "Jakarta",
            "Keterampilan_Dibutuhkan": "Docker, Kubernetes, CI/CD",
            "Deskripsi_Pekerjaan": "Mengelola infrastruktur cloud dan automation."
        }
    ]

    training_samples = [
        "Pelatihan Cloud Computing (AWS/GCP Fundamentals)",
        "Kursus CI/CD Pipelines untuk DevOps",
        "Workshop Manajemen Proyek Agile",
        "Bootcamp Machine Learning Intermediate",
        "Sertifikasi Data Engineering Professional"
    ]

    jobs = random.sample(job_samples, k=min(2, len(job_samples)))
    trainings = random.sample(training_samples, k=min(3, len(training_samples)))

    return jobs, trainings


# ========================================
# UI: JUDUL
# ========================================
st.title("💡 3. Career Assistant AI")
st.markdown("""
💬 **Konsultasi Karier dengan AI** - Seperti chat dengan career coach profesional!
""")


# ========================================
# UI: CHATBOT INTERFACE
# ========================================
st.markdown("### 🤖 Chat dengan Career AI")

# Container untuk chat
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Render semua chat history
    for message in st.session_state.chat_history:
        render_chat_bubble(message)
    
    # Typing indicator jika waiting
    if st.session_state.waiting_response:
        st.markdown("""
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ========================================
# UI: INPUT CHAT
# ========================================
st.markdown("---")

col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "Ketik pesan...",
        key="user_message",
        placeholder="Contoh: Saya berpengalaman Python 2 tahun, cocok jadi apa ya?",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 Kirim", use_container_width=True)


# ========================================
# PROSES CHAT
# ========================================
if send_button and user_input.strip():
    # Tambahkan pesan user
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Set waiting state
    st.session_state.waiting_response = True
    
    # Get AI response
    with st.spinner(""):
        ai_response = get_career_analysis(
            user_input, 
            st.session_state.chat_history
        )
    
    # Tambahkan response AI
    st.session_state.chat_history.append({
        "role": "ai",
        "content": ai_response,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Reset waiting
    st.session_state.waiting_response = False
    
    # Simpan profil ke session
    st.session_state['profil_teks'] = user_input
    
    # Rerun untuk update chat
    st.rerun()


# ========================================
# QUICK ACTION BUTTONS
# ========================================
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💼 Rekomendasi Lowongan"):
        quick_msg = "Bisa rekomendasikan lowongan kerja yang cocok untuk saya?"
        st.session_state.chat_history.append({
            "role": "user",
            "content": quick_msg,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        st.rerun()

with col2:
    if st.button("📚 Rekomendasi Pelatihan"):
        quick_msg = "Pelatihan apa yang sebaiknya saya ikuti?"
        st.session_state.chat_history.append({
            "role": "user",
            "content": quick_msg,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        st.rerun()

with col3:
    if st.button("🔄 Reset Chat"):
        st.session_state.chat_history = [{
            "role": "ai",
            "content": "👋 Halo! Saya **Career Assistant AI**.\n\nSaya akan membantu Anda menemukan jalur karier yang tepat! Ceritakan tentang:\n\n✅ Pengalaman kerja Anda\n✅ Skill yang Anda kuasai\n✅ Minat karier Anda\n\nYuk mulai! 🚀",
            "timestamp": datetime.now().strftime("%H:%M")
        }]
        st.rerun()


st.divider()


# ========================================
# VALIDASI ASESMEN (Optional)
# ========================================
if 'assessment_score' in st.session_state and 'mapped_okupasi_id' in st.session_state:
    
    st.markdown("### 👤 Profil Anda")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Talent ID", 
        st.session_state.get('talent_id', '-')
    )
    col2.metric(
        "Okupasi", 
        st.session_state.get('mapped_okupasi_nama', '-')
    )
    col3.metric(
        "Skor", 
        f"{st.session_state.assessment_score}/100"
    )
    
    st.divider()
    
    # ========================================
    # REKOMENDASI DETAIL
    # ========================================
    if st.button("🎯 Lihat Rekomendasi Detail"):
        with st.spinner("🤖 AI sedang memproses rekomendasi..."):
            try:
                jobs, trainings = get_recommendations(
                    st.session_state.get('mapped_okupasi_id', ''),
                    st.session_state.get('skill_gap', []),
                    st.session_state.get('profil_teks', '')
                )
            except Exception as e:
                st.error(f"❌ Gagal ambil rekomendasi: {e}")
                jobs, trainings = [], []
        
        # Layout 2 kolom
        col1, col2 = st.columns(2)
        
        # Kolom 1: Pekerjaan
        with col1:
            st.markdown("## 💼 Rekomendasi Lowongan")
            
            if not jobs:
                st.info("Belum ada lowongan yang sesuai.")
            else:
                for job in jobs:
                    with st.container():
                        st.markdown(f"### 🧩 {job['Posisi']}")
                        st.caption(f"🏢 {job['Perusahaan']} — 📍 {job['Lokasi']}")
                        st.markdown(f"**Skill:** {job['Keterampilan_Dibutuhkan']}")
                        
                        with st.expander("📘 Deskripsi"):
                            st.write(job['Deskripsi_Pekerjaan'])
                            
                        st.markdown("---")
        
        # Kolom 2: Pelatihan
        with col2:
            st.markdown("## 🎯 Rekomendasi Pelatihan")
            st.markdown(f"""
            **Skill Gap Anda:** 
            `{st.session_state.get('skill_gap', '-')}`
            """)
            
            if not trainings:
                st.info("Belum ada rekomendasi pelatihan.")
            else:
                for training in trainings:
                    st.success(f"📚 {training}")
