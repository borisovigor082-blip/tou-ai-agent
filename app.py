import streamlit as st
import google.generativeai as genai
import os
import requests
from PIL import Image
from io import BytesIO

# =========================================================
# 1. КОНФИГУРАЦИЯ И СТИЛИЗАЦИЯ
# =========================================================
st.set_page_config(page_title="ToU AI Advisor", page_icon="🎓", layout="wide")

# Получение API ключа из Secrets
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

# =========================================================
# 2. ПОЛЕ ПОИСКА (ИНТЕРФЕЙС НАВЕРХУ)
# =========================================================
prompt = st.text_input("Введите ваш вопрос:", placeholder="Например: как узнать задолженность по оплате?")

# =========================================================
# 3. ЛОГИКА ИИ
# =========================================================
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

        # Автоподбор модели (защита от 404)
        @st.cache_resource
        def get_model():
            try:
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                for target in target_models:
                    for real_name in available:
                        if target in real_name:
                            return genai.GenerativeModel(
                                model_name=real_name,
                                system_instruction=f"Ты — консультант ToU. Отвечай кратко на основе этого текста: {kb_content}"
                            )
                return genai.GenerativeModel(available[0]) if available else None
            except:
                return None

        model = get_model()

        if prompt and model:
            with st.spinner('Поиск информации...'):
                try:
                    # Генерация ответа
                    response = model.generate_content(prompt)
                    
                    st.markdown("### Ответ консультанта:")
                    st.markdown(f"<div class='answer-box'>{response.text}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Превышен лимит запросов. Пожалуйста, подождите 30 секунд.")
                    else:
                        st.error(f"Ошибка API: {e}")
        elif not model:
            st.error("Доступные модели не найдены.")

    except Exception as e:
        st.error(f"Ошибка: {e}")
else:
    st.warning("⚠️ Добавьте API_KEY в Secrets.")

# --- ПОДВАЛ ---
st.markdown("<div class='footer'>© 2026 ToU. Разработано в рамках учебной практики.</div>", unsafe_allow_html=True)
