import streamlit as st
import google.generativeai as genai
import os
import requests
from PIL import Image
from io import BytesIO
import time

# =========================================================
# 1. НАСТРОЙКА СТРАНИЦЫ И СТИЛЕЙ
# =========================================================
st.set_page_config(page_title="ToU AI Advisor", page_icon="🎓", layout="wide")

# Получение API ключа
API_KEY = st.secrets.get("API_KEY", "")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #fcfcfc; }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 10px;
        background: linear-gradient(90deg, #0055A4 0%, #007FFF 50%, #FFCC00 100%); z-index: 9999;
    }
    .main-title { color: #0055A4; font-size: 2.2rem; font-weight: 700; border-bottom: 2px solid #FFCC00; padding-bottom: 10px; }
    .sub-title { color: #666; font-size: 1.1rem; margin-bottom: 25px; }
    .footer { text-align: center; color: #888; font-size: 0.8rem; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ВЕРХНЯЯ ПАНЕЛЬ (ЛОГО И ЗАГОЛОВОК) ---
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    try:
        response = requests.get("https://tou.edu.kz/images/logo_tou_ru.png", timeout=5)
        img = Image.open(BytesIO(response.content))
        st.image(img, width=180)
    except:
        st.markdown("<h2 style='color:#0055A4;'>ToU</h2>", unsafe_allow_html=True)

with header_col2:
    st.markdown("<div class='main-title'>Виртуальный консультант Торайгыров Университета</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Интеллектуальная поддержка факультета Computer Science</div>", unsafe_allow_html=True)

# =========================================================
# 2. Я
