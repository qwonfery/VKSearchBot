import io
import time

import requests
from bs4 import BeautifulSoup

DOMAIN_RU = "yandex.ru"
DOMAIN_TR = "yandex.com.tr"
DOMAIN_UNIVERSAL = "yandex.com"

API_URL = f"https://{DOMAIN_RU}/search/xml"
API_KEY = "AQVN3a6cwFDdkEXQxpUPnSYNDnrRWZsdmusbTfRB"
FOLDER_ID = "b1g5hj8ub56gibs6hcav"
DELAY = 0.7

TOPS = [1, 3, 5, 10]


def yandex_search(query, folder_id, api_key):
    """
    Отправляет запрос к Yandex Search API и возвращает результаты.

    :param folder_id: идентификатор каталога, нужен для авторизации
    :param api_key: API-ключ для доступа к Yandex Search API.
    :param query: Поисковый запрос.
    :param page: Номер страницы результатов (по умолчанию 1).
    :param results_per_page: Количество результатов на странице (по умолчанию 10).
    :return: JSON с результатами поиска.
    """

    params = {
        "folderid": folder_id,
        "apikey": api_key,
        "query": query,
        "page": 0,  # В API нумерация страниц начинается с 0
        "groupby": "attr=d.groups-on-page=10.docs-in-group=1",
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        return response.text  # XML-ответ в виде текста
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None


def find_top(n, tops):
    current = tops[0]
    for top in tops:
        current = top
        if n <= current:
            break
    return current


def parse_xml(xml: str) -> list:
    soup = BeautifulSoup(xml, 'xml')
    groups = soup.find('yandexsearch').find('response').find('results')
    groups = groups.find_all('group')
    doms = dict()
    for group in groups:
        doms[group.find('domain').text] = group.find('doccount').text
    doms_list = doms.items()
    sorted_list = sorted(doms_list, key=lambda x: int(x[1]), reverse=True)

    return sorted_list


def find_in_top(top_list, target_domains):
    target_top = []
    top_list_domains = [i[0] for i in top_list]
    for domain in target_domains:
        try:
            n = top_list_domains.index(domain) + 1
        except ValueError:
            n = 10
        position = find_top(n, TOPS)
        target_top.append((domain, position))
    return target_top


def process_queries(queries: str, api_key: str, folder_id: str, domains: str) -> str:
    domains = domains.split(', ')
    domains_in_top = dict()
    for domain in domains:
        for top in TOPS:
            domains_in_top[domain, top] = 0
    for query in queries.split('\n'):
        xml = yandex_search(query=query, folder_id=folder_id, api_key=api_key)
        dom_top = parse_xml(xml)
        dom_top = find_in_top(dom_top, domains)

        for dom in dom_top:
            domains_in_top[dom[0], dom[1]] += 1
        time.sleep(DELAY)

    # Преобразуем словарь в таблицу
    table = []
    # Добавляем заголовок таблицы
    table.append(["Domain"] + list(map(str, TOPS)))

    # Добавляем строки таблицы
    for domain in domains:
        row = [domain]
        for top in TOPS:
            row.append(domains_in_top.get((domain, top), 0))
        table.append(row)
    print(table)


    # Преобразуем каждый внутренний список в строку, разделенную запятыми
    rows = [','.join(map(str, row)) for row in table]
    # Объединяем строки с помощью символа новой строки
    content = '\n'.join(rows)
    # Преобразование строки в файл в памяти
    file_stream = io.BytesIO(content.encode("utf-8"))
    file_stream.name = "example.txt"  # Имя файла, которое будет отображаться пользователю

    return content


def console_controller():
    print("Привет! Отправь мне название CSV/TXT файла с запросами. Он должен быть в той же папке что и скрипт.")
    with open(input(), 'r') as f:
        queries = f.read()
    print("Теперь отправь ключ API.")
    api_key = input()
    print("Теперь отправь идентификатор каталога.")
    folder_id = input()
    print("Теперь отправьте домен или домены, по которым мы будем смотреть позиции (разделите домены запятой).")
    domains = input()

    with open('output.txt', 'w') as f:
        f.write(process_queries(queries, api_key, folder_id, domains))


if __name__ == '__main__':
    # domains = "vk.com, rutube.ru, dzen.ru"
    # query1 = "субстанция фильм смотреть онлайн"
    # query2 = 'вк видео смотреть онлайн бесплатно'
    # # res = yandex_search(query1, FOLDER_ID, API_KEY)
    # # res = parse_xml(res)
    # # print(res)
    # # res = find_in_top(res, domains)
    # res = process_queries(query1 + '\n' + query2, API_KEY, FOLDER_ID, domains)
    # print(res)
    console_controller()

