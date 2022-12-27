from typing import List, Dict
import pandas as pd
import requests
import concurrent.futures

url = "https://api.hh.ru/vacancies"

def execute_vacancies(vacancies: List[Dict[str, str]] or List[Dict[Dict[str, str], str]]) -> (List[List[str]]):
    if len(vacancies) == 0:
        return []
    else:
        return [
            [
                vacancy["name"],
                vacancy["area"]["name"],
                vacancy["salary"]["from"],
                vacancy["salary"]["to"],
                vacancy["salary"]["currency"],
                vacancy["published_at"],
            ]
            for vacancy in vacancies
            if vacancy["salary"]==True
        ]

def get_vacancies(params: dict) -> (List[Dict[str, str]] or List[Dict[Dict[str, str], str]]):
    return requests.get(url, params).json()["items"]


if __name__ == "__main__":
    pages_count = 20
    params1 = [
        dict(
            specialization=1,
            date_from="2022-12-25T00:00:00",
            date_to="2022-12-25T12:00:00",
            per_page=100,
            page=i,
        )
        for i in range(pages_count)
    ]

    params2 = [
        dict(
            specialization=1,
            date_from="2022-12-25T00:12:00",
            date_to="2022-12-26T00:00:00",
            per_page=100,
            page=i,
        )
        for i in range(pages_count)
    ]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = list(executor.map(get_vacancies, params1 + params2))
        response = list(executor.map(execute_vacancies, result))
        result = pd.concat(
            [
                pd.DataFrame(
                    el,
                    columns=[
                        "name",
                        "salary_from",
                        "salary_to",
                        "salary_currency",
                        "area_name",
                        "published_at",
                    ],
                )
                for el in response
            ]
        )
    result.to_csv("vacancies_from_hh.csv", index=False)
