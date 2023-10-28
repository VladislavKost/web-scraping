
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import bs4
import fake_headers
import requests
import json
from tqdm import tqdm




def wait_element(browser, delay_seconds=1, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


def get_pages_amount(browser, url):
    print('Определяю общее количество страниц с результатами')
    browser.get(url)
    pages_block = wait_element(browser, 1, By.CLASS_NAME, "pager")
    pages_amount = pages_block.text.split()[-2][-2:]
    return pages_amount


def get_vacancies_urls(browser, url):

    pages_total_amount = get_pages_amount(browser, url)

    pages_amount = input(
        f"Общее число страниц по данному запросу: {pages_total_amount}. Какое количество страниц необходимо просмотреть? Введите число от 1 до {pages_total_amount}: "
    )

    parsed_vacansies = []
    for page in range(int(pages_amount)):
        url_to_get = f"{url}&page={page}"
        browser.get(url_to_get)
        vacancy_list_tag = wait_element(
            browser, 1, By.CLASS_NAME, "vacancy-serp-content"
        )
        vacancy_tags = vacancy_list_tag.find_elements(By.CLASS_NAME, "serp-item")
        for vacancy_tag in vacancy_tags:
            a_tag = wait_element(vacancy_tag, 1, By.CLASS_NAME, "serp-item__title")
            link = a_tag.get_attribute("href")
            parsed_vacansies.append({"link": link})
    browser.quit()
    return parsed_vacansies


def get_company_name(main_soup):
    company_tag = main_soup.find("span", class_="vacancy-company-name")
    company_name = company_tag.text.replace("\xa0", " ")
    return company_name


def get_salary(main_soup):
    head_tag = main_soup.find("div", class_="vacancy-title")
    salary_tag = head_tag.find(
        "span", class_="bloko-header-section-2 bloko-header-section-2_lite"
    )
    if salary_tag:
        salary = salary_tag.text.replace("\xa0", " ")
    else:
        salary = "Не указана"
    return salary


def get_city(main_soup):
    city_tag = main_soup.find(
        "a", class_="bloko-link bloko-link_kind-tertiary bloko-link_disable-visited"
    )
    if city_tag:
        city_name = city_tag.text.split(", ")[0]
    else:
        city_tag = main_soup.find("div", class_="vacancy-company-redesigned")
        city_name = city_tag.find("p").text.replace("\xa0", " ")
    return city_name


def check_skills(main_soup, skiils):
    vacansy_skills = main_soup.find("div", class_="bloko-tag-list")
    if vacansy_skills:
        vacansy_skills_text = [skill.text for skill in vacansy_skills.find_all("span")]
        for skill in skiils:
            if skill in vacansy_skills_text:
                return True
    return False


def get_vacancies_list(parsed_vacanсies):
    result = []
    skills = ["Django", "Flask", "Django Framework"]
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    for parsed_vacansy in tqdm(parsed_vacanсies, desc = 'Обработка вакансий'):
        response = requests.get(parsed_vacansy["link"], headers=headers_gen.generate())
        main_html_data = response.text
        main_soup = bs4.BeautifulSoup(main_html_data, "lxml")
        if check_skills(main_soup, skills):

            salary = get_salary(main_soup)
            company_name = get_company_name(main_soup)
            city_name = get_city(main_soup)

            result.append(
                {
                    "link": parsed_vacansy["link"],
                    "company": company_name,
                    "city": city_name,
                    "salary": salary,
                }
            )
    return result


def make_json(result):
    with open("vacansies.json", "w", encoding="UTF-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print('Загрузка завершена')
