import csv
import pathlib
import time

import requests
from bs4 import BeautifulSoup

from settings import LOGGER, Month

url = "https://announcements.bybit.com/en-US/?category=&page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0)"
                  " Gecko/20100101 Firefox/110.0",
    "Accept-Language": "en-US,en;q=0.5"
}


@LOGGER.catch
def get_page(num: int = 1) -> requests.models.Response:
    """Метод обращается к сайту и забирает HTML-page"""
    return requests.get(
        url=f"https://announcements.bybit.com/"
            f"en-US/?category=&page={num}",
        headers=headers,
        stream=True
    )


@LOGGER.catch
def create_date(date: str) -> str | bool:
    try:
        month = Month[date[:3]].value
    except KeyError:
        return False
    year = date[-4:]
    day = date.split(",")[0][3:].lstrip()
    return f"{year}-{month}-{day}"


@LOGGER.catch
def validator(page: requests.models.Response) -> list | bool | None:
    """Метод валидирует HTML-page в собираемую нами информацию"""
    soup = BeautifulSoup(page.text, "html.parser")
    result = []
    find_href = soup.findAll(
        name="a",
        class_="no-style"
    )
    try:
        find_href[0]
    except IndexError:
        return None
    find_date = soup.findAll(
        name="div",
        class_="article-item-date"
    )
    find_name = soup.findAll(
        name="div",
        class_="ant-row ant-row-space-between article-item-content"
    )
    for i in range(len(find_href)):
        date = create_date(str(find_date[i].contents[0]))
        if date is False:
            return False
        name = find_name[i].find('span').contents[0]
        href = f"https://announcements.bybit.com/en-US{find_href[i]['href']}"
        result.append([date, name, href])
    return result


@LOGGER.catch
def mywriter(data: list, new_row: bool = False) -> bool:
    """Метод реализует запись в файл"""
    if new_row is True:
        with open("example.csv", "r") as file:
            lines = list(csv.reader(file))
        lines.insert(0, data)
        with open("example.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerows(lines)
        return True
    path = pathlib.Path("example.csv")
    if path.exists() is True:
        file = open("example.csv", "a", newline="", encoding="utf-8")
        writer = csv.writer(file)
        writer.writerows(data)
        LOGGER.info("Посты были добавлены в файл")
        file.close()
    else:
        file = open("example.csv", 'w', newline="", encoding="utf-8")
        LOGGER.info("Файл для записи был создан")
        writer = csv.writer(file)
        writer.writerows(data)
        file.close()
        LOGGER.info("Публакции со страницы были записаны")
    return True


def myreader(flag: bool = False, new_row: list = None) -> list | None:
    """Метод читает строки из файла,
     если флаг установлен и передано значение,
      проверяет это значение на уникальность"""
    if flag is True:
        file = open("example.csv", "r")
        read = csv.reader(file)
        for row in read:
            if row[1] == new_row[1]:
                return None
        LOGGER.info("Пост оказался Уникальным")
        return new_row
    file = open("example.csv", "r")
    read = csv.reader(file)
    result = []
    counter = 0
    for row in read:
        if 1 <= counter <= 9:
            result.append(row)
        counter += 1
        if counter >= 10:
            break
    return result


@LOGGER.catch
def collector():
    """Метод собирает все записи с сайта"""
    num = 1
    LOGGER.info(f"Номер запроса {num}")
    while True:
        time.sleep(1)
        page = get_page(num=num)
        data = validator(page=page)
        if data is None:
            LOGGER.info("Работа коллектора была завершена")
            break
        if data is False:
            continue
        else:
            LOGGER.info(f"Страница {num} была собрана.")
            mywriter(data=data)
        num += 1


@LOGGER.catch
def vatcher():
    while True:
        time.sleep(1)
        page = get_page()
        new_data = validator(page=page)
        for row in new_data:
            res = myreader(flag=True, new_row=row)
            if res is None:
                continue
            else:
                mywriter(data=res, new_row=True)


@LOGGER.catch
def main():
    collector()
    LOGGER.info("Запущен наблюдатель")
    vatcher()


if __name__ == "__main__":
    collector()
    LOGGER.info("Запущен наблюдатель")
    vatcher()
