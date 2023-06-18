from .setting import SettingsStocks
from ..forms import StockForm
import mock
from common.utils.stocks import get_stock_description
#from mocked_utils import mocked_get_stock_description
from .mocked_utils import mocked_get_stock_description
from django.utils.translation import gettext_lazy as _


class TestStockForm(SettingsStocks):

    #@mock.patch('common.utils.stocks.get_stock_description',
    #            side_effect=mocked_get_stock_description)
    #def test_case(self, mocked):
    #    print(get_stock_description('lsng'))  # will print: 'Hey'

    # @mock.patch('common.utils.stocks.get_stock_description',
    #             side_effect=mocked_get_stock_description)
    def test_valid_transaction_form(self):

        with mock.patch('common.utils.stocks.get_stock_description',
                side_effect=mocked_get_stock_description):
            form = StockForm(data={
                'ticker': 'tatnp',
            })

        self.assertTrue(form.is_valid())

    def test_invalid_transaction_form(self):

        form = TransactionForm(data={
            'transaction_type': None,
            'asset_type': 'NO_TYPE',
            'ticker': self.stock_id_1,
            'date': '1990-12-31',
            'price': '-10',
            'quantity': -1
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)
        self.assertTrue(_("Price must be more than 0") in form.errors['price'])
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
