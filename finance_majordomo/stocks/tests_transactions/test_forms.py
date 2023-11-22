import requests_mock

from .setting import SettingsTransactions
from finance_majordomo.stocks.forms.forms import TransactionForm
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models import Stock


class UserFormTest(SettingsTransactions):

    def test_transaction_form_ticker_choice_GET_no_params(self):
        with requests_mock.Mocker() as request:
            request.method = "GET"
            request.user = self.user_authenticated

            form = TransactionForm(request=request)

            choices = form.fields['ticker'].choices

            users_stocks = \
                self.user_authenticated.stocksofuser_set.values_list('stock')

            self.assertEqual(form.fields['ticker'].initial, None)
            self.assertEqual(len(choices) - 1, len(users_stocks))
            for asset_id in users_stocks:
                asset = Stock.objects.get(id=asset_id[0])
                self.assertIn((asset.id, str(asset)), choices)

    def test_transaction_form_ticker_choice_GET_asset_SECID_param(self):
        with requests_mock.Mocker() as request:
            request.method = "GET"
            request.user = self.user_authenticated

            # user has no such asset yet:
            asset_query = Stock.objects.filter(id=2)

            form = TransactionForm(request=request, asset=asset_query)

            choices = form.fields['ticker'].choices

            users_stocks = \
                self.user_authenticated.stocksofuser_set.values_list(
                    'stock')

            self.assertEqual(len(choices) - 1, len(users_stocks) + 1)
            self.assertIn((asset_query[0].id, str(asset_query[0])), choices)
            for asset_id in users_stocks:
                asset = Stock.objects.get(id=asset_id[0])
                self.assertIn((asset.id, str(asset)), choices)

    def test_transaction_form_GET(self):

        with requests_mock.Mocker() as request:
            request.method = "GET"
            request.user = self.user_authenticated

            form = TransactionForm(request=request, data={
                'transaction_type': 'BUY',
                'asset_type': 'STOCK',
                'ticker': self.stock_id_1,
                'date': '2010-12-31',
                'price': '10',
                'quantity': 1
            })

            self.assertTrue(form.is_valid())

    def test_valid_transaction_form(self):

        with requests_mock.Mocker() as request:
            request.method = "GET"
            request.user = self.user_authenticated

            form = TransactionForm(request=request, data={
                'transaction_type': 'SELL',
                'asset_type': 'STOCK',
                'ticker': self.stock_id_1,
                'date': '2010-12-31',
                'price': '1000',
                'quantity': 1
            })

            self.assertTrue(form.is_valid())

    def test_invalid_transaction_form(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(request=request, data={
                'transaction_type': None,
                'asset_type': 'NO_TYPE',
                'ticker': self.stock_id_1,
                'date': '1990-12-31',
                'price': '-10',
                'quantity': -1
            })

            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 5)
            self.assertTrue(
                _("Price must be more than 0") in form.errors['price'])
            self.assertTrue(
                'Select a valid choice. '
                'NO_TYPE is not one of the available choices.'
                in form.errors['asset_type'])
            self.assertTrue(
                'This field is required.' in form.errors['transaction_type'])
            self.assertTrue(
                _('The stock started trading after the specified'
                  ' date') + ' (2000-01-01)' in form.errors['date'])
            self.assertTrue(
                _('Quantity must be more than 0') in form.errors['quantity'])

    def test_invalid_transaction_form_with_valid_data_1(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(request=request, data={
                'transaction_type': 'SELL',
                'asset_type': 'STOCK',
                'user': self.user_authenticated,
                'ticker': self.stock_id_1,
                'date': '2010-12-31',
                'price': '1000',
                'quantity': 1000  # The sale on this quantity make total < 0
            })

            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertTrue(
                _("Such a SELL would raise a short sale situation. "
                  "Short sales are not supported! "
                  "Please check the transaction type, date and quantity")
                in form.errors['__all__'])

    def test_invalid_transaction_form_with_valid_data_2(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(request=request, data={
                'transaction_type': 'SELL',
                'asset_type': 'STOCK',
                'user': self.user_authenticated,
                'ticker': self.stock_id_3,
                'date': '2019-12-31',  # The sale on this date make total < 0
                'price': '1000',
                'quantity': 1
            })

            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertTrue(
                _("Such a SELL would raise a short sale situation. "
                  "Short sales are not supported! "
                  "Please check the transaction type, date and quantity")
                in form.errors['__all__'])
