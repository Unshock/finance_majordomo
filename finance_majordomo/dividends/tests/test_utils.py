import json
import os
from _decimal import Decimal

from django.test.client import RequestFactory
import requests_mock
from django.core.exceptions import ObjectDoesNotExist
from finance_majordomo.dividends.models import Dividend
from finance_majordomo.dividends.tests.setting import SettingsDividends
from finance_majordomo.dividends.utils import get_stock_dividends, add_dividends_to_model


FIXTURES_FOLDER = 'fixtures'
HTML_FILE_LSNG = 'LSNG_divs.html'
HTML_FILE_TATN = 'TATN_divs.html'
TEST_URL_LSNG = f"https://{'закрытияреестров.рф'.encode('idna').decode()}/LSNG/"
TEST_URL_TATN = f"https://{'закрытияреестров.рф'.encode('idna').decode()}/TATN/"


class TestDividendUtils(SettingsDividends):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.requests_mock = requests_mock

    def test_dividend_parser_common_share_1(self):
        LSNG_HTML_PATH = os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      HTML_FILE_LSNG)

        with open(LSNG_HTML_PATH, 'r') as get_expected:

            with requests_mock.Mocker() as r:

                r.register_uri("GET", TEST_URL_LSNG, text=get_expected.read())

                result = get_stock_dividends(self.stock_id_1)

                lsng_result = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "LSNG_divs.json"), 'r'))

                assert result == lsng_result

    def test_dividend_parser_preferred_share_1(self):

        LSNG_HTML_PATH = os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      HTML_FILE_LSNG)

        with open(LSNG_HTML_PATH, 'r') as get_expected:

            with requests_mock.Mocker() as r:

                r.register_uri("GET", TEST_URL_LSNG, text=get_expected.read())

                result = get_stock_dividends(self.stock_id_2)

                lsng_result = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "LSNG_divs.json"), 'r'))

                assert result == lsng_result

    def test_dividend_parser_common_share_2(self):

        TATN_HTML_PATH = os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      HTML_FILE_TATN)


        with open(TATN_HTML_PATH, 'r') as get_expected:

            with requests_mock.Mocker() as r:

                r.register_uri("GET", TEST_URL_TATN, text=get_expected.read())

                result = get_stock_dividends(self.stock_id_3)

                tatn_result = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "TATN_divs.json"), 'r'))

                assert result == tatn_result

    def test_dividend_parser_preferred_share_2(self):

        TATN_HTML_PATH = os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      HTML_FILE_TATN)


        with open(TATN_HTML_PATH, 'r') as get_expected:

            with requests_mock.Mocker() as r:

                r.register_uri("GET", TEST_URL_TATN, text=get_expected.read())

                result = get_stock_dividends(self.stock_id_4)

                tatn_result = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "TATN_divs.json"), 'r'))

                assert result == tatn_result
                assert isinstance(result, dict)

    def test_add_dividend_to_model(self):

        valid_dividend_dict = json.load(
                    open(os.path.join(os.path.dirname(__file__),
                                      FIXTURES_FOLDER,
                                      "TATN_divs.json"), 'r'))

        add_dividends_to_model(self.stock_id_3, valid_dividend_dict)

        dividends = Dividend.objects.all()

        assert dividends.count() == 35
        with self.assertRaises(Dividend.DoesNotExist):
            Dividend.objects.get(date='2020-06-30')
        assert sum([div.amount for div in dividends]) == Decimal("418.69")

        add_dividends_to_model(self.stock_id_4, valid_dividend_dict)
        dividends = Dividend.objects.all()

        assert dividends.count() == 71
        assert Dividend.objects.get(date='2020-06-30').stock == self.stock_id_4
        assert len(Dividend.objects.filter(date='2004-05-10')) == 2
        assert Dividend.objects.get(
            date='2004-05-10',
            stock=self.stock_id_3).amount == Decimal("0.30")
        assert Dividend.objects.get(
            date='2004-05-10',
            stock=self.stock_id_4).amount == Decimal("1")
        assert sum([div.amount for div in dividends]) == Decimal("841.23")
