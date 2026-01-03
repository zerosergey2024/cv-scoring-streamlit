import requests
from bs4 import BeautifulSoup


def get_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    # Важно: возвращаем ТЕКСТ HTML, а не объект response
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


def extract_vacancy_data(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def safe_text(tag, attrs=None):
        el = soup.find(tag, attrs or {})
        return el.get_text(strip=True) if el else "Не найдено"

    title = safe_text("h1")
    salary = safe_text("span", {"data-qa": "vacancy-salary"})
    company = safe_text("a", {"data-qa": "vacancy-company-name"})

    description = soup.find("div", {"data-qa": "vacancy-description"})
    description_text = description.get_text(separator="\n").strip() if description else "Описание не найдено"

    markdown = f"# {title}\n\n"
    markdown += f"**Компания:** {company}\n\n"
    markdown += f"**Зарплата:** {salary}\n\n"
    markdown += f"## Описание\n\n{description_text}"

    return markdown.strip()


def extract_resume_data(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def safe_text(tag, **kwargs):
        el = soup.find(tag, kwargs)
        return el.get_text(strip=True) if el else "Не найдено"

    name = safe_text("h2", data_qa="bloko-header-1")
    gender_age = safe_text("p")
    location = safe_text("span", data_qa="resume-personal-address")
    job_title = safe_text("span", data_qa="resume-block-title-position")
    job_status = safe_text("span", data_qa="job-search-status")

    experiences = []
    experience_section = soup.find("div", {"data-qa": "resume-block-experience"})
    if experience_section:
        experience_items = experience_section.find_all("div", class_="resume-block-item-gap")
        for item in experience_items:
            try:
                period = item.find("div", class_="bloko-column_s-2").get_text(strip=True)
                duration = item.find("div", class_="bloko-text").get_text(strip=True)
                period = period.replace(duration, f" ({duration})")

                company = item.find("div", class_="bloko-text_strong").get_text(strip=True)
                position = item.find("div", {"data-qa": "resume-block-experience-position"}).get_text(strip=True)
                description = item.find("div", {"data-qa": "resume-block-experience-description"}).get_text(strip=True)

                experiences.append(
                    f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n"
                )
            except Exception:
                continue

    skills = []
    skills_section = soup.find("div", {"data-qa": "skills-table"})
    if skills_section:
        skills = [
            tag.get_text(strip=True)
            for tag in skills_section.find_all("span", {"data-qa": "bloko-tag__text"})
        ]

    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    markdown += "\n".join(experiences) if experiences else "Опыт работы не найден.\n"
    markdown += "\n## Ключевые навыки\n\n"
    markdown += ", ".join(skills) if skills else "Навыки не указаны.\n"

    return markdown.strip()
