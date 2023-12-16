import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from django.db.models import Sum
import django.db.utils
import simplejson
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from unittest.mock import patch
from finance_majordomo.stocks.models.accrual_models import Dividend, \
    AccrualsOfPortfolio
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    execute_toggle_portfolio_accrual_service, \
    execute_accrual_model_data_filling_service, \
    execute_update_accruals_of_portfolio
from finance_majordomo.stocks.services.accrual_services.dividend_view_services import \
    execute_portfolio_accrual_view_context_service, AccrualItem
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.users.models import Portfolio

FIXTURES_FOLDER = "fixtures"

EXECUTE_PORTFOLIO_ACCRUAL_VIEW_SERVICE_DATETIME = \
    "finance_majordomo.stocks.services.accrual_services." \
    "dividend_view_services.datetime"


class AccrualViewServicesTest(BaseTest):

    def test_execute_portfolio_accrual_view_context_service_90_days(self):
        portfolio_accrual_data = execute_portfolio_accrual_view_context_service(
            portfolio=self.user_authenticated.get_current_portfolio(),
            days_delta=90
        )

        self.assertEqual(
            portfolio_accrual_data['total_results']['total_divs_payable'],
            Decimal('235.15')
        )
        self.assertEqual(
            portfolio_accrual_data['total_results']['total_divs_received'],
            Decimal('35.40')
        )
        self.assertEqual(
            portfolio_accrual_data['total_results']['total_divs_upcoming'],
            Decimal('0.0')
        )
        self.assertEqual(
            len(portfolio_accrual_data['accrual_list']), 3
        )

        acc1, _, acc3 = portfolio_accrual_data['accrual_list']

        self.assertTrue(isinstance(acc1, AccrualItem))
        self.assertEqual(acc1.asset_name, self.bond1.latname)
        self.assertEqual(acc1.asset_quantity, Decimal('1'))
        self.assertEqual(acc1.id, 3)
        self.assertEqual(acc1.amount, Decimal('10.40'))
        self.assertEqual(acc1.sum, Decimal('10.40'))
        self.assertEqual(acc1.date, datetime(year=2023, month=5, day=18).date())
        self.assertFalse(acc1.is_received)
        self.assertFalse(acc1.is_upcoming)

        self.assertEqual(acc3.asset_name, self.share_POSI.latname)
        self.assertEqual(acc3.date, datetime(year=2023, month=4, day=16).date())

    @patch(EXECUTE_PORTFOLIO_ACCRUAL_VIEW_SERVICE_DATETIME)
    def test_execute_portfolio_accrual_view_context_service_3_days(
            self, mocked_datetime):

        mocked_datetime.today.return_value = datetime(
            year=2023, month=4, day=18)

        portfolio_accrual_data = execute_portfolio_accrual_view_context_service(
            portfolio=self.user_authenticated.get_current_portfolio(),
            days_delta=3
        )

        self.assertEqual(
            portfolio_accrual_data['total_results']['total_divs_payable'],
            Decimal('189.35')
        )
        self.assertEqual(
            portfolio_accrual_data['total_results']['total_divs_received'],
            Decimal('0.0')
        )
        self.assertEqual(
            portfolio_accrual_data['total_results']['total_divs_upcoming'],
            Decimal('35.40')
        )
        self.assertEqual(len(portfolio_accrual_data['accrual_list']), 2)

        acc1, acc2 = portfolio_accrual_data['accrual_list']

        self.assertTrue(isinstance(acc1, AccrualItem))
        self.assertEqual(acc1.asset_name, self.bond1.latname)
        self.assertEqual(acc1.asset_quantity, Decimal('1'))
        self.assertEqual(acc1.id, 2)
        self.assertEqual(acc1.amount, Decimal('35.40'))
        self.assertEqual(acc1.sum, Decimal('35.40'))
        self.assertEqual(acc1.date, datetime(year=2023, month=4, day=19).date())

        # synthetic situation - in reality can not be received and upcoming
        self.assertTrue(acc1.is_received)
        self.assertTrue(acc1.is_upcoming)

        self.assertEqual(acc2.asset_name, self.share_POSI.latname)
        self.assertEqual(acc2.date, datetime(year=2023, month=4, day=16).date())

    def test_execute_portfolio_accrual_view_context_service_empty_portfolio(
            self):

        portfolio_accrual_data = execute_portfolio_accrual_view_context_service(
            portfolio=self.user_authenticated_no_assets.get_current_portfolio(),
            days_delta=90
        )

        self.assertEqual(
            portfolio_accrual_data['total_results'].get('total_divs_payable'),
            None
        )
        self.assertEqual(
            portfolio_accrual_data['total_results'].get('total_divs_received'),
            None
        )
        self.assertEqual(
            portfolio_accrual_data['total_results'].get('total_divs_upcoming'),
            None
        )
        self.assertEqual(len(portfolio_accrual_data['accrual_list']), 0)
