from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from headhunter import get_vacancies_urls, get_vacancies_list, make_json



chrome_driver_path = ChromeDriverManager().install()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser_servise = Service(executable_path=chrome_driver_path)
browser = Chrome(service=browser_servise, options=options)

url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"

if __name__ == '__main__':
    vacancies_url = get_vacancies_urls(browser, url)
    get_suitable_vacancies = get_vacancies_list(vacancies_url)
    make_json(get_suitable_vacancies)