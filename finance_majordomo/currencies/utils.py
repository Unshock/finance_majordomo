from datetime import datetime, timedelta
from decimal import Decimal

from .models import CurrencyRate
import requests
import xmltodict

from ..stocks.utils import get_prod_date


def update_currency_rates(date=None):

    if date:
        date_req1 = date
    else:
        date_req1 = '01/01/2023'

    date_req2 = datetime.strftime(
        datetime.today().date(), '%d/%m/%Y')

    url = f'https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date_req1}' \
          f'&date_req2={date_req2}&VAL_NM_RQ=R01235'

    data = requests.get(url)

    usd_rates_list = xmltodict.parse(data.text)['ValCurs']['Record']

    if isinstance(usd_rates_list, dict):
        return

    for day_data in usd_rates_list:
        date_dt = datetime.strptime(day_data.get('@Date'), "%d.%m.%Y")
        rate = Decimal(day_data.get('Value').replace(',', '.'))

        date_usd_rate, created = CurrencyRate.objects.get_or_create(
            tradedate=date_dt, price_usd=rate, defaults={
                'is_closed': False
            })
        date_usd_rate.is_closed = True
        date_usd_rate.save()


def update_usd():
    last_date = CurrencyRate.objects.last()
    last_date_str = datetime.strftime(last_date.tradedate, '%d/%m/%Y')
    update_currency_rates(date=last_date_str)
    

def get_usd_rate(date_dt):

    for gap in range(0, 20):
        delta_date_dt = (date_dt - timedelta(gap))

        date_str = datetime.strftime(
            datetime(delta_date_dt.year,
                     delta_date_dt.month,
                     delta_date_dt.day), '%Y-%m-%d')

        day_status = get_prod_date(date_str).date_status

        if day_status == 'Working':
            try:
                result = CurrencyRate.objects.get(tradedate=delta_date_dt)
                return result.price_usd
            except CurrencyRate.DoesNotExist:
                print(f'currency rate {delta_date_dt} doesnot exist')
