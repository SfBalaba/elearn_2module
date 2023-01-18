import pandas as pd
import sqlite3 as sql
import re


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
pd.set_option('expand_frame_repr', False)

df = pd.read_csv('vacancies_with_skills.csv', low_memory=False)

# df = df.dropna(subset=['name', 'key_skills', 'salary_currency',  'area_name', 'published_at']) \
#     .dropna(subset=['salary_from', 'salary_to'], how='all').reset_index(drop=True)
con = sql.connect('vacancy_db')
cur = con.cursor()
pd.set_option
df = df.dropna(subset=['salary_from', 'salary_to'], how='all').reset_index(drop=True)
df['date'] = df['published_at'].str[:7]


df['salary'] = df[['salary_from', 'salary_to']].mean(axis=1)
df['salary'] = df.apply(axis=1, func=apply_to_currency)
# print(df[df['date']=='2005-12'].head(10))
df = df[['name', 'key_skills', 'salary', 'area_name', 'date']]
df = df.dropna(subset=['name',  'salary', 'area_name', 'date']).reset_index(drop=True)
vacancy_name = ['web develop', 'веб разработчик', 'web разработчик', 'web programmer', 'web программист',
                'веб программист', 'битрикс разработчик', 'bitrix разработчик', 'drupal разработчик', 'cms разработчик',
                'wordpress разработчик', 'wp разработчик', 'joomla разработчик', 'drupal developer', 'cms developer',
                'wordpress developer', 'wp developer', 'joomla developer']
flag = True
for vac in vacancy_name:
    if(flag):
        df2 = df[df['name'].str.contains(vac, flags=re.IGNORECASE,
                                                 regex=True)]
    else:
        new = df[df['name'].str.contains(vac, flags=re.IGNORECASE,
                                                 regex=True)]
        print(new.shape[0])
        df2 = pd.concat([df2, new], axis=0, ignore_index=True)
        print(df2.shape[0])
    flag = False

print(df2.shape[0])
# print(df[df['date']=='2005-12'].head(10))
# years = df2[df2['date']][:4].unique
# print(df2[df2['date']=='2010-12'].head(10))
df2.to_sql('vacs_with_prof', con=con, index=True, if_exists='append')
# df2.to_sql('skills_with_vac', con=con, index=True, if_exists='append')