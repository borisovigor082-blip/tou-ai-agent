import streamlit as st
import google.generativeai as genai
import os
import time

# Настройки
st.set_page_config(page_title="ToU AI Advisor", layout="wide")
API_KEY = st.secrets.get("API_KEY", "")

# Центрированный заголовок
st.markdown("<h1 style='text-align: center; color: #0055A4;'>ToU AI Advisor</h1>", unsafe_allow_html=True)

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        
        # Читаем базу
        if os.path.exists("knowledge.txt"):
            with open("knowledge.txt", "r", encoding="utf-8") as f:
                context = f.read()
        else:
            context = "Информация об университете ToU."

        # Форма поиска — КРИТИЧНО для борьбы с 429
        with st.form(key='search_form'):
            user_input = st.text_input("Введите ваш вопрос:")
            submit = st.form_submit_button("Найти ответ")

        if submit and user_input:
            # Ищем модель динамически
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_name = next((m for m in models if '1.5-flash' in m), models[0])
            
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=f"Ты помощник ToU. Отвечай кратко по тексту: {context}"
            )

            with st.spinner("Запрос к ИИ..."):
                try:
                    # Самый важный фикс: если упало, просто выводим текст, а не вешаем сайт
                    res = model.generate_content(user_input)
                    st.success("Ответ найден:")
                    st.write(res.text)
                except Exception as e:
                    if "429" in str(e):
                        st.warning("⚠️ Лимит запросов. Просто подождите ровно 1 минуту, не нажимая кнопку.")
                    else:
                        st.error(f"Ошибка: {e}")

    except Exception as e:
        st.error(f"Ошибка инициализации: {e}")
else:
    st.info("Добавьте API_KEY в настройки Secrets.")
