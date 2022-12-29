import pandas as pd
import sqlite3 as sql


def apply_to_currency(row: pd.Series) -> int or None:
    """ конверсирует salary в рубли по актуальному курсу(на момент публикации) из таблицы currencies

    Args:
        row: строка DataFrame

    Returns: заначение salary в рублях

    """
    if row['salary_currency'] == 'RUR':
        return round(row['salary'])
    cur.execute(f"""SELECT * FROM currencies WHERE DATE = '{row['date']}'""")
    valutes = dict(zip([col[0] for col in cur.description], cur.fetchone()))
    if row['salary_currency'] not in valutes or valutes[row['salary_currency']] is None:
        return None
    return round(row['salary'] * valutes[row['salary_currency']])


df = pd.read_csv('vacancies_dif_currencies.csv')
df = df.dropna(subset=['name', 'salary_currency', 'area_name', 'published_at']) \
    .dropna(subset=['salary_from', 'salary_to'], how='all').reset_index(drop=True)
con = sql.connect('vacancy_db')
cur = con.cursor()

df['date'] = df['published_at'].str[:7]
df['salary'] = df[['salary_from', 'salary_to']].mean(axis=1)
df['salary'] = df.apply(axis=1, func=apply_to_currency)
df = df[['name', 'salary', 'area_name', 'date']].dropna()
df.to_sql('vacancies', con=con, index=True, if_exists='append')