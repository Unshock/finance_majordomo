from django.test import TestCase
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
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.forms.transaction_forms import TransactionForm
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
from finance_majordomo.users.models import Portfolio

FIXTURES_FOLDER = "fixtures"

DESCRIPTION_LQDT = 'get_stock_description_LQDT.json'
DESCRIPTION_RU000A0JTW83 = 'get_stock_description_RU000A0JTW83.json'
DESCRIPTION_SBER = 'get_stock_description_SBER.json'
DESCRIPTION_SU26222RMFS8 = 'get_stock_description_SU26222RMFS8.json'
DESCRIPTION_ZSGPP = 'get_stock_description_ZSGPP.json'

SHARE_ACCRUAL_DATA = 'POSI_dividend_data.json'
BOND_ACCRUAL_DATA = 'bond_accrual_data.json'

SHARE_HISTORY_DATA = 'get_asset_history_data_SHARE.json'
BOND_HISTORY_DATA = 'get_asset_history_data_BOND.json'


class AssetServicesFixtureSetUp(TestCase):

    def setUp(self):
        self.description_LQDT = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, DESCRIPTION_LQDT),
                'r')
        )

        self.description_RU000A0JTW83 = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER,
                DESCRIPTION_RU000A0JTW83),
                'r')
        )

        self.description_SBER = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, DESCRIPTION_SBER),
                'r')
        )

        self.description_SU26222RMFS8 = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER,
                DESCRIPTION_SU26222RMFS8),
                'r')
        )

        self.description_ZSGPP = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, DESCRIPTION_ZSGPP),
                'r')
        )

        self.share_accrual_data = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, SHARE_ACCRUAL_DATA),
                'r')
        )

        self.bond_accrual_data = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, BOND_ACCRUAL_DATA),
                'r')
        )

        self.share_history_data = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, SHARE_HISTORY_DATA),
                'r')
        )

        self.bond_history_data = json.load(
            open(os.path.join(
                os.path.dirname(__file__), FIXTURES_FOLDER, BOND_HISTORY_DATA),
                'r')
        )


class ExtraTransactionsSetUp(TestCase):
    def setUp(self):
        self.transaction_extra_1 = Transaction.objects.create(
            asset_id=30,
            transaction_type='SELL',
            portfolio_id=2,
            price=Decimal('900.00'),
            accrued_interest=None,
            quantity=Decimal('3'),
            date=datetime(year=2023, month=4, day=20)
        )

        self.transaction_extra_2 = Transaction.objects.create(
            asset_id=30,
            transaction_type='BUY',
            portfolio_id=2,
            price=Decimal('2000.00'),
            accrued_interest=None,
            quantity=Decimal('2'),
            date=datetime(year=2023, month=4, day=23)
        )

        self.transaction_extra_3 = Transaction.objects.create(
            asset_id=30,
            transaction_type='SELL',
            portfolio_id=2,
            price=Decimal('5000.00'),
            accrued_interest=None,
            quantity=Decimal('3'),
            date=datetime(year=2023, month=4, day=24)
        )

        self.transaction_extra_4 = Transaction.objects.create(
            asset_id=31,
            transaction_type='SELL',
            portfolio_id=2,
            price=Decimal('2000.00'),
            accrued_interest=None,
            quantity=Decimal('1'),
            date=datetime(year=2023, month=4, day=25)
        )
