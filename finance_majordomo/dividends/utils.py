from decimal import Decimal

import requests
from bs4 import BeautifulSoup
import re
import datetime
import django
import os
from datetime import datetime

from ..transactions.utils import get_quantity


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
django.setup()

from .models import Dividend, DividendsOfUser


def get_stock_dividends(stock_obj):
    stock_type = stock_obj.type
    if stock_type == 'preferred_share':
        ticker = stock_obj.ticker[:-1]
    elif stock_type == 'common_share':
        ticker = stock_obj.ticker
    else:
        raise Exception('stock_type не опознан')

    url = f'https://' \
          f'{"закрытияреестров.рф".encode("idna").decode()}' \
          f'/{ticker.upper()}/'

    dividend_page_code = requests.get(url)
    dividend_page_code.encoding = 'utf-8'

    dividend_page_soup = BeautifulSoup(dividend_page_code.text, 'lxml')

    table = dividend_page_soup.find(
        'table',
        style=lambda value: value and 'border: 1px solid #208ede;' in value)

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

    common_share_row = None
    preferred_share_row = None

    for i, row in enumerate(data[0]):
        if re.search(r'обыкновенную', row):
            common_share_row = i
        if re.search(r'привилегированную', row):
            preferred_share_row = i

    for line in data[1:]:

        date = re.search(
            r'(?!0{1,2}\.)\d{1,2}\.(?!0{1,2}\.)\d{1,2}\.\d{4}', line[0])

        if date:

            date = datetime.strptime(
                date.group(), "%d.%m.%Y").strftime("%Y-%m-%d")

            dividend_dict[date] = {'common_share': {},
                                   'preferred_share': {}
                                   }

            if common_share_row:
                common_share_price = re.search(
                    r'\d+,\d+', line[common_share_row])
                if common_share_price:
                    common_share_div = True
                    common_share_price = \
                        common_share_price.group().replace(',', '.')

                else:
                    common_share_div = False
                    common_share_price = '0.00'

                dividend_dict[date]['common_share'] = \
                    {'div': common_share_div,
                     'value': common_share_price}

            if preferred_share_row:
                preferred_share_price = re.search(
                    r'\d+,\d+', line[preferred_share_row])
                if preferred_share_price:
                    preferred_share_div = True
                    preferred_share_price = \
                        preferred_share_price.group().replace(',', '.')

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

    for date, div_value in dividend_dict.items():

        if stock_type in ['preferred_share', 'common_share'] and \
                div_value[stock_type]['div'] is True:
            amount = Decimal(div_value[stock_type]['value'])

            #print(date, amount)
        
        else:
            continue

        # if stock_type == 'preferred_share' and \
        #         div_value['preferred_share']['div'] is True:
        #     amount = Decimal(div_value['preferred_share']['value'])
        # elif stock_type == 'common_share' and \
        #         div_value['common_share']['div'] is True:
        #     amount = Decimal(div_value['common_share']['value'])

        try:
            existing_div = Dividend.objects.get(stock=stock_obj, date=date)

            if not existing_div.amount == amount:
                print('Dividend has been changed while updating. '
                      'Probably mistake!')
            continue

        except Dividend.DoesNotExist:
            dividend = Dividend.objects.create(
                date=datetime.strptime(date, "%Y-%m-%d"),
                stock=stock_obj,
                amount=amount
            )

            dividend.save()

    stock_obj.latest_dividend_update = datetime.today()
    #print('stock', stock_obj, stock_obj.latest_dividend_update)
    stock_obj.save()


def get_dividend_result(request, stock_obj):

    users_dividends_received = Dividend.objects.filter(
        stock=stock_obj.id,
        id__in=request.user.dividendsofuser_set.filter(
            is_received=True).values_list('dividend'))

    sum_dividends_received = 0

    for div in users_dividends_received:

        quantity = get_quantity(request, stock_obj, date=div.date)
        sum_dividends_received += quantity * div.amount

    return sum_dividends_received * Decimal(0.87)


def update_dividends_of_user(request, stock_obj, date=None):

    stock_dividends = Dividend.objects.filter(stock=stock_obj.id)

    if date:
        stock_dividends = stock_dividends.filter(date__gte=date)

    # users_dividends = Dividend.objects.filter(
    #     stock=stock_obj.id,
    #     id__in=request.user.dividendsofuser_set.values_list(
    #         'dividend'))

    for div in stock_dividends:

        quantity = get_quantity(request, stock_obj, div.date)

        try:
            dividend_of_user = DividendsOfUser.objects.get(
                user=request.user,
                dividend=div)

            if quantity <= 0:
                dividend_of_user.is_received = False

        except DividendsOfUser.DoesNotExist:
            dividend_of_user = DividendsOfUser.objects.create(
                user=request.user,
                dividend=div,
                is_received=False
            )

        dividend_of_user.save()
