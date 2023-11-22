import decimal

import django.db.utils
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models.models import Dividend, DividendsOfUser
from .setting import SettingsDividends


class DividendsModelsTest(SettingsDividends):

    def test_models_params(self):
        self.assertEqual(self.dividend_id_1.stock_id, 1)
        self.assertEqual(self.dividend_id_1.date, "2000-01-01")
        self.assertEqual(self.dividend_id_1.amount, "24.36")
        self.assertEqual(Dividend.objects.count(), 2)
        self.assertEqual(
            self.dividend_id_1._meta.get_field('date').verbose_name,
            _("Dividend date"))
        self.assertEqual(
            self.dividend_id_1._meta.get_field('amount').verbose_name,
            _("Dividend amount for one share"))
        self.assertEqual(
            self.dividend_id_1._meta.get_field('creation_date').verbose_name,
            _("Creation date"))

    def test_amount_validation_fail_1(self):
        amount_invalid = "not decimal"
        with self.assertRaises(ValidationError):
            Dividend.objects.create(
                amount=amount_invalid,
                date='2020-03-02',
                stock_id=3
            )

    def test_amount_validation_fail_2(self):
        amount_invalid = '100,10'

        with self.assertRaises(ValidationError):
            Dividend.objects.create(
                amount=amount_invalid,
                date='2020-03-02',
                stock_id=3
            )

    # why InvalidOperation not ValidationError?
    def test_amount_validation_fail_3(self):
        amount_invalid = 100500600

        with self.assertRaises(decimal.InvalidOperation):
            Dividend.objects.create(
                amount=amount_invalid,
                date='2020-03-02',
                stock_id=3
            )

    def test_date_validation_fail_1(self):
        date_invalid = '100,10'

        with self.assertRaises(ValidationError):
            Dividend.objects.create(
                amount=1,
                date=date_invalid,
                stock_id=3
            )

    def test_date_validation_fail_2(self):
        date_invalid = '10-10-2020'

        with self.assertRaises(ValidationError):
            Dividend.objects.create(
                amount=1,
                date=date_invalid,
                stock_id=3
            )


class DividendsOfUserModelsTest(SettingsDividends):

    def test_models_params(self):
        self.assertEqual(
            self.dividend_of_user_id_1.user.username, "user_authenticated")
        self.assertEqual(
            self.dividend_of_user_id_1.dividend.date, "2000-01-01")
        self.assertEqual(
            self.dividend_of_user_id_1.is_received, False)
        self.assertEqual(
            self.dividend_of_user_id_1._meta.get_field(
                'is_received').verbose_name, _("Dividend status"))
        self.assertEqual(DividendsOfUser.objects.count(), 2)

    def test_is_received_validation_fail_1(self):
        is_received_invalid = 'false'

        with self.assertRaises(ValidationError):
            DividendsOfUser.objects.create(
                user=self.user_authenticated,
                dividend=self.dividend_id_1,
                is_received=is_received_invalid
            )

    def test_unique_together(self):

        with self.assertRaises(django.db.utils.IntegrityError):
            DividendsOfUser.objects.create(
                user=self.user_authenticated,
                dividend=self.dividend_id_1,
            )

            DividendsOfUser.objects.create(
                user=self.user_authenticated,
                dividend=self.dividend_id_1,
            )






