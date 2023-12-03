from datetime import date
from decimal import Decimal, InvalidOperation

import django.db.utils
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models.accrual_models import Dividend, \
    AccrualsOfPortfolio
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    execute_toggle_portfolio_accrual_service
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.users.models import Portfolio


class AccrualModelManagementServicesTest(BaseTest):

    def test_execute_toggle_portfolio_accrual_service(self):
        portfolio = self.user_authenticated.get_current_portfolio()
        accrual = self.accrual1

        accrual_of_portfolio = AccrualsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=accrual)
        self.assertFalse(accrual_of_portfolio.is_received)

        execute_toggle_portfolio_accrual_service(accrual, portfolio)

        accrual_of_portfolio = AccrualsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=accrual)
        self.assertTrue(accrual_of_portfolio.is_received)

        execute_toggle_portfolio_accrual_service(accrual, portfolio)

        accrual_of_portfolio = AccrualsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=accrual)
        self.assertFalse(accrual_of_portfolio.is_received)
