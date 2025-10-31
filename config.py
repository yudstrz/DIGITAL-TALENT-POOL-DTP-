# config.py
"""
Konfigurasi sistem - hanya berisi path dan konstanta
"""

import os

# Path ke file Excel database
EXCEL_PATH = os.path.join("data", "DTP_Database.xlsx")

# Nama sheet di Excel
SHEET_PON = "PON_TIK"
SHEET_LOWONGAN = "Lowongan_Kerja"
SHEET_HASIL = "Hasil_Asesmen"
SHEET_TALENTA = "Profil_Talenta"

# API Configuration
GEMINI_API_KEY = "AIzaSyCR8xgDIv5oYBaDmMyuGGWjqpFi7U8SGA4"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-flash-latest"

# Konstanta
JUMLAH_SOAL = 5
