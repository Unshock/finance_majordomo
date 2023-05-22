import json
import os
from django.test.client import RequestFactory
import requests_mock


from finance_majordomo.dividends.tests.setting import SettingsDividends
from finance_majordomo.dividends.utils import get_stock_dividends


FIXTURES_FOLDER = 'fixtures'
MAIN_HTML_FILE = 'LSNG_divs.html'
TEST_URL = f"https://{'закрытияреестров.рф'.encode('idna').decode()}/LSNG/"

ORIGINAL_HTML_PATH = os.path.join(os.path.dirname(__file__),
                                  FIXTURES_FOLDER,
                                  MAIN_HTML_FILE)


class TestDividendUtils(SettingsDividends):
    
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.requests_mock = requests_mock

    def test_dividend_common_share(self):


        with open(ORIGINAL_HTML_PATH, 'r') as get_expected:

            with requests_mock.Mocker() as r:

                r.register_uri("GET", TEST_URL, text=get_expected.read())

                result = get_stock_dividends(self.stock_id_1)

                lsng_result = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "LSNG_divs.json"), 'r'))

                assert result == lsng_result
    
    def test_dividend_preferred_share(self):


        with open(ORIGINAL_HTML_PATH, 'r') as get_expected:

            with requests_mock.Mocker() as r:

                r.register_uri("GET", TEST_URL, text=get_expected.read())

                result = get_stock_dividends(self.stock_id_2)

                lsng_result = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "LSNG_divs.json"), 'r'))

                assert result == lsng_result