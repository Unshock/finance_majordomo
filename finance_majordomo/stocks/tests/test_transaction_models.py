from decimal import Decimal, InvalidOperation
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.users.models import User, Portfolio


class TransactionsModelsTest(BaseTest):

    def test_models_params(self):

        transaction_1 = Transaction.objects.get(id=1)
        transaction_3 = Transaction.objects.get(id=3)

        self.assertEqual(transaction_1.asset.id, 30)
        self.assertEqual(transaction_1.date, date(2023, 4, 15))
        self.assertEqual(transaction_1.price, Decimal('1000'))
        self.assertEqual(transaction_1.transaction_type, 'BUY')
        self.assertEqual(transaction_1.fee, Decimal('0'))
        self.assertEqual(transaction_1.accrued_interest, None)
        self.assertEqual(transaction_3.accrued_interest, Decimal('20'))

        self.assertEqual(Transaction.objects.count(), 3)
        self.assertEqual(
            transaction_1._meta.get_field('date').verbose_name,
            _("Transaction date"))
        self.assertEqual(
            transaction_1._meta.get_field('quantity').verbose_name,
            _("Transaction quantity"))
        self.assertEqual(
            transaction_1._meta.get_field('creation_date').verbose_name,
            _("Creation date"))

        self.assertEqual(
            str(transaction_1),
            'BUY x5.00 POSI for 1000.00 on 2023-04-15'
        )

    def test_price_validation_fail_1(self):
        price_invalid = "not decimal"  # invalid Decimal format

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price=price_invalid,
                quantity=1,
                date='2020-03-02',
                asset=Asset.objects.get(id=30),
                portfolio=Portfolio.objects.get(id=2)
            )

    def test_price_validation_fail_2(self):
        price_invalid = '100,10'  # invalid Decimal format

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price=price_invalid,
                quantity=1,
                date='2020-03-02',
                asset=Asset.objects.get(id=30),
                portfolio=Portfolio.objects.get(id=2)
            )

    # why InvalidOperation not ValidationError?
    def test_price_validation_fail_3(self):
        price_invalid = 123456789

        with self.assertRaises(InvalidOperation):
            Transaction.objects.create(
                price=price_invalid,
                quantity=1,
                date='2020-03-02',
                asset=Asset.objects.get(id=30),
                portfolio=Portfolio.objects.get(id=2)
            )

    def test_date_validation_fail_1(self):
        date_invalid = '2020-02-30'  # there is no 30 Feb

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price='11',
                quantity=1,
                date=date_invalid,
                asset=Asset.objects.get(id=30),
                portfolio=Portfolio.objects.get(id=2)
            )

    def test_date_validation_fail_2(self):
        date_invalid = '10-10-2020'  # format is invalid

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price='11',
                quantity=1,
                date=date_invalid,
                asset=Asset.objects.get(id=30),
                portfolio=Portfolio.objects.get(id=2)
            )
