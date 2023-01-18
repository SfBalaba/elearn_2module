import sqlite3
from itertools import islice

from matplotlib import pyplot as plt
from openpyxl import Workbook
import csv
import pandas as pd
def iterate_rows(df2):
    count = {}
    for index, row in df2.iterrows():
        res = row['key_skills']
        list_skills = res.split('\n')
        for item in list_skills:
            if(item not in count.keys()):
                count[item] = 1
            else:
                count[item] +=1
    count = sorted(count.items(), key=lambda item: item[1], reverse=True)[:10]
    count = [i[0] for i in count]
    return count

def get_all_skills(df2):
    all_count = df2.shape[0]
    count = {}
    for index, row in df2.iterrows():
        res = row['key_skills']
        list_skills = res.split('\n')
        for item in list_skills:
            if(item not in count.keys()):
                count[item] = 1
            else:
                count[item] +=1

    for key, value in count.copy().items():
        count[key] = round(value/all_count, 4)

    return count
con = sqlite3.connect('vacancy_db')
cur = con.cursor()
df = pd.read_sql("""select * from vacs_with_prof""", con)
df = df[df['key_skills'].notna()]

df['date'] = df['date'].apply(lambda x: x[:4])
data = get_all_skills(df)
years = df['date'].unique()
counts = {}
for year in years:
    new = df.loc[df['date'] == year, ['key_skills', 'date']]
    counts[year] = iterate_rows(new)
print(counts)
def take(n, iterable):
    return list(islice(iterable, n))

def generate_img(count):
    count = sorted(count.items(), key=lambda item: item[1], reverse=True)
    other = sum([i[1] for i in count[25:]])
    count = count[:25]
    x = [i[0] for i in count]
    x.insert(0, 'Другие')
    fig, ax = plt.subplots()
    # x = list(count.keys())
    ax.set_title('Самые высокочатотные навыки', fontsize=20)
    percent = [i[1] for i in count]
    percent.insert(0, other)
    ax.pie(percent, radius=1, labels=x, textprops={'fontsize': 10})
    plt.savefig('report_new/graph3.png')


def create_xl():
    wb= Workbook()
    ws = wb.create_sheet("Навыки", 0)
    data = [[], [], [], [],[],[],[],[],[],[],[]]
    data[0] = [y for y in years]
    data[0].insert(0, "")
    for i in range(1, 10):
        for year in years:
            data[i].append(counts[year][i])
        data[i].insert(0, str(i))
    for row in data:
        ws.append(row)
    wb.save('report_new/skills_stat_new.xlsx')

create_xl()
generate_img(data)
