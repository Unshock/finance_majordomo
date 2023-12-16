from decimal import Decimal

import xmltodict

from common.utils.datetime_utils import get_today_date
from finance_majordomo.stocks.models.asset import ProdCalendar
from finance_majordomo.stocks.models.currency import CurrencyRate
from datetime import datetime as dt
from datetime import timedelta as td
import requests


def update_currency_rates(date=None):

    # Постоянно шлет реквесты - переделать на update

    currency_code = {
        'usd': 'R01235',
        'euro': 'R01239'  # с евро пока не работаем
    }

    if date:
        date_req1 = date
    else:
        date_req1 = '01/01/2023'  # тянет с этой даты

    date_req2 = dt.strftime(dt.today(), '%d/%m/%Y')

    url = f'https://www.cbr.ru/scripts/XML_dynamic.asp?' \
          f'date_req1={date_req1}&' \
          f'date_req2={date_req2}&' \
          f'VAL_NM_RQ={currency_code["usd"]}'

    data = requests.get(url)

    usd_rates_list = xmltodict.parse(data.text)['ValCurs']['Record']

    if isinstance(usd_rates_list, dict):
        return

    for day_data in usd_rates_list:
        date_dt = dt.strptime(day_data.get('@Date'), "%d.%m.%Y")
        rate = Decimal(day_data.get('Value').replace(',', '.'))

        date_usd_rate, created = CurrencyRate.objects.get_or_create(
            tradedate=date_dt, price_usd=rate, defaults={
                'is_closed': False
            })
        date_usd_rate.is_closed = True
        date_usd_rate.save()


def update_usd():
    last_date = CurrencyRate.objects.last()
    print(f"last_date in usd table: {last_date}")
    last_date_str = dt.strftime(last_date.tradedate, '%d/%m/%Y')
    update_currency_rates(date=last_date_str)


def get_currency_rate(date_dt=None, *, currency=None):

    RANGE = 40  # max non-working range - mb to rework

    if not currency:
        return Decimal('1')

    if currency.lower() not in ('usd', 'euro'):
        raise ValueError(f'{currency} is not in ("usd", "euro")')

    if not date_dt:
        date_dt = get_today_date()

    for gap in range(RANGE):
        delta_date_dt = (date_dt - td(gap))

        date_str = dt.strftime(
            dt(delta_date_dt.year, delta_date_dt.month, delta_date_dt.day),
            '%Y-%m-%d')

        day_status = ProdCalendar.get_date(date_str).date_status

        if day_status == 'Working':
            try:
                result = CurrencyRate.objects.get(tradedate=delta_date_dt)

                if currency.lower() == 'usd':
                    return result.price_usd
                if currency.lower() == 'euro':
                    return result.price_euro

            except CurrencyRate.DoesNotExist:
                print(f'currency rate {delta_date_dt} does not exist')
                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
