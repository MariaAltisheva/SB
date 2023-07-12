# TODO Необходимо для каждого периода задолженности по каждому клиенту вывести текущий
# порядковый номер месяца с задолженностью в рамках периода.
# В рамках каждого периода и клиента нумерация начинается сначала.

# Попытка произвести формирование новой таблицы путем запроса SQL:

# SELECT current_client, date, debt,
#   CASE WHEN debt = 1 THEN SUM(debt) OVER (PARTITION BY current_client, debt ORDER BY date) ELSE 0 END AS month_debt
# FROM (
#   SELECT
#     current_client, date, debt
#   FROM table_1
# ) subquery
# ORDER BY current_client, date;

# но данный код не позволяет обновлять счетчик месяцев при нулевой задолженности. Поэтому код был сформирован на python

import sqlite3
from typing import Tuple


def create_database(name: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Функция для создания и/или открытия БД"""
    connection = sqlite3.connect(name)
    cursor = connection.cursor()
    return connection, cursor


def find_debt(clients_info: list) -> None:

    """Функция для поиска количества задолженностей клиентов"""
    debt_counter = 0  # Счетчик месяцев с задолженностью
    previous_client = 0  # Номер предыдущего клиента

    # Перебираем записи о клиентах
    for current_client, date, debt in clients_info:

        # Если смотрим нового клиента, то обнуляем счетчик
        if previous_client != current_client or debt == 0:
            debt_counter = 0
            previous_client = current_client
        # Если у клиента долг, то обновляем счетчик

        if debt:
            debt_counter += 1

        # Делаем запись в новую таблицу
        cursor.execute(
            """INSERT INTO table_2 (
        client,
        date,
        debt,
        month_debt) VALUES (?, ?, ?, ?)""",
            (current_client, date, debt, debt_counter),
        )
        # print(current_client, date, debt, debt_counter)  # можно протестировать через консоль


if __name__ == "__main__":
    try:
        connection, cursor = create_database("sb")

        # Создаем новую таблицу
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS table_2 (
        client INTEGER,
        date DATE,
        debt INTEGER,
        month_debt INTEGER)"""
        )

        # Забираем все из таблицы с клиентами и ищем их долги
        cursor.execute("SELECT client, date, debt FROM table_1")
        find_debt(clients_info=cursor.fetchall())

        # Фиксируем изменения в бд если всё прошло успешно
        connection.commit()
    finally:
        # Иначе закрываем соединение
        connection.close()