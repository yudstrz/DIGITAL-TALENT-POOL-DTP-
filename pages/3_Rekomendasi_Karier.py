# HALAMAN REKOMENDASI - CHATBOT VERSION (Fixed)
# Chatbot AI untuk analisis profil & rekomendasi karier

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
    page_title="Career Assistant AI", 
    page_icon="💡", 
    layout="wide"
)


# ========================================
# CUSTOM CSS - MODERN CHAT UI
# ========================================
st.markdown("""
<style>
/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Main Container */
.main-chat-wrapper {
    max-width: 900px;
    margin: 0 auto;
    padding: 0;
}

/* Chat Header */
.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px 15px 0 0;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.chat-header h2 {
    margin: 0;
    font-size: 1.5em;
    font-weight: 600;
}

.chat-header p {
    margin: 5px 0 0 0;
    font-size: 0.9em;
    opacity: 0.9;
}

/* Chat Container */
.chat-container {
    background: #f0f2f5;
    padding: 25px;
    height: 550px;
    overflow-y: auto;
    border-left: 1px solid #e0e0e0;
    border-right: 1px solid #e0e0e0;
    scroll-behavior: smooth;
}

/* Scroll bar styling */
.chat-container::-webkit-scrollbar {
    width: 8px;
}

.chat-container::-webkit-scrollbar-track {
    background: #f0f2f5;
}

.chat-container::-webkit-scrollbar-thumb {
    background: #c0c0c0;
    border-radius: 10px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
    background: #a0a0a0;
}

/* Message Wrapper */
.message-wrapper {
    display: flex;
    margin-bottom: 16px;
    animation: fadeIn 0.3s ease;
}

.message-wrapper.user {
    justify-content: flex-end;
}

.message-wrapper.ai {
    justify-content: flex-start;
}

/* Avatar */
.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3em;
    flex-shrink: 0;
    margin: 0 10px;
}

.avatar.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    order: 2;
}

.avatar.ai {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    order: 1;
}

/* Message Bubble */
.message-bubble {
    max-width: 65%;
    padding: 12px 18px;
    border-radius: 18px;
    word-wrap: break-word;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    position: relative;
}

.message-bubble.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
    order: 1;
}

.message-bubble.ai {
    background: white;
    color: #333;
    border-bottom-left-radius: 4px;
    order: 2;
}

/* Message Content */
.message-content {
    margin: 0;
    line-height: 1.5;
    font-size: 0.95em;
}

.message-bubble.ai .message-content {
    color: #2c3e50;
}

.message-bubble.ai strong {
    color: #667eea;
    display: block;
    margin-bottom: 5px;
    font-size: 0.85em;
}

/* Timestamp */
.message-time {
    font-size: 0.75em;
    margin-top: 6px;
    opacity: 0.7;
    text-align: right;
}

.message-bubble.user .message-time {
    color: rgba(255,255,255,0.8);
}

.message-bubble.ai .message-time {
    color: #999;
    text-align: left;
}

/* Typing Indicator */
.typing-wrapper {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
}

.typing-indicator {
    background: white;
    padding: 15px 20px;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-left: 60px;
}

.typing-indicator span {
    height: 10px;
    width: 10px;
    background: #667eea;
    border-radius: 50%;
    display: inline-block;
    margin: 0 3px;
    animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-10px); opacity: 1; }
}

/* Input Container */
.input-container {
    background: white;
    padding: 20px;
    border-radius: 0 0 15px 15px;
    border: 1px solid #e0e0e0;
    border-top: none;
    box-shadow: 0 -2px 15px rgba(0,0,0,0.05);
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Status Badge */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
    margin: 5px 0;
}

.status-badge.online {
    background: #d4edda;
    color: #155724;
}

/* Welcome Card */
.welcome-card {
    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
    border: 2px solid #667eea40;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
}

.welcome-card h3 {
    color: #667eea;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ========================================
# INISIALISASI SESSION STATE
# ========================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({
        "role": "ai",
        "content": "👋 **Halo! Saya Career Assistant AI**\n\nSaya siap membantu Anda menemukan jalur karier yang tepat di bidang TIK!\n\n💡 **Ceritakan kepada saya:**\n• Pengalaman kerja Anda\n• Skill teknis yang dikuasai\n• Minat & passion karier\n\nYuk mulai percakapan! 🚀",
        "timestamp": datetime.now().strftime("%H:%M")
    })

if 'waiting_response' not in st.session_state:
    st.session_state.waiting_response = False

if 'trigger_ai_response' not in st.session_state:
    st.session_state.trigger_ai_response = False


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
        return f"❌ Maaf, terjadi kesalahan koneksi. Silakan coba lagi.\n\nDetail: {str(e)}"


# ========================================
# FUNGSI: ANALISIS KARIER AI
# ========================================
def get_career_analysis(user_message: str, chat_history: list) -> str:
    """Generate response dari AI berdasarkan context chat"""
    
    context = "\n".join([
        f"{'User' if msg['role']=='user' else 'AI'}: {msg['content']}" 
        for msg in chat_history[-6:]
    ])
    
    prompt = f"""Anda adalah Career Coach AI yang ramah dan profesional untuk bidang Teknologi Informasi dan Komunikasi (TIK).

=== CONTEXT PERCAKAPAN ===
{context}

=== PESAN USER TERBARU ===
{user_message}

=== INSTRUKSI ===
1. Jawab dengan ramah dan supportif seperti chat profesional
2. Gunakan emoji secukupnya (1-2 per respon)
3. Berikan analisis spesifik tentang karier TIK di Indonesia
4. Jika user cerita pengalaman: identifikasi skill & okupasi yang cocok (Software Engineer, Data Analyst, DevOps, dll)
5. Jika user tanya pelatihan: rekomendasikan platform (Coursera, Dicoding, MySkill, dll)
6. Jika user tanya lowongan: sebutkan jenis pekerjaan TIK yang sesuai
7. Maksimal 5-6 kalimat, padat & actionable
8. Gunakan bahasa Indonesia profesional tapi tetap hangat
9. Akhiri dengan pertanyaan follow-up jika perlu

Jawab sekarang:"""

    return call_gemini_api(prompt)


# ========================================
# FUNGSI: RENDER CHAT BUBBLE
# ========================================
def render_chat_bubble(message: dict):
    """Render chat bubble dengan avatar"""
    if message['role'] == 'user':
        st.markdown(f"""
        <div class="message-wrapper user">
            <div class="message-bubble user">
                <div class="message-content">{message['content']}</div>
                <div class="message-time">{message['timestamp']}</div>
            </div>
            <div class="avatar user">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        content_formatted = message['content'].replace('\n', '<br>')
        st.markdown(f"""
        <div class="message-wrapper ai">
            <div class="avatar ai">🤖</div>
            <div class="message-bubble ai">
                <div class="message-content">{content_formatted}</div>
                <div class="message-time">{message['timestamp']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ========================================
# FUNGSI: REKOMENDASI
# ========================================
def get_recommendations(okupasi_id, skill_gap, profil_teks):
    """Return: (jobs, trainings)"""
    job_samples = [
        {
            "Posisi": "Data Analyst",
            "Perusahaan": "Tech Innovate Indonesia",
            "Lokasi": "Jakarta Selatan",
            "Keterampilan_Dibutuhkan": "Python, SQL, Power BI, Excel",
            "Deskripsi_Pekerjaan": "Menganalisis data bisnis untuk insight strategis perusahaan fintech."
        },
        {
            "Posisi": "Machine Learning Engineer",
            "Perusahaan": "AI Labs Indonesia",
            "Lokasi": "Bandung",
            "Keterampilan_Dibutuhkan": "Python, TensorFlow, PyTorch, AWS",
            "Deskripsi_Pekerjaan": "Membangun dan deploy model AI untuk produk digital."
        },
        {
            "Posisi": "DevOps Engineer",
            "Perusahaan": "CloudTech Indonesia",
            "Lokasi": "Jakarta Pusat",
            "Keterampilan_Dibutuhkan": "Docker, Kubernetes, CI/CD, Terraform",
            "Deskripsi_Pekerjaan": "Mengelola infrastruktur cloud dan automation pipeline."
        },
        {
            "Posisi": "Frontend Developer",
            "Perusahaan": "Digital Creative",
            "Lokasi": "Yogyakarta",
            "Keterampilan_Dibutuhkan": "React, TypeScript, Tailwind CSS",
            "Deskripsi_Pekerjaan": "Membangun UI/UX responsive untuk aplikasi web modern."
        }
    ]

    training_samples = [
        "🎓 AWS Certified Solutions Architect (Dicoding Indonesia)",
        "📊 Data Science Bootcamp (MySkill Academy)",
        "⚙️ CI/CD Mastery dengan Jenkins & GitLab (Udemy)",
        "🧠 Machine Learning Intermediate (Coursera)",
        "🚀 Full Stack Web Development (Dicoding)",
        "☁️ Google Cloud Professional (Qwiklabs)"
    ]

    jobs = random.sample(job_samples, k=min(3, len(job_samples)))
    trainings = random.sample(training_samples, k=min(4, len(training_samples)))

    return jobs, trainings


# ========================================
# UI: HEADER
# ========================================
st.markdown("""
<div class="chat-header">
    <h2>💡 Career Assistant AI</h2>
    <p>Konsultasi Karier TIK dengan AI • <span class="status-badge online">● Online</span></p>
</div>
""", unsafe_allow_html=True)


# ========================================
# PROSES AI RESPONSE (Jika ada trigger)
# ========================================
if st.session_state.trigger_ai_response:
    last_message = st.session_state.chat_history[-1]
    if last_message['role'] == 'user':
        # Tampilkan typing indicator
        st.session_state.waiting_response = True
        
        # Get AI response
        ai_response = get_career_analysis(
            last_message['content'], 
            st.session_state.chat_history
        )
        
        # Tambahkan AI response
        st.session_state.chat_history.append({
            "role": "ai",
            "content": ai_response,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Save profil
        st.session_state['profil_teks'] = last_message['content']
        
        # Reset flags
        st.session_state.waiting_response = False
        st.session_state.trigger_ai_response = False


# ========================================
# UI: CHAT CONTAINER
# ========================================
st.markdown('<div class="chat-container" id="chat-box">', unsafe_allow_html=True)

for message in st.session_state.chat_history:
    render_chat_bubble(message)

if st.session_state.waiting_response:
    st.markdown("""
    <div class="typing-wrapper">
        <div class="avatar ai">🤖</div>
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ========================================
# UI: QUICK ACTIONS
# ========================================
st.markdown("#### ⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💼 Lowongan", use_container_width=True):
        st.session_state.chat_history.append({
            "role": "user",
            "content": "Lowongan apa yang cocok untuk saya?",
            "timestamp": datetime.now().strftime("%H:%M")
        })
        st.session_state.trigger_ai_response = True
        st.rerun()

with col2:
    if st.button("📚 Pelatihan", use_container_width=True):
        st.session_state.chat_history.append({
            "role": "user",
            "content": "Pelatihan apa yang sebaiknya saya ikuti?",
            "timestamp": datetime.now().strftime("%H:%M")
        })
        st.session_state.trigger_ai_response = True
        st.rerun()

with col3:
    if st.button("🎯 Analisis", use_container_width=True):
        st.session_state.chat_history.append({
            "role": "user",
            "content": "Analisis skill saya dan kasih saran karier",
            "timestamp": datetime.now().strftime("%H:%M")
        })
        st.session_state.trigger_ai_response = True
        st.rerun()

with col4:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.chat_history = [{
            "role": "ai",
            "content": "👋 **Chat direset!**\n\nSilakan mulai percakapan baru. Ceritakan tentang pengalaman dan minat karier Anda! 🚀",
            "timestamp": datetime.now().strftime("%H:%M")
        }]
        st.session_state.waiting_response = False
        st.session_state.trigger_ai_response = False
        st.rerun()


# ========================================
# UI: INPUT CHAT
# ========================================
st.markdown("---")

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ketik pesan Anda...",
            placeholder="Contoh: Saya punya pengalaman Python 2 tahun, cocok jadi apa ya?",
            label_visibility="collapsed",
            key="message_input"
        )
    
    with col2:
        send_button = st.form_submit_button("📤 Kirim", use_container_width=True)


# ========================================
# PROSES INPUT USER
# ========================================
if send_button and user_input.strip():
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    st.session_state.trigger_ai_response = True
    st.rerun()


# ========================================
# SECTION: PROFIL & REKOMENDASI (OPSIONAL)
# ========================================
if 'assessment_score' in st.session_state and 'mapped_okupasi_id' in st.session_state:
    
    st.markdown("---")
    st.markdown("### 👤 Profil & Hasil Asesmen Anda")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🆔 Talent ID", st.session_state.get('talent_id', '-'))
    col2.metric("💼 Okupasi", st.session_state.get('mapped_okupasi_nama', '-'))
    col3.metric("📊 Skor", f"{st.session_state.assessment_score}/100")
    col4.metric("📈 Status", "Tersertifikasi" if st.session_state.assessment_score >= 70 else "Perlu Pelatihan")
    
    st.markdown("---")
    
    if st.button("🎯 Lihat Rekomendasi Detail Lengkap", use_container_width=True):
        with st.spinner("🤖 Memproses rekomendasi terpersonalisasi..."):
            try:
                jobs, trainings = get_recommendations(
                    st.session_state.get('mapped_okupasi_id', ''),
                    st.session_state.get('skill_gap', []),
                    st.session_state.get('profil_teks', '')
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
                jobs, trainings = [], []
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💼 Lowongan Rekomendasi")
            
            if not jobs:
                st.info("📭 Belum ada lowongan yang cocok saat ini.")
            else:
                for idx, job in enumerate(jobs, 1):
                    with st.expander(f"🧩 **{job['Posisi']}** — {job['Perusahaan']}", expanded=(idx==1)):
                        st.markdown(f"**📍 Lokasi:** {job['Lokasi']}")
                        st.markdown(f"**🛠️ Skill:** `{job['Keterampilan_Dibutuhkan']}`")
                        st.markdown(f"**📝 Deskripsi:**")
                        st.write(job['Deskripsi_Pekerjaan'])
                        st.button(f"Lamar Sekarang →", key=f"apply_{idx}", use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Pelatihan Rekomendasi")
            st.info(f"**🎓 Skill Gap:** `{st.session_state.get('skill_gap', '-')}`")
            
            if not trainings:
                st.info("📭 Belum ada rekomendasi pelatihan.")
            else:
                for training in trainings:
                    st.success(training)
                
                st.markdown("---")
                st.markdown("**📚 Platform Belajar:**")
                st.markdown("• [Dicoding Indonesia](https://dicoding.com)")
                st.markdown("• [MySkill Academy](https://myskill.id)")
                st.markdown("• [Coursera](https://coursera.org)")
