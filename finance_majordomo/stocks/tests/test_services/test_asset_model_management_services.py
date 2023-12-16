from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
from unittest import mock
from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.models.asset import Bond, Stock
from finance_majordomo.stocks.services.asset_services.\
    asset_model_management_services import \
    get_or_create_asset_obj, get_current_asset_price_per_asset
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.stocks.tests.test_services.conftest import \
    AssetServicesFixtureSetUp


FIXTURES_FOLDER = "fixtures"

GET_CURRENCY_RATE_DATETIME = \
    "finance_majordomo.stocks.services.currency_services." \
    "currency_management_services.get_today_date"

GET_ASSET_HISTORY_DATA = \
    "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_asset_history_data"

GET_BOND_COUPON_HISTORY =\
    "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_bond_coupon_history"

GET_SHARE_DIVIDENDS =\
    "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_share_dividends"

GET_ASSET_DESCRIPTION =\
    "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_asset_description"

DESCRIPTION_LQDT = 'get_stock_description_LQDT.json'
DESCRIPTION_RU000A0JTW83 = 'get_stock_description_RU000A0JTW83.json'
DESCRIPTION_SBER = 'get_stock_description_SBER.json'
DESCRIPTION_SU26222RMFS8 = 'get_stock_description_SU26222RMFS8.json'
DESCRIPTION_ZSGPP = 'get_stock_description_ZSGPP.json'

SHARE_ACCRUAL_DATA = 'POSI_dividend_data.json'
BOND_ACCRUAL_DATA = 'bond_accrual_data.json'

SHARE_HISTORY_DATA = 'get_asset_history_data_SHARE.json'
BOND_HISTORY_DATA = 'get_asset_history_data_BOND.json'


class AssetModelManagementServicesTest(BaseTest, AssetServicesFixtureSetUp):

    @mock.patch(GET_SHARE_DIVIDENDS)
    @mock.patch(GET_BOND_COUPON_HISTORY)
    @mock.patch(GET_ASSET_HISTORY_DATA)
    @mock.patch(GET_ASSET_DESCRIPTION)
    def test_get_or_create_asset_obj_RU000A0JTW83(
            self, mocked_get_asset_description, mocked_get_asset_history_data,
            mocked_get_bond_coupon_history, mocked_get_share_dividends
    ):
        mocked_get_asset_description.return_value =\
            self.description_RU000A0JTW83
        mocked_get_asset_history_data.return_value = self.bond_history_data
        mocked_get_bond_coupon_history.return_value = self.bond_accrual_data
        mocked_get_share_dividends.return_value = None

        asset = get_or_create_asset_obj('Ticker', 'expected_board_id')
        sub_asset = asset.get_related_object()

        self.assertTrue(isinstance(asset, Asset))
        self.assertEqual(asset.get_related_object().id, asset.id)
        self.assertTrue(isinstance(sub_asset, Bond))

        self.assertEqual(asset.latname, 'DOM.RF - 25')
        self.assertEqual(asset.secid, 'RU000A0JTW83')
        self.assertEqual(asset.isin, 'RU000A0JTW83')
        self.assertEqual(asset.name, 'ДОМ.РФ25об')

        self.assertEqual(asset.currency, 'RUR')
        self.assertEqual(
            asset.issuedate, datetime(year=2013, month=4, day=29).date())

        self.assertEqual(asset.isqualifiedinvestors, False)
        self.assertEqual(asset.morningsession, False)
        self.assertEqual(asset.eveningsession, False)

        self.assertEqual(asset.type, 'corporate_bond')
        self.assertEqual(asset.typename, 'Корпоративная облигация')
        self.assertEqual(asset.group, 'stock_bonds')
        self.assertEqual(asset.groupname, 'Облигации')

        self.assertEqual(asset.primary_boardid, 'expected_board_id')

        self.assertEqual(sub_asset.startdatemoex, datetime(
            year=2013, month=5, day=13).date())
        self.assertEqual(sub_asset.buybackdate, datetime(
            year=2024, month=1, day=1).date())
        self.assertEqual(sub_asset.matdate, datetime(
            year=2026, month=10, day=1).date())
        self.assertEqual(sub_asset.couponfrequency, Decimal('4'))
        self.assertEqual(sub_asset.couponpercent, Decimal('13.1'))
        self.assertEqual(sub_asset.couponvalue, Decimal('26.42'))
        self.assertEqual(sub_asset.days_to_redemption, 1026)
        self.assertEqual(sub_asset.face_value, 800)

        self.assertTrue(asset.latest_accrual_update)
        self.assertEqual(len(asset.dividend_set.all()), 2)
        self.assertEqual(
            asset.dividend_set.get(date='2024-10-16').amount, Decimal('35.4'))

        self.assertEqual(len(asset.assetshistoricaldata_set.all()), 6)

    @mock.patch(GET_SHARE_DIVIDENDS)
    @mock.patch(GET_BOND_COUPON_HISTORY)
    @mock.patch(GET_ASSET_HISTORY_DATA)
    @mock.patch(GET_ASSET_DESCRIPTION)
    def test_get_or_create_asset_obj_SU26222RMFS8(
            self, mocked_get_asset_description, mocked_get_asset_history_data,
            mocked_get_bond_coupon_history, mocked_get_share_dividends
    ):
        mocked_get_asset_description.return_value = \
            self.description_SU26222RMFS8
        mocked_get_asset_history_data.return_value = self.bond_history_data
        mocked_get_bond_coupon_history.return_value = self.bond_accrual_data
        mocked_get_share_dividends.return_value = None

        asset = get_or_create_asset_obj('Ticker', 'expected_board_id')
        sub_asset = asset.get_related_object()

        self.assertTrue(isinstance(asset, Asset))
        self.assertTrue(isinstance(sub_asset, Bond))
        self.assertEqual(asset.get_related_object().id, asset.id)

        self.assertEqual(asset.latname, 'OFZ-PD 26222')
        self.assertEqual(asset.secid, 'SU26222RMFS8Unique')
        self.assertEqual(asset.isin, 'RU000A0JXQF2Unique')
        self.assertEqual(asset.name, 'ОФЗ 26222')

        self.assertEqual(asset.currency, 'RUR')
        self.assertEqual(
            asset.issuedate, datetime(year=2017, month=5, day=3).date())

        self.assertEqual(asset.isqualifiedinvestors, False)
        self.assertEqual(asset.morningsession, False)
        self.assertEqual(asset.eveningsession, True)

        self.assertEqual(asset.type, 'ofz_bond')
        self.assertEqual(asset.typename, 'Государственная облигация')
        self.assertEqual(asset.group, 'stock_bonds')
        self.assertEqual(asset.groupname, 'Облигации')

        self.assertEqual(asset.primary_boardid, 'expected_board_id')

        self.assertEqual(sub_asset.startdatemoex, datetime(
            year=2017, month=5, day=3).date())
        self.assertEqual(sub_asset.buybackdate, None)
        self.assertEqual(sub_asset.matdate, datetime(
            year=2024, month=10, day=16).date())
        self.assertEqual(sub_asset.couponfrequency, Decimal('2'))
        self.assertEqual(sub_asset.couponpercent, Decimal('7.1'))
        self.assertEqual(sub_asset.couponvalue, Decimal('35.4'))
        self.assertEqual(sub_asset.days_to_redemption, 311)
        self.assertEqual(sub_asset.face_value, 1000)

        self.assertTrue(asset.latest_accrual_update)
        self.assertEqual(len(asset.dividend_set.all()), 2)
        self.assertEqual(
            asset.dividend_set.get(date='2024-10-16').amount, Decimal('35.4'))

        self.assertEqual(len(asset.assetshistoricaldata_set.all()), 6)

    @mock.patch(GET_SHARE_DIVIDENDS)
    @mock.patch(GET_BOND_COUPON_HISTORY)
    @mock.patch(GET_ASSET_HISTORY_DATA)
    @mock.patch(GET_ASSET_DESCRIPTION)
    def test_get_or_create_asset_obj_ZSGPP(
            self, mocked_get_asset_description, mocked_get_asset_history_data,
            mocked_get_bond_coupon_history, mocked_get_share_dividends
    ):
        mocked_get_asset_description.return_value = self.description_ZSGPP
        mocked_get_asset_history_data.return_value = self.share_history_data
        mocked_get_bond_coupon_history.return_value = None
        mocked_get_share_dividends.return_value = self.share_accrual_data

        asset = get_or_create_asset_obj('Ticker', 'expected_board_id')
        sub_asset = asset.get_related_object()

        self.assertTrue(isinstance(asset, Asset))
        self.assertTrue(isinstance(sub_asset, Stock))
        self.assertEqual(asset.get_related_object().id, asset.id)

        self.assertEqual(asset.latname,
                         'Public Joint-Stock Company "Zapsibgazprom" otkrytogo '
                         'akcionernogo obshhestva "Gazprom"')
        self.assertEqual(asset.secid, 'zsgpp')
        self.assertEqual(asset.isin, 'RU0006752862')
        self.assertEqual(asset.name, 'ОАО "Запсибгазпром"')

        self.assertEqual(asset.currency, 'RUB')
        self.assertEqual(asset.issuedate, None)

        self.assertEqual(asset.isqualifiedinvestors, False)
        self.assertEqual(asset.morningsession, False)
        self.assertEqual(asset.eveningsession, False)

        self.assertEqual(asset.type, 'preferred_share')
        self.assertEqual(asset.typename, 'Акция привилегированная')
        self.assertEqual(asset.group, 'stock_shares')
        self.assertEqual(asset.groupname, 'Акции')

        self.assertEqual(asset.primary_boardid, 'expected_board_id')

        self.assertTrue(asset.latest_accrual_update)
        self.assertEqual(len(asset.dividend_set.all()), 1)
        self.assertEqual(
            asset.dividend_set.get(date='2022-05-08').amount, Decimal('14.4'))

        self.assertEqual(len(asset.assetshistoricaldata_set.all()), 6)

    @mock.patch(GET_SHARE_DIVIDENDS)
    @mock.patch(GET_BOND_COUPON_HISTORY)
    @mock.patch(GET_ASSET_HISTORY_DATA)
    @mock.patch(GET_ASSET_DESCRIPTION)
    def test_get_or_create_asset_obj_SBER(
            self, mocked_get_asset_description, mocked_get_asset_history_data,
            mocked_get_bond_coupon_history, mocked_get_share_dividends
    ):
        mocked_get_asset_description.return_value = self.description_SBER
        mocked_get_asset_history_data.return_value = self.share_history_data
        mocked_get_bond_coupon_history.return_value = None
        mocked_get_share_dividends.return_value = self.share_accrual_data

        asset = get_or_create_asset_obj('Ticker', 'expected_board_id')

        self.assertTrue(isinstance(asset, Asset))
        self.assertEqual(asset.get_related_object().id, asset.id)

        self.assertEqual(asset.latname, 'Sberbank')
        self.assertEqual(asset.secid, 'SBER')
        self.assertEqual(asset.isin, 'RU0009029540')
        self.assertEqual(asset.name, 'Сбербанк')

        self.assertEqual(asset.currency, 'RUR')
        self.assertEqual(
            asset.issuedate, datetime(year=2007, month=7, day=20).date())

        self.assertEqual(asset.isqualifiedinvestors, False)
        self.assertEqual(asset.morningsession, True)
        self.assertEqual(asset.eveningsession, True)

        self.assertEqual(asset.type, 'common_share')
        self.assertEqual(asset.typename, 'Акция обыкновенная')
        self.assertEqual(asset.group, 'stock_shares')
        self.assertEqual(asset.groupname, 'Акции')

        self.assertEqual(asset.primary_boardid, 'expected_board_id')

        self.assertTrue(asset.latest_accrual_update)
        self.assertEqual(len(asset.dividend_set.all()), 4)
        self.assertEqual(
            asset.dividend_set.get(date='2022-11-14').amount,
            Decimal('5.16'))

        self.assertEqual(len(asset.assetshistoricaldata_set.all()), 6)

    def test_get_current_asset_price_share_rub(self):
        result = get_current_asset_price_per_asset(self.share_POSI)
        self.assertEqual(result, Decimal('1715.4'))

    @patch(GET_CURRENCY_RATE_DATETIME)
    def test_get_current_asset_price_share_usd(self, mocked_datetime):
        mocked_datetime.return_value = datetime(
            year=2023, month=5, day=18)

        result = get_current_asset_price_per_asset(
            self.share_POSI, currency='USD')
        self.assertEqual(result, Decimal('21.2396'))

    def test_get_current_asset_price_bond_rub(self):
        result = get_current_asset_price_per_asset(self.bond1)
        self.assertEqual(result, Decimal('993.47'))

    @patch(GET_CURRENCY_RATE_DATETIME)
    def test_get_current_asset_price_bond_usd(self, mocked_datetime):
        mocked_datetime.return_value = datetime(
            year=2023, month=5, day=20)

        result = get_current_asset_price_per_asset(
            self.bond1, currency='USD')
        self.assertEqual(result, Decimal('12.3009'))
