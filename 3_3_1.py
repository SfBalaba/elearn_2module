import numpy as np
import pandas as pd
# from report_out_old import formatter_date


def split_data(file_name):
    pd.set_option('expand_frame_repr', False)
    df = pd.read_csv(file_name)
    years = df['date'].unique()
    years = sorted(set([year[:4] for year in years]))
    for year in years:
        data = df[df['date'].str.contains(year)]
        data.to_csv(rf'new_csv_files\part_{year}.csv', index=False)


# cont = True
# if not cont:
#     split_data('Currency_data.csv')
#     print('Данные разделены')
#     exit()

pd.set_option('expand_frame_repr', False)
df = pd.read_csv('vacancies_dif_currencies.csv')
df.info()
print(df.head(10))
df_currency = df.groupby('salary_currency')['name'].agg(['count'])
df_currency.reset_index(inplace=True)
df_currency = df_currency.sort_values('count', ascending=False)
print()
print(df_currency)

currency = list(df_currency.loc[df_currency['count'] > 5000].salary_currency)

dates = df.loc[df['salary_currency'].isin(currency)].published_at
currency += ['BYN']

valutes = []
column = ['date'] + currency
max_month = 13
for year in range(2003, 2023):
    if year == 2022:
        max_month = int(dates.max()[5:7]) + 1
    for month in range(1, max_month):
        url = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{month:02}/{year}'
        print(url)
        df_valute = pd.read_xml(url, encoding='cp1251')[['CharCode', 'Nominal', 'Value']]
        df_valute = df_valute[df_valute['CharCode'].isin(currency)]
        df_valute['Value'] = df_valute['Value'].apply(lambda x: float(x.replace(',', '.')))
        df_valute['Value'] = df_valute['Value'] / df_valute['Nominal']
        df_valute['date'] = f'{year}-{month:02}'
        df_valute = df_valute.pivot_table(index='date', columns='CharCode', values='Value', aggfunc='sum').rename(columns={'BYN': 'BYR'})
        df_valute['UZS'] = np.NAN
        df_valute['KGS'] = np.NAN
        df_valute['AZN'] = np.NAN
        df_valute['GEL'] = np.NAN
        valutes.append(df_valute)
        print(df_valute.head())

df_merge = pd.concat(valutes)
print()
print(df_merge.head(10))
df_merge.to_csv('Currency_data.csv')
