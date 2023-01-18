import json
from typing import List, Dict
import pandas as pd
import requests
import concurrent.futures

url = "https://api.hh.ru/vacancies"

def execute_vacancies(vacancies: List[Dict[str, str]] or List[Dict[Dict[str, str], str]]) -> (List[List[str]]):
    """ формирует дату для создания итогового датафрейма
    оставляет только нужные поля: название, город, вилка оклада, дата публиукации вакансии

    Args:
        vacancies: список словарей выгруженных api содержащие информацию по вакасии

    Returns: список вакансий c зарплатами

    """
    return [
        [
            vacancy['id'],
            vacancy["name"],
            vacancy["employer"]["name"],
            vacancy["salary"]["from"],
            vacancy["salary"]["to"],
            vacancy["salary"]["currency"],
            vacancy["area"]["name"],
            vacancy["published_at"],
        ]
        for vacancy in vacancies
        if vacancy["salary"]
    ]

def get_vacancies_items(params: dict) -> (List[Dict[str, str]] or List[Dict[Dict[str, str], str]]):
    """ поулчает json данные о вакансии по заданынм параметрам

    Args:
        params: параметры для запроса

    Returns: данные по вакансиям

    """
    return requests.get(url, params).json()["items"]





if __name__ == "__main__":
    pd.set_option('expand_frame_repr', False)
    params = dict(
            specialization=1,
            date_from="2022-12-26T00:00:00",
            date_to="2022-12-26T12:00:00",
            per_page=30,
            page=1,
        )
    res = requests.get(url, params).json()['items']
    res = execute_vacancies(res)
    for i, el in enumerate(res):
        new_get = requests.get(f"https://api.hh.ru/vacancies/{el[0]}").json()
        el.pop(0)

        el.append(new_get['description'])
        if(len(new_get['key_skills']) != 0):
            el.append(", ".join([x['name'] for x in new_get['key_skills']]))
        else:
            res.pop(i)
    res= [x for x in res if len(x)==9]
    df = pd.DataFrame(
                res,
                columns=[
                    "Название вакансии",

                    "Компания",

                    "salary_from",
                    "salary_to",
                    "salary_currency",
                    "Название региона",
                    "Дата публикации вакансии",
                    "Описание",
                    "Навыки",
                ],
            )
    df["Дата публикации вакансии"] = df["Дата публикации вакансии"].apply(lambda x: x[:10])
    df['Оклад'] = df['salary_from'] + df["salary_to"] / 2
    df.loc[df["salary_to"].isna(), ['Оклад']] = df["salary_from"]
    df = df.loc[df['salary_currency'] == 'RUR']

    df = df.drop(["salary_from", "salary_to"], axis=1)
    json_records =df.reset_index().to_json(orient='records')
    data = []
    data = json.loads(json_records)
    var1 = data
    var = df["Описание"].tolist()
    print()
    print(df.head(10))

