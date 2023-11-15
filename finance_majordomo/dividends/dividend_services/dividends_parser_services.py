import re
from datetime import datetime
from decimal import Decimal

import requests
from bs4 import BeautifulSoup
from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.stocks.models import Asset


def get_share_dividends(asset_obj):
    """
    site1: закрытияреестров.рф
    """

    try:
        return GetShareDividendsSite1.execute({'share': asset_obj})

    except Exception as e:
        print(e)


class GetShareDividendsSite1(Service):
    """Parse dividends from 'закрытияреестров.рф'
        returns dictionary like:
        {datetime.date: {'common_share': {'div': Bool, 'value': Decimal},
                         'preferred_share': {'div': Bool, 'value': Decimal}},
         datetime.date ...
         }
    """

    share = ModelField(Asset)

    def process(self):
        self.share = self.cleaned_data.get('share')

        url = self._get_share_dividends_page_url(
            self._get_ticker_depend_on_type())
        divs_data_table = self._get_dividends_data_table(url)
        return self._get_dividends_dict(divs_data_table)

    def _get_ticker_depend_on_type(self):
        share_type = self.share.type

        if share_type == 'preferred_share':
            return self.share.secid[:-1]
        elif share_type == 'common_share':
            return self.share.secid
        else:
            raise Exception('share_type is not supported')

    def _get_share_dividends_page_url(self, ticker):
        path = self._get_share_dividends_page_path(ticker)

        url = f'https://' \
              f'{"закрытияреестров.рф".encode("idna").decode()}' \
              f'/{path}/'

        return url

    @staticmethod
    def _get_share_dividends_page_path(ticker):

        "gets path for the page of the site share dividends are on"

        url = f'https://' \
              f'{"закрытияреестров.рф".encode("idna").decode()}' \
              f'/_/'

        companies_page_code = requests.get(url)
        companies_page_code.encoding = 'utf-8'

        companies_page_soup = BeautifulSoup(companies_page_code.text, 'lxml')

        span = companies_page_soup.select_one(
            f'span:-soup-contains("{ticker.upper()}")')

        if not span:
            span = companies_page_soup.select_one(
                f'span:-soup-contains("{ticker.lower()}")')

        path = span.find('a').get('href')

        return path.strip('./')

    @staticmethod
    def _get_dividends_data_table(url):

        dividend_page_code = requests.get(url)
        dividend_page_code.encoding = 'utf-8'
        dividend_page_soup = BeautifulSoup(dividend_page_code.text, 'lxml')

        table = dividend_page_soup.find(
            'table',
            style=lambda value: value and 'border: 1px solid #208ede;' in value)

        dividend_data_table = []
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [element.text.strip() for element in cols]
            dividend_data_table.append([element for element in cols if element])

        return dividend_data_table

    def _get_dividends_dict(self, data_table):

        dividend_dict = {}

        common_share_row = None
        preferred_share_row = None

        for i, row in enumerate(data_table[0]):
            if re.search(r'обыкновенную', row):
                common_share_row = i
            if re.search(r'привилегированную', row):
                preferred_share_row = i

        for t_line in data_table[1:]:

            date = re.search(
                r'(?!0{1,2}\.)\d{1,2}\.(?!0{1,2}\.)\d{1,2}\.\d{4}', t_line[0])

            if date:

                date = self._make_formatted_date(date)

                dividend_dict[date] = {'common_share': {},
                                       'preferred_share': {}
                                       }

                if common_share_row:

                    dividend_dict[date]['common_share'] = \
                        self._get_row_dividend_data(t_line, common_share_row)

                if preferred_share_row:

                    dividend_dict[date]['preferred_share'] = \
                        self._get_row_dividend_data(t_line, preferred_share_row)
        return dividend_dict

    @staticmethod
    def _make_formatted_date(date_site_format):
        return datetime.strptime(
            date_site_format.group(), "%d.%m.%Y").strftime("%Y-%m-%d")

    @staticmethod
    def _get_row_dividend_data(t_line, row) -> dict:
        share_price = re.search(
            r'\d+,\d+', t_line[row])
        if share_price:
            share_div = True
            share_price = Decimal(share_price.group().replace(',', '.'))

        else:
            share_div = False
            share_price = Decimal('0.00')

        return {'div': share_div, 'value': share_price}
