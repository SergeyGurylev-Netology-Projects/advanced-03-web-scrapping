import json
import re
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


def get_headers():
    return Headers(browser='firefox', os='win').generate()


REGEX_DF = re.compile(r'Django.*Flask|Flask.*Django')
REGEX_USD = re.compile(r'USD')
params = {'text': 'python', 'area': [1, 2], 'only_with_salary': 'true'}
result = []

for page in range(0,10):
    print(page)
    response = requests.get('https://hh.ru/search/vacancy', params={**params, **{'page': page}}, headers=get_headers())
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', class_='vacancy-serp-content')
    content_items = content.find_all('div', class_='serp-item')

    for item in content_items:
        salary = item.find(attrs={"data-qa": 'vacancy-serp__vacancy-compensation'})
        REGEX_USD.search(salary.text)
        if REGEX_USD.search(salary.text) is None:
            continue

        title = item.find('a', class_='serp-item__title')

        item_company = item.find('div', class_='vacancy-serp-item-company')
        company_name = item_company.find(attrs={"data-qa": "vacancy-serp__vacancy-employer"})
        company_locale = item_company.find(attrs={"data-qa": "vacancy-serp__vacancy-address"})

        vacancy_item = requests.get(title['href'], headers=get_headers())
        vacancy_soup = BeautifulSoup(vacancy_item.text, 'html.parser')
        content_list = vacancy_soup.find('div', class_='vacancy-description').find_all('li')
        item_text = ''.join(li.text for li in content_list)
        if REGEX_DF.search(item_text) is not None:
            result.append(
                {'href': title['href'],
                 'company_name': company_name.text,
                 'company_locale': company_locale.text,
                 'salary': salary.text
                }
            )

with open('result.json', 'w', encoding='utf8') as file:
    json.dump(result, file, indent=2, ensure_ascii=False)