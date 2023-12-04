import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from django.db.models import Sum
import django.db.utils
import simplejson
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models.accrual_models import Dividend, \
    AccrualsOfPortfolio
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    execute_toggle_portfolio_accrual_service, \
    execute_accrual_model_data_filling_service
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.users.models import Portfolio

FIXTURES_FOLDER = "fixtures"

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

    def test_execute_accrual_model_data_filling_service(self):

        valid_dividend_data_dict = simplejson.load(
            open(
                os.path.join(
                    os.path.dirname(__file__),
                    FIXTURES_FOLDER,
                    "POSI_dividend_data.json"),
                'r'), use_decimal=True)

        self.assertEqual(len(self.share_POSI.dividend_set.all()), 1)
        self.assertEqual(
            self.share_POSI.dividend_set.all()
                .aggregate(Sum('amount')).get('amount__sum'),
            Decimal('37.87')
        )

        execute_accrual_model_data_filling_service(
            self.share_POSI, valid_dividend_data_dict)

        self.assertEqual(
            self.share_POSI.latest_accrual_update.date(),
            datetime.today().date()
        )
        self.assertEqual(len(self.share_POSI.dividend_set.all()), 4)
        self.assertEqual(
            self.share_POSI.dividend_set.all()
                .aggregate(Sum('amount')).get('amount__sum'), Decimal('73.23'))

        self.assertEqual(Dividend.objects.get(
            date='2022-05-08', asset=self.share_POSI).amount, Decimal('14.4'))
