from decimal import Decimal
import requests_mock
from .base_settings import BaseTest
from finance_majordomo.stocks.forms.transaction_forms import TransactionForm
from django.utils.translation import gettext_lazy as _


class TransactionFormTest(BaseTest):

    # def test_transaction_form_ticker_choice_GET_no_params(self):
    #     with requests_mock.Mocker() as request:
    #         request.method = "GET"
    #         request.user = self.client_authenticated
    # 
    #         form = TransactionForm(request=request)
    # 
    #         choices = form.fields['asset'].choices
    # 
    #         users_stocks = \
    #             self.user_authenticated.assetsofuser_set.values_list('asset')
    # 
    #         self.assertEqual(form.fields['asset'].initial, None)
    #         self.assertEqual(len(choices) - 1, len(users_stocks))
    #         for asset_id in users_stocks:
    #             asset = Stock.objects.get(id=asset_id[0])
    #             self.assertIn((asset.id, str(asset)), choices)
    # 
    # def test_transaction_form_ticker_choice_GET_asset_SECID_param(self):
    #     with requests_mock.Mocker() as request:
    #         request.method = "GET"
    #         request.user = self.user_authenticated
    # 
    #         # user has no such asset yet:
    #         asset_query = Stock.objects.filter(id=2)
    # 
    #         form = TransactionForm(request=request, asset=asset_query)
    # 
    #         choices = form.fields['ticker'].choices
    # 
    #         users_stocks = \
    #             self.user_authenticated.stocksofuser_set.values_list(
    #                 'stock')
    # 
    #         self.assertEqual(len(choices) - 1, len(users_stocks) + 1)
    #         self.assertIn((asset_query[0].id, str(asset_query[0])), choices)
    #         for asset_id in users_stocks:
    #             asset = Stock.objects.get(id=asset_id[0])
    #             self.assertIn((asset.id, str(asset)), choices)

    def test_valid_transaction_form_buy_GET(self):

        with requests_mock.Mocker() as request:
            request.method = "GET"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=self.user_authenticated,
                data={
                    'transaction_type': 'BUY',
                    'asset': self.share1,
                    'date': '2023-10-31',
                    'price': Decimal('2000.3'),
                    'fee': Decimal('2.3'),
                    'quantity': Decimal('1')
                })

            self.assertTrue(form.is_valid())

    def test_valid_transaction_form_buy_POST(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=request.user,
                data={
                    'transaction_type': 'BUY',
                    'asset': self.share1,
                    'date': '2023-10-31',
                    'price': Decimal('2000.3'),
                    'fee': Decimal('2.3'),
                    'quantity': Decimal('1')
                })

            self.assertTrue(form.is_valid())

    def test_valid_transaction_form_sell_GET(self):

        with requests_mock.Mocker() as request:
            request.method = "GET"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=self.user_authenticated,
                data={
                    'transaction_type': 'SELL',
                    'asset': self.share1,
                    'date': '2023-05-17',
                    'price': 1000,
                    'fee': None,
                    'quantity': 1
                })

            self.assertTrue(form.is_valid())

    def test_valid_transaction_form_sell_POST(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=self.user_authenticated,
                data={
                    'transaction_type': 'SELL',
                    'asset': self.share1,
                    'date': '2023-05-17',
                    'price': 1000,
                    'fee': None,
                    'quantity': 1
                })

            self.assertTrue(form.is_valid())

    def test_invalid_transaction_form_invalid_data_POST(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(request=request, data={
                'transaction_type': None,
                'asset': self.bond1,
                'date': '1990-12-31',
                'price': '-10',
                'fee': Decimal('-100'),
                'quantity': -1
            })

            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 5)
            self.assertIn(
                _("Price must be more than 0"), form.errors.get('price')
            )

            self.assertIn(
                'This field is required.', form.errors.get('transaction_type')
            )
            self.assertIn(
                _('The stock started trading after the specified date')
                + ' (2017-05-03)', form.errors.get('date'))
            self.assertIn(
                _('Fee must be more or equal 0'), form.errors.get('fee')
            )
            self.assertIn(
                _('Quantity must be more than 0'), form.errors.get('quantity')
            )

    def test_invalid_transaction_form_with_valid_data_1_POST(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=self.user_authenticated,
                data={
                    'transaction_type': 'SELL',
                    'asset': self.share1,
                    'date': '2023-10-31',
                    'price': '1000',
                    'quantity': 1000  # The sale on this quantity make total < 0
                })

            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertTrue(
                _("Such a SELL would raise a short sale situation. "
                  "Short sales are not supported! "
                  "Please check the transaction type, date and quantity")
                in form.errors.get('__all__'))

    def test_invalid_transaction_form_with_valid_data_2_POST(self):

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=self.user_authenticated,
                data={
                    'transaction_type': 'SELL',
                    'asset': self.share2,
                    'date': '2019-12-31',  # The sale on the date make total < 0
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

    def test_bond_transaction_form_with_empty_accrued_interest(self):

        accrued_err_message = 'message'

        with requests_mock.Mocker() as request:
            request.method = "POST"
            request.user = self.user_authenticated

            form = TransactionForm(
                request=request,
                user=self.user_authenticated,
                accrued_interest_err_message=accrued_err_message,
                data={
                    'transaction_type': 'SELL',
                    'asset': self.bond1,  # bond bun accrued interest is empty
                    'date': '2023-10-31',
                    'price': '1000',
                    'quantity': 1
                })

            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertTrue(accrued_err_message in form.errors['__all__'])
