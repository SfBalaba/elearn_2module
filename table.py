import os, re, csv
import datetime
from typing import Dict, List, Tuple
from prettytable import PrettyTable, ALL


class DataSet:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.vacancies_objects = [Vacancy(vac) for vac in self.csv_filer(*self.csv_reader(file_name))]

    def clean_string(self, raw: str) -> str:
        clean_string = re.sub('<.*?>', '', raw)
        return clean_string if '\n' in raw else " ".join(clean_string.split())

    def csv_reader(self, file_name: str) -> Tuple[List[str], List[List[str]]]:
        reader = csv.reader(open(file_name, encoding='utf_8_sig'))
        data_base = [line for line in reader]
        fields = data_base[0]
        vacancies = data_base[1:]
        return fields, vacancies

    def csv_filer(self, fields: List[str], vacancies_list: List[List[str]]) -> List[Dict[str, str]]:
        filtered_vacancies = list(filter(lambda vac: (len(vac) == len(fields) and vac.count('') == 0), vacancies_list))
        dict_vacans = [dict(zip(fields, map(self.clean_string, vac))) for vac in filtered_vacancies]
        if (len(dict_vacans) == 0):
            print('Нет данных')
            exit()
        else:
            return dict_vacans


class Vacancy:
    def __init__(self, vac: Dict[str, str]):
        self.name = vac['name']
        self.description = vac['description']
        self.key_skills = vac['key_skills'].split('\n')
        self.experience_id = vac['experience_id']
        self.premium = vac['premium']
        self.employer_name = vac['employer_name']
        self.salary = Salary(vac['salary_from'], vac['salary_to'], vac['salary_gross'], vac['salary_currency'])
        self.area_name = vac['area_name']
        self.published_at = vac['published_at']


dict_currency_to_rub = {"AZN": 35.68,
                        "BYR": 23.91,
                        "EUR": 59.90,
                        "GEL": 21.74,
                        "KGS": 0.76,
                        "KZT": 0.13,
                        "RUR": 1,
                        "UAH": 1.64,
                        "USD": 60.66,
                        "UZS": 0.0055, }


class Salary:
    def __init__(self, salary_from: str, salary_to: str, salary_gross: str, salary_currency: str):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency


translation = {"name": "Название",
               "description": "Описание",
               "key_skills": "Навыки",
               "experience_id": "Опыт работы",
               "premium": "Премиум-вакансия",
               "employer_name": "Компания",
               "salary_from": "Нижняя граница вилки оклада",
               "salary_to": "Верхняя граница вилки оклада",
               "salary_gross": "Оклад указан до вычета налогов",
               "salary_currency": "Идентификатор валюты оклада",
               "area_name": "Название региона",
               "published_at": "Дата публикации вакансии",
               "Оклад": "Оклад",
               "True": "Да",
               "TRUE": "Да",
               "False": "Нет",
               "FALSE": "Нет",
               "noExperience": "Нет опыта",
               "between1And3": "От 1 года до 3 лет",
               "between3And6": "От 3 до 6 лет",
               "moreThan6": "Более 6 лет",
               "AZN": "Манаты",
               "BYR": "Белорусские рубли",
               "EUR": "Евро",
               "GEL": "Грузинский лари",
               "KGS": "Киргизский сом",
               "KZT": "Тенге",
               "RUR": "Рубли",
               "UAH": "Гривны",
               "USD": "Доллары",
               "UZS": "Узбекский сум"}

rang_experience_id = {"noExperience": 0,
                      "between1And3": 1,
                      "between3And6": 2,
                      "moreThan6": 3}

reverse_translation = {"Название": "name",
                       "Описание": "description",
                       "Навыки": "key_skills",
                       "Опыт работы": "experience_id",
                       "Премиум-вакансия": "premium",
                       "Компания": "employer_name",
                       "Идентификатор валюты оклада": "salary_currency",
                       "Название региона": "area_name",
                       "Дата публикации вакансии": "published_at"}


class InputConect:
    def __init__(self, data_set, parameter, sorting_param, is_reverse, interval, columns):
        self.param = parameter
        self.DataSet = data_set
        self.sorting_param = sorting_param
        self.is_reverse = is_reverse
        self.interval = interval
        self.columns = columns

    def formatter(self, row):
        result = {}
        salary_list = []

        def check_need_translate(key):
            result[key] = translation[getattr(row, key)]

        def check_last_salary_field(salary):
            salary_list.append(salary.salary_from)
            salary_list.append(getattr(salary, 'salary_to'))
            salary_list.append(getattr(salary, 'salary_currency'))
            salary_list[0] = int(float(getattr(salary, 'salary_from')))
            salary_list[1] = int(float(getattr(salary, 'salary_to')))
            if salary_list[0] > 1000:
                salary_list[0] = f'{int(float(salary_list[0])) // 1000} {str(int(float(salary_list[0])))[-3:]}'
                salary_list[1] = f'{int(float(salary_list[1])) // 1000} {str(int(float(salary_list[1])))[-3:]}'
            salary_list[2] = 'Без вычета налогов' if translation[
                                                         getattr(salary,
                                                                 'salary_gross')] == 'Да' else 'С вычетом налогов'
            result[
                'Оклад'] = f'{salary_list[0]} - {salary_list[1]} ({translation[getattr(salary, "salary_currency")]}) ({salary_list[2]})'

        def check_data(key):
            result[key] = datetime.datetime.strptime(getattr(row, key), '%Y-%m-%dT%H:%M:%S%z').strftime(
                '%d.%m.%Y')

        def check_else_fields(key):
            result[key] = getattr(row, key)

        checks = list(translation.keys())
        funcs = [check_else_fields, check_else_fields, check_else_fields, check_need_translate,
                 check_need_translate, check_else_fields, check_last_salary_field, check_else_fields, check_data]
        for key in row.__dict__.keys():
            for i, func in enumerate(funcs):
                if key == 'salary':
                    check_last_salary_field(getattr(row, 'salary'))
                if key == 'area_name':
                    check_else_fields(key)
                if key == 'published_at':
                    check_data(key)
                if key == checks[i]:
                    func(key)
                    break
        return result

    data_filter_dict = {
        'Навыки': lambda data_vacancies, par_value: [vac for vac in data_vacancies if
                                                     (set(par_value.split(', '))).issubset(
                                                         vac.key_skills)],
        'Оклад': lambda data_vacancies, par_value: [vac for vac in data_vacancies if
                                                    float(vac.salary.salary_from) <= int(par_value) <= float(
                                                        vac.salary.salary_to)],
        'Опыт работы': lambda data_vacancies, par_value: [vac for vac in data_vacancies
                                                          if par_value == translation[vac.experience_id]],
        'Идентификатор валюты оклада': lambda data_vacancies, par_value: [vac for vac in data_vacancies
                                                                          if
                                                                          par_value == translation[
                                                                              vac.salary.salary_currency]],
        'Премиум-вакансия': lambda data_vacancies, par_value: [vac for vac in data_vacancies
                                                               if par_value == translation[vac.premium]],
        'Дата публикации вакансии': lambda data_vacancies, par_value: [vac for vac in data_vacancies
                                                                       if par_value == datetime.datetime.strptime(
                vac.published_at, '%Y-%m-%dT%H:%M:%S%z').strftime(
                '%d.%m.%Y')],

        'Название': lambda data_vacancies, par_value: [vac for vac in data_vacancies if par_value == vac.name],
        'Название региона': lambda data_vacancies, par_value: [vac for vac in data_vacancies if
                                                               par_value == vac.area_name],
        'Компания': lambda data_vacancies, par_value: [vac for vac in data_vacancies if
                                                       par_value == vac.employer_name],
    }

    data_sort_dict = {
        'Навыки': lambda vac: len(vac.key_skills),
        'Оклад': lambda vac: dict_currency_to_rub[vac.salary.salary_currency] * (float(vac.salary.salary_from)
                                                                                 + float(vac.salary.salary_to)) / 2,
        'Опыт работы': lambda vac: rang_experience_id[vac.experience_id],
        'Дата публикации вакансии': lambda vac: datetime.datetime.strptime(vac.published_at, '%Y-%m-%dT%H:%M:%S%z')
    }

    def data_sort(self) -> list:
        if self.sorting_param in self.data_sort_dict.keys():
            self.DataSet = sorted(self.DataSet, key=self.data_sort_dict[self.sorting_param],
                                  reverse=self.is_reverse)
            return sorted(self.DataSet, key=self.data_sort_dict[self.sorting_param],
                          reverse=self.is_reverse)
        else:
            self.DataSet = sorted(self.DataSet, key=lambda vac: getattr(vac, reverse_translation[self.sorting_param]),
                                  reverse=self.is_reverse)
            return sorted(self.DataSet, key=lambda vac: getattr(vac, reverse_translation[self.sorting_param]),
                          reverse=self.is_reverse)

    def edit_date(func):
        def wrap(self):
            self.DataSet = self.DataSet if len(parameter) != 2 else self.data_filter_dict[parameter[0]](self.DataSet,
                                                                                                        parameter[1])
            # data_vacancies = data_vacancies if len(parameter) != 2 else data_filter(data_vacancies, parameter)
            self.DataSet = self.DataSet if len(self.DataSet) != 0 else 'Ничего не найдено'
            if type(self.DataSet) is str:
                print(self.DataSet)
                return
            self.DataSet = self.DataSet if len(self.sorting_param) == 0 else self.data_sort()
            data = self.DataSet
            func(self)

        return wrap

    @edit_date
    def print_vacancies(self):
        head = self.formatter(self.DataSet[0])
        table_header = list(map(lambda head: translation[head], self.formatter(self.DataSet[0]).keys()))
        table_header.insert(0, '№')
        vacans_table = PrettyTable(table_header)
        vacans_table.hrules = ALL
        for i in range(len(self.DataSet)):
            vac = list(self.formatter(self.DataSet[i]).values())
            vac[2] = '\n'.join(vac[2])
            vac = list(map(lambda i: f'{"".join(i)[:100]}...' if len(i) > 100 else i, vac))
            vac.insert(0, i + 1)
            vacans_table.add_row(vac)
        vacans_table.align = 'l'
        vacans_table.max_width = 20
        self.interval.append(len(self.DataSet) + 1)
        if len(interval) > 1 and len(columns) >= 2:
            vacans_table = vacans_table.get_string(start=interval[0] - 1, end=interval[1] - 1, fields=columns)
        elif len(interval) > 1:
            vacans_table = vacans_table.get_string(start=interval[0] - 1, end=interval[1] - 1)
        elif len(columns) >= 2:
            vacans_table = vacans_table.get_string(fields=columns)

        print(vacans_table)


def exit_from_file(message):
    print(message)
    exit()


file_name = input('Введите название файла: ')
parameter = input('Введите параметр фильтрации: ')
sorting_param = input('Введите параметр сортировки: ')
is_reversed_sort = input('Обратный порядок сортировки (Да / Нет): ')
interval = list(map(int, input('Введите диапазон вывода: ').split()))
columns = input('Введите требуемые столбцы: ')


if os.stat(file_name).st_size == 0:
    exit_from_file('Пустой файл')
if ': ' not in parameter and parameter != '':
    exit_from_file('Формат ввода некорректен')
parameter = parameter.split(': ')
if len(parameter) == 2 and parameter[0] not in list(translation.values()):
    exit_from_file('Параметр поиска некорректен')
if sorting_param != '' and sorting_param not in list(translation.values()):
    exit_from_file('Параметр сортировки некорректен')
if is_reversed_sort not in ['Да', 'Нет', '']:
    exit_from_file('Порядок сортировки задан некорректно')
is_reversed_sort = (is_reversed_sort == 'Да')
if len(columns) != 0:
    columns = columns.split(', ')
    columns.insert(0, '№')

ds = DataSet(file_name)
inpt = InputConect(ds.vacancies_objects, parameter=parameter,
                   interval=interval,
                   sorting_param=sorting_param,
                   is_reverse=is_reversed_sort,
                   columns=columns)
inpt.print_vacancies()
