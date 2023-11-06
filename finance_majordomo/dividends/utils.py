from decimal import Decimal

import requests
from bs4 import BeautifulSoup
import re
import datetime
import django
import os
from datetime import datetime

from ..currencies.utils import get_usd_rate
from ..transactions.services.transaction_calculation_services import get_asset_quantity_for_portfolio
from ..users.models import Portfolio
from ..users.utils.utils import get_current_portfolio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
django.setup()

from .models import Dividend, DividendsOfUser, DividendsOfPortfolio


def get_stock_dividends(stock_obj):
    stock_type = stock_obj.type
    if stock_type == 'preferred_share':
        secid = stock_obj.secid[:-1]
    elif stock_type == 'common_share':
        secid = stock_obj.secid
    else:
        raise Exception('stock_type не опознан')
    
    

    url = f'https://' \
          f'{"закрытияреестров.рф".encode("idna").decode()}' \
          f'/{secid.upper()}/'

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

    print(dividend_dict)
    return dividend_dict


def add_dividends_to_model(asset_obj, dividend_dict):
    print(dividend_dict)
    asset_type = asset_obj.type
    print(asset_type)
    for date, div_value in dividend_dict.items():

        if asset_type in ['preferred_share', 'common_share'] and \
                div_value[asset_type]['div'] is True:
            amount = Decimal(div_value[asset_type]['value'])

        elif asset_type in ['ofz_bond', 'corporate_bond'] and \
                div_value['bond']['div'] is True:
            amount = Decimal(div_value['bond']['value'])

        else:
            continue

        try:
            existing_div = Dividend.objects.get(asset=asset_obj, date=date)

            if not existing_div.amount == amount:
                print('Dividend has been changed while updating. '
                      'Probably mistake!')
            continue

        except Dividend.DoesNotExist:
            dividend = Dividend.objects.create(
                date=datetime.strptime(date, "%Y-%m-%d"),
                asset=asset_obj,
                amount=amount
            )
            print(dividend)
            dividend.save()

    asset_obj.latest_dividend_update = datetime.today()
    #print('stock', stock_obj, stock_obj.latest_dividend_update)
    asset_obj.save()


# def get_dividend_result(user, asset_obj):
# 
#     users_dividends_received = Dividend.objects.filter(
#         asset=asset_obj.id,
#         id__in=user.dividendsofuser_set.filter(
#             is_received=True).values_list('dividend'))
# 
#     sum_dividends_received = 0
# 
#     for div in users_dividends_received:
#         print(div.date, type(div.date), 'DIVDATE')
#         quantity = get_quantity(user, asset_obj, date=div.date)
#         sum_dividends_received += quantity * div.amount
# 
#     return sum_dividends_received * Decimal(0.87)
# 
# 
# def get_dividend_result_usd(user, asset_obj):
# 
#     users_dividends_received = Dividend.objects.filter(
#         asset=asset_obj.id,
#         id__in=user.dividendsofuser_set.filter(
#             is_received=True).values_list('dividend'))
# 
#     sum_dividends_received = 0
# 
#     for div in users_dividends_received:
# 
#         quantity = get_quantity(user, asset_obj, date=div.date)
#         usd_rate = get_usd_rate(div.date)
#         sum_dividends_received += quantity * div.amount / usd_rate
# 
#     return sum_dividends_received * Decimal(0.87)


def get_dividend_result_of_portfolio(
        portfolio: Portfolio, asset_id: int, currency: str = None) -> Decimal:

    portfolio_dividends_received = Dividend.objects.filter(
        asset=asset_id,
        id__in=portfolio.dividendsofportfolio_set.filter(
            is_received=True).values_list('dividend'))

    currency_rate = Decimal('1')

    sum_dividends_received = Decimal('0')

    for div in portfolio_dividends_received:

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_id, date=div.date)

        if currency == 'usd':
            currency_rate = get_usd_rate(div.date)
        sum_dividends_received += quantity * div.amount / currency_rate

    return sum_dividends_received * Decimal(0.87)


def update_dividends_of_user(request, asset_obj, date=None, transaction=None):

    asset_dividends = Dividend.objects.filter(asset=asset_obj.id)
    portfolio = get_current_portfolio(request.user)
    print(asset_dividends, 'tttttttttttttttttttttttttttttttt')

    if date:
        asset_dividends = asset_dividends.filter(date__gte=date)

    # users_dividends = Dividend.objects.filter(
    #     stock=stock_obj.id,
    #     id__in=request.user.dividendsofuser_set.values_list(
    #         'dividend'))

    for div in asset_dividends:

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_obj.id, date=div.date)\
                   - transaction.quantity

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
        print(dividend_of_user)
        dividend_of_user.save()


def update_dividends_of_portfolio(
        portfolio, asset_id, date=None, transaction=None):

    asset_dividends = Dividend.objects.filter(asset=asset_id)

    if date:
        asset_dividends = asset_dividends.filter(date__gte=date)

    for div in asset_dividends:

        tr_quantity = transaction.quantity if transaction.transaction_type == \
                                           'BUY' else transaction.quantity * -1

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_id, date=div.date) + tr_quantity
        
        print('DIVIDEND QUANTITTY', quantity, tr_quantity, quantity - tr_quantity)
        
        try:
            dividend_of_portfolio = DividendsOfPortfolio.objects.get(
                portfolio=portfolio,
                dividend=div)

            if quantity <= 0:
                dividend_of_portfolio.is_received = False

        except DividendsOfPortfolio.DoesNotExist:
            dividend_of_portfolio = DividendsOfPortfolio.objects.create(
                portfolio=portfolio,
                dividend=div,
                is_received=False
            )
        print(dividend_of_portfolio)
        dividend_of_portfolio.save()
