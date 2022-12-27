import pandas as pd
import numpy as np
import pdfkit
from task_3_3_2 import create_vacancies
from jinja2 import Environment, FileSystemLoader


def get_params():
    file_name = input('Введите название файла: ')
    vac_name = input('Введите название профессии: ')
    return file_name, vac_name


def mean_to_number(numb):
    if numb == np.NAN:
        return 0
    else:
        return int(numb)


def report_pdf(data_list, job_name):
    salary_key = list(data_list[4])
    vacs_key = list(data_list[5])
    vacs_by_cities = [str('{0:.2%}'.format(float(x))).replace('.', ',') for x in list(data_list[5].values())]
    heads1 = ['Год', 'Средняя зарплата', f'Средняя зарплата - {job_name}', 'Количество вакансий',
              f'Количество вакансий - {job_name}']
    heads2 = ['Город', 'Уровень зарплат', 'Город', 'Доля вакансий']
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("pdf_template_pandas.html")
    pdf_template = template.render({'heads1': heads1, 'job': job_name,
                                    'salary_by_years': data_list[0],
                                    'job_salary_by_years': data_list[2],
                                    'vacs_by_years': data_list[1],
                                    'job_count_by_years': data_list[3],
                                    'heads2': heads2, 'salary_key': salary_key, 'vacs_key': vacs_key,
                                    'salary_by_cities': data_list[4],
                                    'vacs_by_cities': vacs_by_cities})

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdfkit.from_string(pdf_template, 'report_new.pdf', configuration=config, options={'enable-local-file-access': None})


def create_report():
    file_name, job_name = get_params()
    create_vacancies(file_name)
    pd.set_option('expand_frame_repr', False)
    print('Подгрузка файла вакансии')
    df = pd.read_csv('vacancies_new.csv')
    df['published_at'] = df['published_at'].apply(lambda x: x[:4])
    years = df['published_at'].unique()

    salary_by_years = {year: [] for year in years}
    vacs_by_years = {year: 0 for year in years}
    job_salary_by_years = {year: [] for year in years}
    job_count_by_years = {year: 0 for year in years}

    for year in years:
        year_df = df[df['published_at'] == year]
        salary_by_years[year] = int(year_df['salary'].mean())
        vacs_by_years[year] = len(year_df)
        job_salary_by_years[year] = mean_to_number(year_df[year_df['name'].str.contains(job_name)]['salary'].mean())
        job_count_by_years[year] = len(year_df[year_df['name'].str.contains(job_name)])

    print('Создание первых четырех словарей')

    area = df['area_name'].value_counts().to_dict()
    area = dict(sorted(area.items(), key=lambda x: x[1], reverse=True))
    vacs_sum = len(df)
    result_city = [city for city in area.keys() if area[city] / vacs_sum > 0.01]
    salary_by_cities = {}
    vacs_by_cities = {}

    for i in range(10):
        city = result_city[i]
        salary_by_cities[city] = mean_to_number(df[df['area_name'] == city]['salary'].mean())
        vacs_by_cities[city] = round((len(df[df['area_name'] == city]) / vacs_sum), 4)

    print('Динамика уровня зарплат по годам:', salary_by_years)
    print('Динамика количества вакансий по годам:', vacs_by_years)
    print('Динамика уровня зарплат по годам для выбранной профессии:', job_salary_by_years)
    print('Динамика количества вакансий по годам для выбранной профессии:', job_count_by_years)
    print('Уровень зарплат по городам (в порядке убывания):', salary_by_cities)
    print('Доля вакансий по городам (в порядке убывания):', vacs_by_cities)

    data_list = [salary_by_years, vacs_by_years, job_salary_by_years, job_count_by_years, salary_by_cities,
                 vacs_by_cities]
    report_pdf(data_list, job_name)


if __name__ == '__main__':
    create_report()
