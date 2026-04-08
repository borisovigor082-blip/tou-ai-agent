import streamlit as st
import google.generativeai as genai
import os
import requests
from PIL import Image
from io import BytesIO

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="ToU AI Advisor", page_icon="🎓", layout="wide")
API_KEY = st.secrets.get("API_KEY", "")

# --- СТИЛИ ---
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
    .answer-box { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e0e6ed; box-shadow: 0 2px 5px rgba(0,85,164,0.05); }
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

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

# --- ПОЛЕ ВВОДА ---
query = st.text_input("Введите ваш вопрос:", placeholder="Например: кто декан факультета?")

# --- ЛОГИКА ---
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        
        if os.path.exists("knowledge.txt"):
            with open("knowledge.txt", "r", encoding="utf-8") as f:
                kb_content = f.read()
        else:
            st.error("knowledge.txt не найден")
            st.stop()

        @st.cache_resource
        def load_model(context):
            # Используем последнюю стабильную версию
            return genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=f"Ты — консультант ToU. Отвечай только по делу, используя эти данные: {context}"
            )

        model = load_model(kb_content)

        # Если ввели новый вопрос, которого не было в прошлый раз
        if query and query != st.session_state.last_query:
            with st.spinner('Сверяюсь с базой знаний...'):
                try:
                    response = model.generate_content(query)
                    st.session_state.last_answer = response.text
                    st.session_state.last_query = query
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Лимит запросов. Подождите 15 секунд.")
                    else:
                        st.error(f"Ошибка: {e}")

        # Вывод ответа, если он есть в памяти
        if st.session_state.last_answer:
            st.markdown("### Ответ:")
            st.markdown(f"<div class='answer-box'>{st.session_state.last_answer}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Критическая ошибка: {e}")
else:
    st.warning("⚠️ Добавьте API_KEY в Secrets.")

st.markdown("<div class='footer'>© 2026 ToU. Разработано в рамках учебной практики.</div>", unsafe_allow_html=True)
