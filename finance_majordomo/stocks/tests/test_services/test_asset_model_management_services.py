import json
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import requests_mock
from django.db.models import Sum
import django.db.utils
import simplejson
from unittest import mock
from django.core.exceptions import ValidationError


from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.models.accrual_models import Dividend, \
    AccrualsOfPortfolio
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    execute_toggle_portfolio_accrual_service, \
    execute_accrual_model_data_filling_service, \
    execute_update_accruals_of_portfolio
from finance_majordomo.stocks.services.asset_services.asset_model_management_services import \
    get_or_create_asset_obj
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.stocks.tests.test_services.conftest import \
    AssetServicesFixtureSetUp
from finance_majordomo.users.models import Portfolio

FIXTURES_FOLDER = "fixtures"

GET_ASSET_HISTORY_DATA = "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_asset_history_data"

GET_BOND_COUPON_HISTORY = "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_bond_coupon_history"

GET_SHARE_DIVIDENDS = "finance_majordomo.stocks.services.asset_services." \
    "asset_model_management_services.get_share_dividends"

GET_ASSET_DESCRIPTION = "finance_majordomo.stocks.services.asset_services." \
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
            asset.dividend_set.get(date='2022-11-14').amount, Decimal('5.16'))

        self.assertEqual(len(asset.assetshistoricaldata_set.all()), 6)
