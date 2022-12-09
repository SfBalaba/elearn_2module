import multiprocessing
import os
from cProfile import Profile
from functools import partial
from multiprocessing import Pool
from pstats import Stats

from statistics import get_all_stat, Report
prof = Profile()
prof.disable()

def get_stat(file_name, prof_name):
    salary_by_year, count_by_year,salary_by_year_vac,count_by_year_vac,salary_by_city,pers_by_city = get_all_stat(file_name, prof_name)
    return {"salary_by_year": salary_by_year,
            'count_by_year': count_by_year,
            'salary_by_year_vac': salary_by_year_vac,
            'count_by_year_vac': count_by_year_vac,
            "salary_by_city": salary_by_city,'pers_by_city':pers_by_city}

def update_dict(orig, dicts, by: str):
    for dict in dicts:
        orig.update(dict[by].items())

if __name__ == "__main__":
    prof.enable()
    files = []
    prof.disable()
    csvs_dir = input('Абсолютный путь csv чанков:')
    csvs_dir = "C:\\Users\\anony\Balaba\\csv_by_years" if (csvs_dir == "") else csvs_dir
    prof_name = input('Профессия: ')
    prof_name = "Программист" if (prof_name == "") else prof_name
    prof.enable()
    path_to_csv = os.path.join('.', csvs_dir)
    for file in os.listdir(path_to_csv):
        files.append(os.path.join(path_to_csv, file))
    pool = Pool(multiprocessing.cpu_count() * 3)
    reader = partial(get_stat, prof_name = prof_name)
    output = pool.map(reader, files)
    salary_by_year = {}
    update_dict(salary_by_year, output, 'salary_by_year')
    vacs_by_year = {}
    update_dict(vacs_by_year, output, 'count_by_year')
    prof_salary_by_year = {}
    update_dict(prof_salary_by_year, output, 'salary_by_year_vac')
    prof_vacs_by_year = {}
    update_dict(prof_vacs_by_year, output, 'count_by_year_vac')
    salary_by_city = {}
    update_dict(salary_by_city, output, 'salary_by_city')
    pers_by_city = {}
    update_dict(pers_by_city, output, 'pers_by_city')
    report = Report(salary_by_year=salary_by_year, count_by_year=vacs_by_year,
                    salary_by_year_vac= prof_salary_by_year, count_by_year_vac=prof_vacs_by_year,
                    salary_by_city=salary_by_city, pers_by_city=pers_by_city,  vac=prof_name)
    report.generate_exel()
    report.generate_image()
    report.generate_pdf()
    pool.close()
    prof.disable()


    prof.dump_stats('async')
    with open('async_stats.txt', 'wt') as _output:
        stats = Stats('async', stream=_output)
        stats.sort_stats('cumulative', 'time')
        stats.print_stats()
