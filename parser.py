import os
import time
import re

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from openpyxl import Workbook

def find_all(title):
    """Функция находит информацию по столбцам тип, название, номер, дата, описание, текст"""
    type_doc = ['указ', 'распоряжение', 'федеральный закон', 'федеральный конституционный закон', 'послание',
                'закон российской федерации о поправке', 'кодекс']
    new_text = title
    type = None
    # ищем тип документа
    for i in type_doc:
        if i in new_text.lower():
            type = i
            break

    # добавляем название документа
    name = new_text[:new_text.find('\n')] if new_text.find('\n') >= 0 else None

    # ищем номер документа
    pattern_num = r'\b\d{3}(?:-?[А-Яа-я]{2})?\b'
    nums = re.findall(pattern_num, new_text[:new_text.find('\n')])
    number = nums[0] if nums else None

    # ищем дату
    pattern_date = r"\b\d{2}.\d{2}.\d{4}\b"
    dates = re.findall(pattern_date, new_text)
    date = dates[0] if dates else None

    # добавляем описание и текст
    description = new_text[new_text.find('\n') + 1:]
    description = description[:description.find('\n')]
    text = new_text.replace('\n', ', ') # заменяем в тексте \n на запятую
    row = [type, name, number, date, description, text]
    return row


class KremlinParser:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0')
    options.add_argument(rf"--user-data-dir=C:\Users\{os.getenv('PROFILE')}\
    AppData\Local\Google\Chrome\User Data\Default")
    options.add_argument("--incognito")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def __init__(self, start_dates, end_dates):
        self.driver = webdriver.Chrome(options=self.options)
        self.start_dates = start_dates
        self.end_dates = end_dates
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        headers = ['Тип документа', 'Название', 'Номер', 'Дата', 'Описание', 'Текст']
        self.sheet.append(headers)

    def __find_element(self, by, value):
        try:
            # Wait for the element to be present and visible
            wait = WebDriverWait(self.driver, 10)  # Maximum wait time of 10 seconds
            wait.until(EC.visibility_of_element_located((by, value)))
            elements = self.driver.find_elements(by=by, value=value)
            return elements

        except TimeoutException:
            print(f'❓{value} элемент не найден')
            # обработка ошибки какая-нибудь

    def start_parsing(self):
        for date_start, date_end in zip(self.start_dates, self.end_dates):
            self.driver.get(
                f"http://kremlin.ru/acts/bank/search?force_since={date_start}&force_till={date_end}")
            if 'Искомая комбинация слов нигде не встречается.' in self.driver.page_source:
                print(f'{date_start} - {date_end} - таких документов нету')
            else:
                titles = self.__find_element(by='xpath', value="//*[contains(@class, 'hentry__title hentry__title_special')]")
                for text in titles:
                    self.sheet.append(find_all(text.text))
                self.workbook.save('documents.xlsx')

        time.sleep(9999999)


def main(date_start, date_end):
    browser = KremlinParser([date_start], [date_end])
    browser.start_parsing()


if __name__ == '__main__':
    date_start = input('Введите дату начала периода: дд.мм.гггг: ')
    date_end = input('Введите дату окончания периода: дд.мм.гггг: ')
    main(date_start, date_end)
