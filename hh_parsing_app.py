import streamlit as st
import openai

from parse_hh import get_html, extract_vacancy_data, extract_resume_data


st.title("CV Scoring App")

# Ключ только из Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def load_system_prompt(path: str = "prompts/system_prompt.txt") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are an experienced technical recruiter."


SYSTEM_PROMPT = load_system_prompt()


def request_gpt(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        temperature=0,
    )
    return response.choices[0].message.content


# Инициализация состояния (чтобы авто-загрузка не ломала ручной ввод)
if "job_description" not in st.session_state:
    st.session_state["job_description"] = ""
if "cv" not in st.session_state:
    st.session_state["cv"] = ""


st.subheader("Автозагрузка по ссылке (HH)")

vacancy_url = st.text_input("URL вакансии (hh.ru)", key="vacancy_url")
resume_url = st.text_input("URL резюме (hh.ru)", key="resume_url")

col_a, col_b = st.columns(2)

with col_a:
    if st.button("Загрузить вакансию", key="btn_load_vacancy"):
        try:
            html = get_html(vacancy_url)
            st.session_state["job_description"] = extract_vacancy_data(html)
            st.success("Вакансия загружена.")
        except Exception as e:
            st.error(f"Не удалось загрузить вакансию: {e}")

with col_b:
    
    if st.button("Загрузить резюме", key="btn_load_resume"):
        try:
            html = get_html(resume_url)
            st.session_state["cv"] = extract_resume_data(html)
            st.success("Резюме загружено.")
        except Exception as e:
            st.error(f"Не удалось загрузить резюме: {e}")


st.subheader("Ручной ввод / редактирование")

job_description = st.text_area(
    "Введите описание вакансии",
    value=st.session_state["job_description"],
    height=220,
    key="job_description_area",
)

cv = st.text_area(
    "Введите описание резюме",
    value=st.session_state["cv"],
    height=220,
    key="cv_area",
)

# синхронизация обратно в session_state
st.session_state["job_description"] = job_description
st.session_state["cv"] = cv


if st.button("Score CV", key="btn_score"):
    with st.spinner("Scoring CV..."):
        response = request_gpt(
            SYSTEM_PROMPT,
            f"Job description:\n{job_description}\n\nCV:\n{cv}"
        )
    st.write(response)
