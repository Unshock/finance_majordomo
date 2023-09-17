import decimal

import django.db.utils
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ..models import Transaction
from .setting import SettingsTransactions


class TransactionsModelsTest(SettingsTransactions):

    def test_models_params(self):
        self.assertEqual(self.transaction_id_1.ticker_id, 1)
        self.assertEqual(self.transaction_id_1.date, "1999-12-31")
        self.assertEqual(self.transaction_id_1.price, "10")
        self.assertEqual(self.transaction_id_1.fee, '0.00')
        self.assertEqual(Transaction.objects.count(), 7)
        self.assertEqual(
            self.transaction_id_5._meta.get_field('date').verbose_name,
            _("Transaction date"))
        self.assertEqual(
            self.transaction_id_5._meta.get_field('quantity').verbose_name,
            _("Transaction quantity"))
        self.assertEqual(
            self.transaction_id_5._meta.get_field('creation_date').verbose_name,
            _("Creation date"))

    def test_price_validation_fail_1(self):
        price_invalid = "not decimal"

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price=price_invalid,
                quantity=1,
                date='2020-03-02',
                ticker=self.stock_id_1,
                user=self.user_authenticated
            )

    def test_price_validation_fail_2(self):
        price_invalid = '100,10'

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price=price_invalid,
                quantity=1,
                date='2020-03-02',
                ticker=self.stock_id_1,
                user=self.user_authenticated
            )

    # why InvalidOperation not ValidationError?
    def test_price_validation_fail_3(self):
        price_invalid = 123456789

        with self.assertRaises(decimal.InvalidOperation):
            Transaction.objects.create(
                price=price_invalid,
                quantity=1,
                date='2020-03-02',
                ticker=self.stock_id_1,
                user=self.user_authenticated
            )

    def test_date_validation_fail_1(self):
        date_invalid = '2020-02-30'

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price='11',
                quantity=1,
                date=date_invalid,
                ticker=self.stock_id_1,
                user=self.user_authenticated
            )

    def test_date_validation_fail_2(self):
        date_invalid = '10-10-2020'

        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                price='11',
                quantity=1,
                date=date_invalid,
                ticker=self.stock_id_1,
                user=self.user_authenticated
            )
