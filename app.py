import streamlit as st
import google.generativeai as genai
import os
import requests
from PIL import Image
from io import BytesIO
import time

# =========================================================
# 1. КОНФИГУРАЦИЯ И СТИЛИЗАЦИЯ
# =========================================================
st.set_page_config(page_title="ToU AI Advisor", page_icon="🎓", layout="wide")

# Инициализация ключа из Secrets или напрямую
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

# --- ШАПКА ---
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
# 2. ЛОГИКА РАБОТЫ С БАЗОЙ ЗНАНИЙ И МОДЕЛЬЮ
# =========================================================

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)

        # Загрузка базы знаний
        if os.path.exists("knowledge.txt"):
            with open("knowledge.txt", "r", encoding="utf-8") as f:
                kb_content = f.read()
        else:
            st.error("Файл knowledge.txt не найден! Создайте его в корневой папке.")
            st.stop()

        # Инициализация модели с системной инструкцией (экономит квоту)
        @st.cache_resource
        def load_model():
            return genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=f"Ты — официальный ИИ-консультант ToU. Отвечай кратко, используя этот контекст: {kb_content}. Если вопроса нет в контексте, вежливо скажи, что не владеешь этой информацией и предложи обратиться в деканат."
            )

        model = load_model()

        # Работа с историей чата
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Отображение истории
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Поле ввода
        if prompt := st.chat_input("Напишите ваш вопрос (например: где узнать об оплате?)..."):
            # Добавляем вопрос пользователя в чат
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Генерация ответа
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    # Сама генерация
                    response = model.generate_content(prompt)
                    full_response = response.text
                    message_placeholder.markdown(full_response)
                    
                    # Сохраняем ответ
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg:
                        st.error("⚠️ Превышен лимит запросов. Подождите 30-60 секунд.")
                    else:
                        st.error(f"Произошла ошибка: {error_msg}")

    except Exception as e:
        st.error(f"Ошибка конфигурации: {e}")
else:
    st.warning("⚠️ API_KEY не найден. Пожалуйста, добавьте его в настройки (Secrets).")

# --- ПОДВАЛ ---
st.markdown("<div class='footer'>© 2026 ToU. Разработано в рамках учебной практики.</div>", unsafe_allow_html=True)
