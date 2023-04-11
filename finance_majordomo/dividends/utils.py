import requests
from bs4 import BeautifulSoup
import re
import datetime


ticker = 'sber'
url = f'https://закрытияреестров.рф/{ticker.upper()}/'


r = requests.get(url)
r.encoding = 'utf-8'
# print(r.text)


soup = BeautifulSoup(r.text, 'lxml')

#soup.find('td', style_='text-align: center; ')#style_='border: 1px solid #208ede; heihgt: 1377px;')
#table = soup.find('table', attrs={'style': 'border: 1px solid #208ede;'})
table = soup.find('table',style=lambda value: value and 'border: 1px solid #208ede;' in value)
data = []
table_body = table.find('tbody')

rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])

print(data)

ordinary = {}
priv = {}

result_dict = {}

date_row = 0
ordinary_row = None
priv_row = None

for i, row in enumerate(data[0]):
    if re.search(r'обыкновенную', row):
        ordinary_row = i
    if re.search(r'привилегированную', row):
        priv_row = i


for line in data[1:]:

    date = re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', line[0])

    if date:
        date = datetime.datetime.strptime(date.group(), "%d.%m.%Y").strftime("%d-%m-%Y")

        result_dict[date] = {'ordinary': {},
                             'priv': {}
                             }

        if ordinary_row:
            ordinary_price = re.search(r'\d+,\d+', line[ordinary_row])
            if ordinary_price:
                ordinary_div = True
                ordinary_price = ordinary_price.group()

            else:
                ordinary_div = False
                ordinary_price = '0,00'

            result_dict[date]['ordinary'] = {'div': ordinary_div,
                                             'value': ordinary_price}

        if priv_row:
            priv_price = re.search(r'\d+,\d+', line[priv_row])
            if priv_price:
                priv_div = True
                priv_price = priv_price.group()
            else:
                priv_div = False
                priv_price = '0,00'

            result_dict[date]['priv'] = {'div': priv_div,
                                         'value': priv_price}


print(result_dict)



