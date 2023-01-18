choice = input("Выберите вывод данных(Статистика или Вакансии)")
if(choice =="Статистика"):
    import statistics
if(choice == "Вакансии"):
    import table
else:
    print('Некорректный ввод')
#changes from main'

from statistics import get_all_stat
get_all_stat('vacancies_with_skills.csv', 'ios')