import pandas as pd
import sqlite3

def createSqlFromCSV(file_name: str) -> None:
    """
    Создаёт таблицу currencies базы данных currencies.db из CSV-файла
    :param file_name: название файла csv из  корня проекта
    :return: None
    """
    df = pd.read_csv(file_name)
    conn = sqlite3.connect('vacancy_db')
    cursor = conn.cursor()
    # cursor.execute("""drop table currencies""")
    cursor.execute('CREATE TABLE currencies (date text, RUR number, USD number, KZT number, BYR number,'
              'UAH number, EUR number)')
    conn.commit()
    df.to_sql('currencies', conn, if_exists='replace', index=False)
    conn.close()

createSqlFromCSV('currencies.csv')