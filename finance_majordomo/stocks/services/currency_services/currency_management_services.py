from decimal import Decimal

import xmltodict

from finance_majordomo.stocks.models.asset import ProdCalendar
from finance_majordomo.stocks.models.currency import CurrencyRate
from datetime import datetime as dt
from datetime import timedelta as td
import requests


def get_currency_rate(currency: str = None):
    if currency and currency.lower() == 'usd':
        currency_rate = CurrencyRate.objects.last().price_usd
    else:
        currency_rate = Decimal('1')

    return currency_rate

def update_currency_rates(date=None):

    # Постоянно шлет реквесты - переделать на update

    if date:
        date_req1 = date
    else:
        date_req1 = '01/01/2023'  # тянет с этой даты

    date_req2 = dt.strftime(dt.today(), '%d/%m/%Y')

    url = f'https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date_req1}' \
          f'&date_req2={date_req2}&VAL_NM_RQ=R01235'

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
    print(last_date)
    last_date_str = dt.strftime(last_date.tradedate, '%d/%m/%Y')
    update_currency_rates(date=last_date_str)


def get_usd_rate(date_dt):

    for gap in range(0, 40):
        delta_date_dt = (date_dt - td(gap))

        date_str = dt.strftime(
            dt(delta_date_dt.year,
                     delta_date_dt.month,
                     delta_date_dt.day), '%Y-%m-%d')

        day_status = ProdCalendar.get_date(date_str).date_status

        #print(day_status)

        if day_status == 'Working':
            try:
                result = CurrencyRate.objects.get(tradedate=delta_date_dt)
                #print('resik', result)
                return result.price_usd
            except CurrencyRate.DoesNotExist:
                print(f'currency rate {delta_date_dt} does not exist')
