choice = input("Выберите вывод данных(Статистика или Вакансии)")
if(choice =="Статистика"):
    import statistics
if(choice == "Вакансии"):
    import table
else:
    print('Некорректный ввод')
#changes from main'