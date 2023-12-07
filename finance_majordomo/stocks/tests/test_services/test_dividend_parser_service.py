import os
import requests_mock
import simplejson
from finance_majordomo.stocks.services.accrual_services\
    .dividends_parser_services import get_share_dividends
from finance_majordomo.stocks.tests.base_settings import BaseTest


FIXTURES_FOLDER = "fixtures"
HTML_FILE_POSI = 'POSI_dividend_page.html'
HTML_COMPANIES_DIVIDENDS = 'companies_dividends_page.html'
TEST_URL_POSI = \
    f"https://{'закрытияреестров.рф'.encode('idna').decode()}/gruppa-pozitiv/"
TEST_URL_COMPANIES_DIVIDENDS = \
    f"https://{'закрытияреестров.рф'.encode('idna').decode()}/_/"


class TestDividendParserService(BaseTest):

    def test_dividend_parser_common_share_1(self):

        POSI_dividend_page = os.path.join(
            os.path.dirname(__file__), FIXTURES_FOLDER, HTML_FILE_POSI
        )

        companies_dividends_page = os.path.join(
            os.path.dirname(__file__), FIXTURES_FOLDER, HTML_COMPANIES_DIVIDENDS
        )

        with open(POSI_dividend_page, 'r') as get_expected_posi:
            with open(companies_dividends_page, 'r') as get_expected_companies:
                with requests_mock.Mocker() as r:

                    r.register_uri(
                        "GET", TEST_URL_POSI,
                        text=get_expected_posi.read()
                    )
                    r.register_uri(
                        "GET", TEST_URL_COMPANIES_DIVIDENDS,
                        text=get_expected_companies.read()
                    )

                    result = get_share_dividends(self.share_POSI)

                    expected_result = simplejson.load(
                        open(os.path.join(os.path.dirname(__file__),
                                          FIXTURES_FOLDER,
                                          "POSI_dividend_data.json"), 'r'),
                        use_decimal=True
                    )

                    self.assertEqual(result, expected_result)
