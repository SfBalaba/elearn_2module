import pandas as pd
import numpy as np


def create_vacancies(file_name):
    print('Запуск формирования файла по вакансиям')
    pd.set_option('expand_frame_repr', False)

    currency_data = pd.read_csv('currencies.csv')
    currency_data = currency_data.set_index('date')
    print('Подгрузка файла по валютам')
    print(currency_data.head())
    currency = list(currency_data.columns)

    df = pd.read_csv(file_name)
    print('Открытие файла по вакансиям')
    df.salary_from = df[['salary_from', 'salary_to']].mean(axis=1)
    df['date'] = df.published_at.apply(lambda z: z[:7])
    df['salary_from'] = df.apply(
        lambda x: float(x['salary_from'] * currency_data.at[x['date'], x['salary_currency']])
        if (x['salary_currency'] != 'RUR' and not np.isnan(x['salary_from']))
        else x['salary_from'], axis=1)

    df = df.drop(['salary_to', 'date', 'salary_currency'], axis=1).rename(columns={'salary_from': 'salary'})
    df.head(100).to_csv('first100vacancies.csv', index=False)
    # df.to_csv('vacancies_new.csv', index=False)
    print('Создание итогового файла по вакансиям')


if __name__ == '__main__':
    create_vacancies('vacancies_dif_currencies.csv')
