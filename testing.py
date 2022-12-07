from unittest import TestCase, main
from statistics import Salary, DataSet


class SalaryTest(TestCase):
    def checkTypeSalary(self):
        self.assertEqual(type(Salary(10, 20, 'RUB')).__name__, 'Salary')

    def test_salary_to(self):
        self.assertEqual(Salary(20000, 40000, 'RUR').salary_to, 40000)

    def test_salary_from(self):
        self.assertEqual(Salary(20000, 40000, 'RUR').salary_from, 20000)

    def test_salary_currency(self):
        self.assertEqual(Salary(20000, 40000, 'RUR').salary_currency, 'RUR')

    def test_salary_to_RUB_eur(self):
        self.assertEqual(Salary(1000, 5000, 'EUR').convert_to_RUB(), 179700.0)

    def test_salary_to_RUB_rub(self):
        self.assertEqual(Salary(1000, 5000, 'RUR').convert_to_RUB(), 3000.0)

    def test_salary_to_RUB_kgs(self):
        self.assertEqual(Salary(1000, 5000, 'KGS').convert_to_RUB(), 2280.0)


class DataSetTest(TestCase):
    data = DataSet('test.csv')
    header = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']

    def test_csv_filer_empty_reader(self):
        reader = [[]]
        self.assertEqual(self.data.csv_filer(self.header, reader), [])

    def test_scv_filer_counts_of_fields_not_equal(self):
        reader = [['Веб-программист','30000.0','RUR','Москва','2007-12-04T15:06:07+0300']]
        self.assertEqual(self.data.csv_filer(self.header, reader), [])

    def test_scv_filer_have_empty_field(self):
        reader = [['Веб-программист', '30000.0', '', 'RUR', 'Москва', '2007-12-04T15:06:07+0300']]
        self.assertEqual(self.data.csv_filer(self.header, reader), [])

    def test_csv_filer_valid_reader(self):
        reader1 = [['<strong>Программист 1С (8.0)/Разработчик</strong>', '65000.0', '75000.0', 'RUR', 'Москва',
                    '2007-12-04T16:28:52+0300']]
        self.assertEqual(self.data.csv_filer(self.header, reader1), [{'name': 'Программист 1С (8.0)/Разработчик',
                                                           'salary_from': '65000.0', 'salary_to': '75000.0',
                                                           'salary_currency': 'RUR', 'area_name': 'Москва',
                                                           'published_at': '2007-12-04T16:28:52+0300'}])


if __name__ == '__main__':
    main()