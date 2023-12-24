from datetime import date
from decimal import Decimal, InvalidOperation

import django.db.utils
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models.accrual_models import Accrual, \
    AccrualsOfPortfolio
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.users.models import Portfolio


class DividendsModelsTest(BaseTest):

    def test_models_params(self):

        accrual_1 = Accrual.objects.get(id=1)

        self.assertEqual(accrual_1.asset.id, 30)
        self.assertEqual(
            accrual_1.date, date(2023, 4, 16)
        )
        self.assertEqual(accrual_1.amount, Decimal("37.87"))
        self.assertEqual(Accrual.objects.count(), 3)
        self.assertEqual(
            accrual_1._meta.get_field('date').verbose_name,
            _("Accrual date"))
        self.assertEqual(
            accrual_1._meta.get_field('amount').verbose_name,
            _("Accrual amount for one asset"))
        self.assertEqual(
            accrual_1._meta.get_field('creation_date').verbose_name,
            _("Creation date"))

    def test_amount_validation_fail_1(self):
        amount_invalid = "not decimal"
        with self.assertRaises(ValidationError):
            try:
                Accrual.objects.create(
                    amount=amount_invalid,
                    date='2020-03-02',
                    asset_id=30
                )
            except Exception as e:
                #print(e)
                raise e

    def test_amount_validation_fail_2(self):
        amount_invalid = '100,10'

        with self.assertRaises(ValidationError):
            try:
                Accrual.objects.create(
                    amount=amount_invalid,
                    date='2020-03-02',
                    asset_id=30
                )
            except Exception as e:
                #print(e)
                raise e

    # why InvalidOperation not ValidationError?
    def test_amount_validation_fail_3(self):
        amount_invalid = 100500600

        with self.assertRaises(InvalidOperation):
            Accrual.objects.create(
                amount=amount_invalid,
                date='2020-03-02',
                asset_id=30
            )


    def test_date_validation_fail_1(self):
        date_invalid = '100,10'

        with self.assertRaises(ValidationError):
            Accrual.objects.create(
                amount=1,
                date=date_invalid,
                asset_id=30
            )


    def test_date_validation_fail_2(self):
        date_invalid = '10-10-2020'

        with self.assertRaises(ValidationError):
            Accrual.objects.create(
                amount=1,
                date=date_invalid,
                asset_id=30
            )


class AccrualsOfPortfolioModelsTest(BaseTest):

    def test_models_params(self):

        accrual_of_portfolio = AccrualsOfPortfolio.objects.get(id=1)

        self.assertEqual(
            accrual_of_portfolio.portfolio.user.username, "user1")
        self.assertEqual(
            accrual_of_portfolio.accrual.date, date(2023, 4, 16))
        self.assertEqual(
            accrual_of_portfolio.is_received, False)
        self.assertEqual(
            accrual_of_portfolio._meta.get_field(
                'is_received').verbose_name, _("Accrual status"))
        self.assertEqual(AccrualsOfPortfolio.objects.count(), 3)

    def test_is_received_validation_fail_1(self):
        is_received_invalid = 'false'
        with self.assertRaises(ValidationError):
            AccrualsOfPortfolio.objects.create(
                portfolio=Portfolio.objects.get(id=3),
                accrual=Accrual.objects.get(id=3),
                is_received=is_received_invalid
            )

    def test_unique_together(self):

        with self.assertRaises(django.db.utils.IntegrityError):
            AccrualsOfPortfolio.objects.create(
                portfolio=Portfolio.objects.get(id=3),
                accrual=Accrual.objects.get(id=3)
            )

            AccrualsOfPortfolio.objects.create(
                portfolio=Portfolio.objects.get(id=3),
                accrual=Accrual.objects.get(id=3)
            )
