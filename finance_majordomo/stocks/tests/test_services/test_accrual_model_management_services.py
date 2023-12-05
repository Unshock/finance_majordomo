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
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    execute_toggle_portfolio_accrual_service, \
    execute_accrual_model_data_filling_service, \
    execute_update_accruals_of_portfolio
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

    def test_execute_update_accruals_of_portfolio_invalid_action_type(self):
        transaction = self.transaction3
        portfolio = self.user_authenticated.get_current_portfolio()

        with self.assertRaises(ValueError):
            execute_update_accruals_of_portfolio(
                portfolio, transaction, action_type='invalid_type')

    def test_execute_update_accruals_of_portfolio_delete_buy(self):
        transaction = self.transaction3
        portfolio = self.user_authenticated.get_current_portfolio()

        Dividend.objects.create(
            asset_id=32,
            date='2023-06-01',
            amount=Decimal('100')
        )

        self.assertTrue(AccrualsOfPortfolio.objects.get(id=2).is_received)
        self.assertFalse(AccrualsOfPortfolio.objects.get(id=3).is_received)
        self.assertEqual(AccrualsOfPortfolio.objects.count(), 3)

        self.accrual_of_portfolio3.is_received = True
        execute_update_accruals_of_portfolio(
            portfolio, transaction, action_type='del_transaction')

        self.assertEqual(AccrualsOfPortfolio.objects.count(), 4)
        accrual_of_portfolio4 = AccrualsOfPortfolio.objects.get(id=4)

        self.assertFalse(AccrualsOfPortfolio.objects.get(id=2).is_received)
        self.assertFalse(AccrualsOfPortfolio.objects.get(id=3).is_received)
        self.assertFalse(accrual_of_portfolio4.is_received)

    def test_execute_update_accruals_of_portfolio_delete_sell(self):

        sell_transaction = Transaction.objects.create(
            transaction_type='SELL',
            portfolio_id=2,
            asset_id=32,
            date='2023-04-15',
            price=Decimal('1'),
            accrued_interest=Decimal('1'),
            quantity=Decimal('1')
        )

        portfolio = self.user_authenticated.get_current_portfolio()

        self.accrual_of_portfolio2.is_received = False
        self.accrual_of_portfolio2.save()

        Dividend.objects.create(
            asset_id=32,
            date='2023-06-01',
            amount=Decimal('100')
        )

        self.assertEqual(AccrualsOfPortfolio.objects.count(), 3)

        execute_update_accruals_of_portfolio(
            portfolio, sell_transaction, action_type='del_transaction')

        self.assertEqual(AccrualsOfPortfolio.objects.count(), 4)
        accrual_of_portfolio4 = AccrualsOfPortfolio.objects.get(id=4)

        self.assertFalse(AccrualsOfPortfolio.objects.get(id=2).is_received)
        self.assertFalse(AccrualsOfPortfolio.objects.get(id=3).is_received)
        self.assertFalse(accrual_of_portfolio4.is_received)

    def test_execute_update_accruals_of_portfolio_add_buy_sell(self):

        sell_transaction = Transaction.objects.create(
            transaction_type='SELL',
            portfolio_id=2,
            asset_id=32,
            date='2023-04-15',
            price=Decimal('1'),
            accrued_interest=Decimal('1'),
            quantity=Decimal('1')
        )

        buy_transaction = Transaction.objects.create(
            transaction_type='BUY',
            portfolio_id=2,
            asset_id=32,
            date='2023-05-20',
            price=Decimal('1'),
            accrued_interest=Decimal('1'),
            quantity=Decimal('1')
        )

        portfolio = self.user_authenticated.get_current_portfolio()

        Dividend.objects.create(
            asset_id=32,
            date='2023-06-01',
            amount=Decimal('100')
        )

        self.assertTrue(AccrualsOfPortfolio.objects.get(id=2).is_received)
        self.assertFalse(AccrualsOfPortfolio.objects.get(id=3).is_received)
        self.assertEqual(AccrualsOfPortfolio.objects.count(), 3)

        execute_update_accruals_of_portfolio(
            portfolio, sell_transaction, action_type='add_transaction')

        execute_update_accruals_of_portfolio(
            portfolio, buy_transaction, action_type='add_transaction')

        self.assertEqual(AccrualsOfPortfolio.objects.count(), 4)
        accrual_of_portfolio4 = AccrualsOfPortfolio.objects.get(id=4)

        self.assertFalse(AccrualsOfPortfolio.objects.get(id=2).is_received)
        self.assertFalse(AccrualsOfPortfolio.objects.get(id=3).is_received)
        self.assertFalse(accrual_of_portfolio4.is_received)
