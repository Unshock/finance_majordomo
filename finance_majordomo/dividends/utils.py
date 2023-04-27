from decimal import Decimal

import requests
from bs4 import BeautifulSoup
import re
import datetime
import django
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
django.setup()

from finance_majordomo.dividends.models import Dividend


def get_stock_dividends(stock_obj):
    stock_type = stock_obj.type
    if stock_type == 'preferred_share':
        ticker = stock_obj.ticker[:-1]
    elif stock_type == 'common_share':
        ticker = stock_obj.ticker
    else:
        raise Exception('stock_type не опознан')

    url = f'https://закрытияреестров.рф/{ticker.upper()}/'

    dividend_page_code = requests.get(url)
    dividend_page_code.encoding = 'utf-8'

    dividend_page_soup = BeautifulSoup(dividend_page_code.text, 'lxml')

    table = dividend_page_soup.find('table', style=lambda value: value and 'border: 1px solid #208ede;' in value)

    data = []
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [element.text.strip() for element in cols]
        data.append([element for element in cols if element])

    #common_share = {}
    #preferred_share = {}
    dividend_dict = {}

    date_row = 0
    common_share_row = None
    preferred_share_row = None

    for i, row in enumerate(data[0]):
        if re.search(r'обыкновенную', row):
            common_share_row = i
        if re.search(r'привилегированную', row):
            preferred_share_row = i

    for line in data[1:]:

        date = re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', line[0])

        if date:
            date = datetime.datetime.strptime(date.group(), "%d.%m.%Y").strftime("%Y-%m-%d")

            dividend_dict[date] = {'common_share': {},
                                   'preferred_share': {}
                                   }

            if common_share_row:
                common_share_price = re.search(r'\d+,\d+', line[common_share_row])
                if common_share_price:
                    common_share_div = True
                    common_share_price = common_share_price.group().replace(',', '.')
                    

                else:
                    common_share_div = False
                    common_share_price = '0.00'

                dividend_dict[date]['common_share'] = \
                    {'div': common_share_div,
                     'value': common_share_price}

            if preferred_share_row:
                preferred_share_price = re.search(r'\d+,\d+', line[preferred_share_row])
                if preferred_share_price:
                    preferred_share_div = True
                    preferred_share_price = preferred_share_price.group().replace(',', '.')
                else:
                    preferred_share_div = False
                    preferred_share_price = '0.00'

                dividend_dict[date]['preferred_share'] = \
                    {'div': preferred_share_div,
                     'value': preferred_share_price}


    #print(dividend_dict)
    return dividend_dict


def add_dividends_to_model(stock_obj, dividend_dict):

    stock_type = stock_obj.type

    for key, value in dividend_dict.items():
        try:
            div = Dividend.objects.get(stock=stock_obj, date=key)

        except Dividend.DoesNotExist:
            dividend = Dividend()
            dividend.date = key
            dividend.stock = stock_obj
            if stock_type == 'preferred_share' and \
                    value['preferred_share']['div'] is True:
                dividend.dividend = Decimal(value['preferred_share']['value'])
            elif stock_type == 'common_share' and \
                    value['common_share']['div'] is True:
                dividend.dividend = Decimal(value['common_share']['value'])
            dividend.save()



from finance_majordomo.stocks.models import Stock
stock_obj = Stock.objects.get(id=4)


a = get_stock_dividends(stock_obj)
add_dividends_to_model(stock_obj, a)




