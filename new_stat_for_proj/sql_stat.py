import sqlite3

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)
conn = sqlite3.connect('vacancy_db')
cursor = conn.cursor()
salary_by_year = pd.read_sql("""select STRFTIME('%Y', date || '-01') AS 'year',
            round(avg(salary)) as avg_salary 
                        from vacancies
                        group by year""", conn)
count_by_year = pd.read_sql("""select STRFTIME('%Y', date || '-01') AS 'year',
                count(salary) as count
                        from vacancies
                        group by year """, conn)

count_by_year_with_vac = pd.read_sql("""select STRFTIME('%Y', date || '-01') AS 'year',
                count(salary) as count
                        from vacs_with_prof
                        group by year """, conn)

salary_by_year_with_vac = pd.read_sql("""select STRFTIME('%Y', date || '-01') AS 'year',
            round(avg(salary)) as avg_salary 
                        from vacs_with_prof
                        group by year""", conn)

salary_by_city = pd.read_sql("""select area_name, avg from
                        (select area_name, round(avg(salary)) as avg,
                         count(salary) as count
                        from vacancies
                        group by area_name
                        order by avg desc)
                    where count > (select count(*) from vacancies) * 0.01
                    limit 10""", conn)

count_by_city = pd.read_sql("""select area_name,
                        round(cast(count as real) / (select count(*) from vacancies), 4)
                         as percent from
                        (select area_name, count(salary) as count
                        from vacancies
                        group by area_name
                        order by count desc)
                        limit 10""", conn)


years = salary_by_year['year'].tolist()
# lst = [count_by_year, count_by_city, count_by_year_with_vac, salary_by_year, salary_by_city, salary_by_year_with_vac]
# for data in [salary_by_year, count_by_year, salary_by_year_with_vac, count_by_year_with_vac]:
salary_by_year = salary_by_year.set_index('year')
count_by_year = count_by_year.set_index('year')
salary_by_year_with_vac = salary_by_year_with_vac.set_index('year')
count_by_year_with_vac = count_by_year_with_vac.set_index('year')
# print(salary_by_year.dtypes)
# salary_by_year = salary_by_year[salary_by_year['avg_salary'] < 350000]
# print(salary_by_year[salary_by_year['avg_salary'] > 30000].shape[0])
# df45 = salary_by_year[salary_by_year.loc[2005]]
# print(salary_by_year[salary_by_year['year'] == 2005])
salary_by_year_with_vac = salary_by_year_with_vac.reindex(years)
count_by_year_with_vac = count_by_year_with_vac.reindex(years)
# print(salary_by_year_with_vac.head(10))
df3 = pd.concat([salary_by_year,  salary_by_year_with_vac, count_by_year, count_by_year_with_vac], axis=1,
                ignore_index=True)
df3.rename(columns={"year": 'Год', 0: 'Средняя зарплата, (руб.)', 1: "Средняя зарплата - web разработчик, (руб.)",
                   2: "Количество вакансий", 3: "Количество вакансий - web разработчик"}, inplace=True)
# df = pd.concat([salary_by_year, count_by_year, salary_by_year_with_vac, count_by_year_with_vac])
df2 = pd.concat([salary_by_city, count_by_city], axis=1, ignore_index=True)
df2.rename(columns={0: 'Город', 1: "Уровень зарплат, (руб.)",
                   2: "Город", 3: "Доля вакансий"}, inplace=True)
df3.to_excel('report_new/report1.xlsx', sheet_name='Статистика по годам')
df2.to_excel('report_new/report2.xlsx', sheet_name='Статистика по городам', index=False)
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
x = np.arange(int(salary_by_year.shape[0]))
width = 0.4
ax1.bar(x - width / 2, salary_by_year['avg_salary'].tolist(), width, label='средняя з/п')
ax1.bar(x + width / 2, salary_by_year_with_vac['avg_salary'].tolist(), width, label=f'з/п web разработчик')
ax1.set_title('Уровень зарплат по годам')
plt.sca(ax1)
plt.xticks(x, salary_by_year.index.tolist(), fontsize=10, rotation=90)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(axis='y')
ax1.set_ylim([0, 120000])
ax2.bar(x - width / 2, count_by_year['count'].tolist(), width, label='Количество вакансий')
ax2.bar(x + width / 2, count_by_year_with_vac['count'].tolist(), width, label=f'Количество вакансий web разработчик')
ax2.set_title('Количество вакансий по годам')
ax2.set_ylim([0, 10000])
plt.sca(ax2)
plt.xticks(x, count_by_year.index.tolist(), fontsize=10, rotation=90)

ax2.legend(loc='upper left', fontsize=10)
ax2.grid(axis='y')
fig.set_figheight(5)
fig.set_figwidth(10)
fig.tight_layout()

fig.savefig('report_new/graph1.png')


fig1, (ax3, ax4) = plt.subplots(nrows=1, ncols=2)
cities = salary_by_city['area_name'].tolist()
y_pos = np.arange(len(cities))
ax3.barh(y_pos, salary_by_city['avg'].tolist(), align='center')
plt.sca(ax3)
plt.yticks(y_pos, cities, fontsize=10)
ax3.invert_yaxis()  # labels read top-to-bottom
ax3.set_title('Уровень зарплат по городам')
ax3.grid(axis='x')

x = ['Другие'] + count_by_city['area_name'].tolist()
ax4.set_title('Доля вакансий по городам')
city_percent = count_by_city['percent'].tolist()
city_percent.insert(0, 1 - sum(city_percent))
ax4.pie(city_percent, radius=1, labels=x, textprops={'fontsize': 10})

fig1.tight_layout()
fig1.set_figheight(5)
fig1.set_figwidth(10)
plt.show()
fig1.savefig('report_new/graph2.png')

def generate_image(self):
    """Генерирует изображение в директории report под именем report.png, с 4мя графиками: гистограммами 'Уровень зарплат по годам',
     'Количество вакансий по годам', 'Уровень зарплат по городам' и круговой диаграммой 'Количество вакансий по городам'
      для выбранной профессии, сохраняет сгенерированное изображение в корень проекта с названием grapth.png

    """
    labels = self.salary_by_year.keys()
    vacancy = self.vacancy

    x = np.arange(len(labels))
    width = 0.4
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)

    ax1.bar(x - width / 2, self.salary_by_year.values(), width, label='средняя з/п')
    ax1.bar(x + width / 2, self.salary_by_year_vac.values(), width, label=f'з/п {vacancy[2]}')
    ax1.set_title('Уровень зарплат по годам')
    plt.sca(ax1)
    plt.xticks(x, labels, fontsize=10, rotation=90)

    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(axis='y')

    ax2.bar(x - width / 2, self.count_by_year.values(), width, label='Количество вакансий')
    ax2.bar(x + width / 2, self.count_by_year_vac.values(), width, label=f'Количество вакансий \n{vacancy[2]}')
    ax2.set_title('Количество вакансий по годам')
    plt.sca(ax2)
    plt.xticks(x, labels, fontsize=10, rotation=90)

    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(axis='y')

    cities = self.salary_by_city.keys()
    y_pos = np.arange(len(cities))
    ax3.barh(y_pos, self.salary_by_city.values(), align='center')
    plt.sca(ax3)
    plt.yticks(y_pos, cities, fontsize=10)
    ax3.invert_yaxis()  # labels read top-to-bottom
    ax3.set_title('Уровень зарплат по городам')
    ax3.grid(axis='x')

    x = ['Другие'] + list(self.pers_by_city.keys())
    ax4.set_title('Доля вакансий по городам')
    city_percent = list(self.pers_by_city.values())
    city_percent.insert(0, 1 - sum(city_percent))
    ax4.pie(city_percent, radius=1, labels=x, textprops={'fontsize': 10})

    fig.tight_layout()
    plt.savefig('report/graph.png')