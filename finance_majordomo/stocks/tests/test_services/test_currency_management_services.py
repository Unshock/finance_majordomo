from datetime import date as d
import os
from decimal import Decimal

import requests_mock
from unittest.mock import patch
from unittest import mock
import simplejson

from finance_majordomo.stocks.models.currency import CurrencyRate
from finance_majordomo.stocks.services.accrual_services\
    .dividends_parser_services import get_share_dividends
from finance_majordomo.stocks.services.currency_services.currency_management_services import \
    update_currency_rates
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.stocks.tests.test_services.conftest import MockedDate

FIXTURES_FOLDER = "fixtures"

DATETIME = "finance_majordomo.stocks.services.currency_services." \
    "currency_management_services.date"

CBR_RESPONSE_DOLLAR_20_12 = 'cbr_dollar_response_20-12-2022_20-01-2023.xml'
CBR_RESPONSE_EURO_20_12 = 'cbr_euro_response_20-12-2022_20-01-2023.xml'
CBR_RESPONSE_DOLLAR_01_01 = 'cbr_dollar_response_01-01-2023_20-01-2023.xml'
CBR_RESPONSE_EURO_01_01 = 'cbr_euro_response_01-01-2023_20-01-2023.xml'

URL_CBR_DOLLAR = 'https://www.cbr.ru/scripts/XML_dynamic.asp?' \
                 'date_req1={start_date}&' \
                 'date_req2={end_date}&' \
                 'VAL_NM_RQ=R01235'

URL_CBR_EURO = 'https://www.cbr.ru/scripts/XML_dynamic.asp?' \
               'date_req1={start_date}&' \
               'date_req2={end_date}&' \
               'VAL_NM_RQ=R01239'


class TestCurrencyManagementService(BaseTest):

    def test_update_currency_rates_with_date(self):

        start_date = '20/12/2022'
        end_date = '20/01/2023'

        url_cbr_dollar = URL_CBR_DOLLAR.format(
            start_date=start_date, end_date=end_date)

        cbr_dollar_response = os.path.join(
            os.path.dirname(__file__),
            FIXTURES_FOLDER,
            CBR_RESPONSE_DOLLAR_20_12
        )

        self.assertEqual(CurrencyRate.objects.count(), 6)

        test_today = d(2023, 1, 20)
        with mock.patch(DATETIME, wraps=d) as date:
            date.today.return_value = test_today
            with open(cbr_dollar_response, 'r') as cbr_dollar_response:
                with requests_mock.Mocker() as r:

                    r.register_uri(
                        "GET", url_cbr_dollar,
                        text=cbr_dollar_response.read()
                    )

                    update_currency_rates(start_date=start_date)

                    self.assertEqual(CurrencyRate.objects.count(), 25)
                    self.assertEqual(
                        CurrencyRate.objects.get(id=101).tradedate,
                        date(2022, 12, 20))
                    self.assertEqual(
                        CurrencyRate.objects.get(id=101).price_usd,
                        Decimal('66.3474'))
                    self.assertEqual(
                        CurrencyRate.objects.last().tradedate,
                        date(2023, 1, 20))
                    self.assertEqual(
                        CurrencyRate.objects.last().price_usd,
                        Decimal('68.8467'))

    def test_update_currency_rates_no_date(self):

        start_date = '01/01/2023'
        end_date = '20/01/2023'

        url_cbr_dollar = URL_CBR_DOLLAR.format(
            start_date=start_date, end_date=end_date)

        cbr_dollar_response = os.path.join(
            os.path.dirname(__file__),
            FIXTURES_FOLDER,
            CBR_RESPONSE_DOLLAR_01_01
        )

        self.assertEqual(CurrencyRate.objects.count(), 6)

        test_today = d(2023, 1, 20)
        with mock.patch(DATETIME, wraps=d) as date:
            date.today.return_value = test_today
            with open(cbr_dollar_response, 'r') as cbr_dollar_response:
                with requests_mock.Mocker() as r:

                    r.register_uri(
                        "GET", url_cbr_dollar,
                        text=cbr_dollar_response.read()
                    )

                    update_currency_rates()

                    self.assertEqual(CurrencyRate.objects.count(), 15)
                    self.assertEqual(
                        CurrencyRate.objects.get(id=101).tradedate,
                        date(2023, 1, 10))
                    self.assertEqual(
                        CurrencyRate.objects.get(id=101).price_usd,
                        Decimal('70.3002'))
                    self.assertEqual(
                        CurrencyRate.objects.last().tradedate,
                        date(2023, 1, 20))
                    self.assertEqual(
                        CurrencyRate.objects.last().price_usd,
                        Decimal('68.8467'))
