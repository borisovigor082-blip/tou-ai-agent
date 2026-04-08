import streamlit as st
import google.generativeai as genai
import os
import requests
from PIL import Image
from io import BytesIO

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="ToU AI Advisor", page_icon="🎓", layout="wide")
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
    .answer-box { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e0e6ed; box-shadow: 0 2px 5px rgba(0,85,164,0.05); }
    .footer { text-align: center; color: #888; font-size: 0.8rem; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ШАПКА ---
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
    st.markdown("<div style='color: #666; margin-bottom: 20px;'>Интеллектуальная поддержка факультета Computer Science</div>", unsafe_allow_html=True)

# --- 3. ИНИЦИАЛИЗАЦИЯ И ПОИСК МОДЕЛИ ---
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

query = st.text_input("Введите ваш вопрос:", placeholder="Например: какие документы нужны для поступления?")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)

        # Загрузка базы знаний
        if os.path.exists("knowledge.txt"):
            with open("knowledge.txt", "r", encoding="utf-8") as f:
                kb_content = f.read()
        else:
            st.error("Файл knowledge.txt не найден!")
            st.stop()

        # УМНЫЙ ПОДБОР МОДЕЛИ (Решает ошибку 404)
        @st.cache_resource
        def get_available_model(context):
            try:
                # Получаем список всех доступных моделей для этого ключа
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Ищем самую подходящую (Flash 1.5, затем Pro, затем остальные)
                best_model = None
                for name in models:
                    if 'gemini-1.5-flash' in name:
                        best_model = name
                        break
                if not best_model:
                    for name in models:
                        if 'gemini-pro' in name or 'gemini-1.5-pro' in name:
                            best_model = name
                            break
                
                target = best_model if best_model else models[0]
                return genai.GenerativeModel(
                    model_name=target,
                    system_instruction=f"Ты — консультант ToU. Отвечай кратко на основе этого текста: {context}"
                )
            except Exception as e:
                st.error(f"Не удалось найти рабочую модель: {e}")
                return None

        model = get_available_model(kb_content)

        if query and query != st.session_state.last_query:
            if model:
                with st.spinner('Ищу ответ в базе знаний...'):
                    try:
                        response = model.generate_content(query)
                        st.session_state.last_answer = response.text
                        st.session_state.last_query = query
                    except Exception as e:
                        if "429" in str(e):
                            st.error("⚠️ Слишком много запросов. Подождите 15 секунд.")
                        else:
                            st.error(f"Ошибка при генерации: {e}")
            else:
                st.error("Модели Gemini временно недоступны.")

        if st.session_state.last_answer:
            st.markdown("### Ответ:")
            st.markdown(f"<div class='answer-box'>{st.session_state.last_answer}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ошибка инициализации: {e}")
else:
    st.warning("⚠️ Пожалуйста, добавьте API_KEY в настройки (Secrets).")

st.markdown("<div class='footer'>© 2026 ToU. Разработано в рамках учебной практики.</div>", unsafe_allow_html=True)
