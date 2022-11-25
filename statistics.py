import csv, re, os, datetime
from typing import List, Dict, Tuple, Any

import matplotlib
import openpyxl
from openpyxl.styles import Font, Border, Side, Alignment
from openpyxl.styles.numbers import FORMAT_PERCENTAGE_00
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook

import matplotlib.pyplot as plt
import numpy as np
from xlsx2html import xlsx2html

from jinja2 import Environment, FileSystemLoader
import pdfkit

currency_to_rub = {"AZN": 35.68,
                   "BYR": 23.91,
                   "EUR": 59.90,
                   "GEL": 21.74,
                   "KGS": 0.76,
                   "KZT": 0.13,
                   "RUR": 1,
                   "UAH": 1.64,
                   "USD": 60.66,
                   "UZS": 0.0055, }


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = [Vacancy(vac) for vac in self.csv_filer(*self.csv_reader(file_name))]

    def clean_string(self, raw_html):
        result = re.sub("<.*?>", '', raw_html)
        return result if '\n' in raw_html else " ".join(result.split())

    def csv_reader(self, file_name: str) -> (list, list):
        reader = csv.reader(open(file_name, encoding='utf_8_sig'))
        data_base = [line for line in reader]
        return data_base[0], data_base[1:]

    def csv_filer(self, list_naming: list, reader: list) -> list:
        new_vacans_list = list(filter(lambda vac: (len(vac) == len(list_naming) and vac.count('') == 0), reader))
        dict_vacans = [dict(zip(list_naming, map(self.clean_string, vac))) for vac in new_vacans_list]
        return dict_vacans


class Vacancy:
    def __init__(self, dict_vac):
        self.name = dict_vac['name']
        self.salary = Salary(dict_vac['salary_from'], dict_vac['salary_to'], dict_vac['salary_currency'])
        self.area_name = dict_vac['area_name']
        self.published_at = self.change_data(dict_vac['published_at'])

    def change_data(self, date_vac):
        return int(datetime.datetime.strptime(date_vac, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y'))


class Salary:
    def __init__(self, salary_from, salary_to, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency

    def convert_to_RUB(self, salary: float) -> float:
        return salary * currency_to_rub[self.salary_currency]


def get_dynamic_by_salary(vacancies: List[Vacancy], field: str, filter_name_vacancy: str = ''):
    by_salary = {}
    for vac in vacancies:
        by_salary[vac.__getattribute__(field)] = [] if vac.__getattribute__(field) not in by_salary.keys() else \
            by_salary[
                vac.__getattribute__(field)]
    vacancies = vacancies if filter_name_vacancy == '' else list(
        filter(lambda vac: filter_name_vacancy in vac.name, vacancies))
    for vac in vacancies:
        by_salary[vac.__getattribute__(field)].append(
            vac.salary.convert_to_RUB(float(vac.salary.salary_from) + float(vac.salary.salary_to)) / 2)
    for key in by_salary.keys():
        by_salary[key] = 0 if len(by_salary[key]) == 0 else int(sum(by_salary[key]) // len(by_salary[key]))
    return by_salary


def get_dynamic_by_count(vacancies: List[Vacancy], field: str, filter_name_vacancy: str = ''):
    by_count = {}
    for vac in vacancies:
        by_count[vac.__getattribute__(field)] = 0 if vac.__getattribute__(field) not in by_count.keys() else by_count[
            vac.__getattribute__(field)]
    vacancies = vacancies if filter_name_vacancy == '' else list(
        filter(lambda vac: filter_name_vacancy in vac.name, vacancies))
    for vac in vacancies:
        by_count[vac.__getattribute__(field)] += 1
    if field == 'area_name':
        for key in by_count.keys():
            by_count[key] = round(by_count[key] / len(data.vacancies_objects), 4)
    return by_count


def exit_from_file(message):
    print(message)
    exit()


class report():
    def __init__(self, salary_by_year: Dict, salary_by_year_vac: Dict, count_by_year: Dict, count_by_year_vac: Dict,
                 salary_by_city: Dict,
                 pers_by_city: Dict, vac=""):
        self.vacancy = vac
        self.salary_by_year = salary_by_year
        self.salary_by_year_vac = salary_by_year_vac
        self.count_by_year = count_by_year
        self.count_by_year_vac = count_by_year_vac
        self.salary_by_city = salary_by_city
        self.pers_by_city = pers_by_city
        self.pers_by_city_format = self.__to_percent(pers_by_city)
        self.statistics = [salary_by_year, salary_by_year_vac, count_by_year, count_by_year_vac, salary_by_city,
                           self.pers_by_city]

    def __to_percent(self, pers_by_city):
        copy_pers = pers_by_city.copy()
        for key, value in copy_pers.items():
            copy_pers[key] = "{:.2%}".format(value)
        return copy_pers

    # def generate_image(self) -> None:
    #     matplotlib.rc('font', size=8)
    #     labels = self.salary_by_year.keys()
    #     total_salaries = self.salary_by_year.values()
    #     vacancy_salary = self.salary_by_year_vac.values()
    #     total_count = self.count_by_year.values()
    #     vacancy_count = self.count_by_year_vac.values()
    #     cities = list(self.salary_by_city.keys())
    #     cities_salaries = self.salary_by_city.values()
    #     city_percent = list(self.pers_by_city.values())
    #     city_percent.insert(0, 1 - sum(city_percent))
    #
    #     for i in range(len(cities)):
    #         cities[i] = cities[i].replace(' ', '\n')
    #         cities[i] = '-\n'.join(cities[i].split('-')) if cities[i].count('-') != 0 else cities[i]
    #
    #     x = np.arange(len(labels))
    #     width = 0.35
    #     fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)
    #
    #     ax1.bar(x - width / 2, total_salaries, width, label='средняя з/п')
    #     ax1.bar(x + width / 2, vacancy_salary, width, label=f'з/п {self.vacancy}')
    #     ax1.set_title('Уровень зарплат по годам')
    #     plt.sca(ax1)
    #     plt.xticks(x, labels, rotation=90)
    #     ax1.legend(loc='upper left', fontsize=8)
    #     ax1.grid(axis='y')
    #
    #     ax2.bar(x - width / 2, total_count, width, label='Количество вакансий')
    #     ax2.bar(x + width / 2, vacancy_count, width, label=f'Количество вакансий \n{self.vacancy}')
    #     ax2.set_title('Количество вакансий по годам')
    #     plt.sca(ax2)
    #     plt.xticks(x, labels, rotation=90)
    #     ax2.legend(loc='upper left', fontsize=8)
    #     ax2.grid(axis='y')
    #
    #     y_pos = np.arange(len(cities))
    #     ax3.barh(y_pos, cities_salaries, align='center')
    #     plt.sca(ax3)
    #
    #     plt.yticks(y_pos, cities)
    #     # ax3.set_yticks(y_pos, cities)
    #     ax3.invert_yaxis()  # labels read top-to-bottom
    #     ax3.set_title('Уровень зарплат по городам')
    #     ax3.grid(axis='x')
    #
    #     x = ['Другие'] + list(self.pers_by_city.keys())
    #     ax4.set_title('Доля вакансий по городам')
    #     ax4.pie(city_percent, radius=1, labels=x, textprops={'fontsize': 6})
    #
    #     fig.tight_layout()
    #     plt.savefig('graph.png')

    def generate_image(self):
        labels = self.salary_by_year.keys()
        vacancy = self.vacancy

        x = np.arange(len(labels))
        width = 0.4
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)

        ax1.bar(x - width / 2, self.salary_by_year.values(), width, label='средняя з/п')
        ax1.bar(x + width / 2, self.salary_by_year_vac.values(), width, label=f'з/п {vacancy}')
        ax1.set_title('Уровень зарплат по годам')
        plt.sca(ax1)
        plt.xticks(x, labels, fontsize=8, rotation=90)

        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(axis='y')

        ax2.bar(x - width / 2, self.count_by_year.values(), width, label='Количество вакансий')
        ax2.bar(x + width / 2, self.count_by_year_vac.values(), width, label=f'Количество вакансий \n{vacancy}')
        ax2.set_title('Количество вакансий по годам')
        plt.sca(ax2)
        plt.xticks(x, labels, fontsize=8, rotation=90)

        ax2.legend(loc='upper left', fontsize=8)
        ax2.grid(axis='y')

        cities = self.salary_by_city.keys()
        y_pos = np.arange(len(cities))
        ax3.barh(y_pos, self.salary_by_city.values(), align='center')
        plt.sca(ax3)
        plt.yticks(y_pos, cities, fontsize=6)
        ax3.invert_yaxis()  # labels read top-to-bottom
        ax3.set_title('Уровень зарплат по городам')
        ax3.grid(axis='x')

        x = ['Другие'] + list(self.pers_by_city.keys())
        ax4.set_title('Доля вакансий по городам')
        city_percent = list(pers_by_city.values())
        city_percent.insert(0, 1 - sum(city_percent))
        ax4.pie(city_percent, radius=1, labels=x, textprops={'fontsize': 6})

        fig.tight_layout()
        plt.savefig('graph.png')

    def generate_exel(self, list_vacancies: List[Dict]):
        wb = Workbook()
        ws1 = wb.active
        ws1.title = "Статистика по годам"
        ws2 = wb.create_sheet("Статистика по городам")
        data_1 = list_vacancies[:4]
        data_2 = list_vacancies[4:5]
        data_3 = list_vacancies[5:]
        ws1.append(['Год', "Средняя зарплата", f"Средняя зарплата - {self.vacancy}",
                    "Количество вакансий", f"Количество вакансий - {self.vacancy}"])
        ws2.append(["Город", "Уровень зарплат", "", "Город", "Доля зарплат"])
        keys = list(data_1[0].keys())
        self.create_table(ws1, keys, data_1, min_c=1, min_r=2, max_c=5)
        self.create_table(ws2, list(data_2[0].keys()), data_2, min_c=1,
                          min_r=2,
                          max_c=2)
        self.create_table(ws2, list(data_3[0].keys()), data_3, min_c=4, min_r=2,
                          max_c=5)
        self.set_style(wb)
        file_name = os.path.join(os.getcwd(), 'report.xlsx')
        if (isinstance(file_name, str)):
            if (os.path.basename(file_name).endswith(".xlsx")):
                if (os.path.exists(os.path.dirname(file_name))):
                    wb.save(file_name)
                else:
                    raise FileNotFoundError('Такой директории не существует')
            else:
                raise "Невреное расширение файла"
        else:
            raise TypeError('Имя файла должно иметь тип str')

    def create_table(self, ws: openpyxl.worksheet, keys: List, data_table: List[Dict[str,str]], min_c: int, min_r: int,
                     max_c: int):
        for col in ws.iter_cols(min_col=min_c, min_row=min_r, max_col=max_c, max_row=len(keys) + 1):
            for cell in col:
                row_number = cell.row
                if (cell.column == min_c):
                    cell.value = keys[row_number - min_r]
                else:
                    try:
                        current_key = int(ws.cell(row=row_number, column=min_c).value)
                    except ValueError:
                        current_key = ws.cell(row=row_number, column=min_c).value
                    curr_statistic = data_table[cell.column - min_c - 1]
                    cell.value = curr_statistic[current_key]

    def set_style(self, wb: openpyxl.worksheet):
        thins = Side(border_style="thin")
        names = wb.sheetnames
        max_widths = {}
        for name in names:
            curr_ws = wb[name]
            col_width = []
            for col in curr_ws.columns:
                widths = []
                for cell in col:

                    if cell.value != None and cell.value != "":
                        cell.border = Border(top=thins, bottom=thins, left=thins, right=thins)
                        if (cell.row == 1):
                            cell.font = Font(bold=True)
                    widths.append(len(str(cell.value))) if (cell.value != None) else widths.append(0)
                col_width.append(max(widths))
            max_widths[name] = col_width

        for i in range(2, 12):
            wb["Статистика по городам"][f'E{i}'].number_format = FORMAT_PERCENTAGE_00
        for name in names:
            for i in range(wb[name].max_column):
                wb[name].column_dimensions[get_column_letter(i + 1)].width = max_widths[name][i] + 1.22

    def generate_pdf(self) -> None:
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")

        out1 = xlsx2html('report.xlsx', sheet='Статистика по годам')
        out1.seek(0)
        code1 = out1.read()
        out2 = xlsx2html('report.xlsx', sheet='Статистика по городам')
        out2.seek(0)
        code2 = out2.read()

        pdf_template = template.render({'name_vacancy': self.vacancy, 'table1': code1, 'table2': code2})

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config,
                           options={"enable-local-file-access": ""})


def print_statistic(result_list, index, message, is_reversed=False, slice=0):
    slice = len(result_list) if slice == 0 else slice
    statistic = dict(sorted(result_list, key=lambda x: x[index], reverse=is_reversed)[:slice])
    print(message + str(statistic))
    return statistic


def get_statistic(result_list, index: int, is_reversed=False, slice=0):
    slice = len(result_list) if slice == 0 else slice
    statistic = dict(sorted(result_list, key=lambda x: x[index], reverse=is_reversed)[:slice])
    return statistic


file_name = input('Введите название файла: ')
vacancy_name = input('Введите название профессии: ')
if os.stat(file_name).st_size == 0:
    exit_from_file('Пустой файл')
data = DataSet(file_name)
if len(data.vacancies_objects) == 0:
    exit_from_file('Нет данных')
dict_cities = {}
for vac in data.vacancies_objects:
    if vac.area_name not in dict_cities.keys():
        dict_cities[vac.area_name] = 0
    dict_cities[vac.area_name] += 1
needed_vacancies_objects = list(
    filter(lambda vac: int(len(data.vacancies_objects) * 0.01) <= dict_cities[vac.area_name], data.vacancies_objects))

print_statistic(get_dynamic_by_salary(data.vacancies_objects, 'published_at').items(), 0,
                'Динамика уровня зарплат по годам: ')
print_statistic(get_dynamic_by_count(data.vacancies_objects, "published_at").items(), 0,
                'Динамика количества вакансий по годам: ')
print_statistic(get_dynamic_by_salary(data.vacancies_objects, 'published_at', vacancy_name).items(), 0,
                'Динамика уровня зарплат по годам для выбранной профессии: ')
print_statistic(get_dynamic_by_count(data.vacancies_objects, 'published_at', vacancy_name).items(), 0,
                'Динамика количества вакансий по годам для выбранной профессии: ')
print_statistic(get_dynamic_by_salary(needed_vacancies_objects, 'area_name').items(), 1,
                'Уровень зарплат по городам (в порядке убывания): ', True, 10)
print_statistic(get_dynamic_by_count(needed_vacancies_objects, 'area_name').items(), 1,
                'Доля вакансий по городам (в порядке убывания): ', True, 10)

salary_by_year = get_statistic(get_dynamic_by_salary(data.vacancies_objects, 'published_at').items(), 0)
count_by_year = get_statistic(get_dynamic_by_count(data.vacancies_objects, "published_at").items(), 0)
salary_by_year_vac = get_statistic(
    get_dynamic_by_salary(data.vacancies_objects, 'published_at', vacancy_name).items(), 0)
count_by_year_vac = get_statistic(get_dynamic_by_count(data.vacancies_objects, 'published_at', vacancy_name).items(),
                                  0)
salary_by_city = get_statistic(get_dynamic_by_salary(needed_vacancies_objects, 'area_name').items(), 1, False,
                               slice=10)
pers_by_city = get_statistic(get_dynamic_by_count(needed_vacancies_objects, 'area_name').items(), 1, True, slice=10)

report = report(salary_by_year=salary_by_year,
                salary_by_year_vac=salary_by_year_vac,
                count_by_year=count_by_year,
                count_by_year_vac=count_by_year_vac,
                salary_by_city=salary_by_city,
                pers_by_city=pers_by_city,

                vac=vacancy_name)

report.generate_exel(report.statistics)
report.generate_image()
report.generate_pdf()
