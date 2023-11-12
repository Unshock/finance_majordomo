from unittest.mock import patch

from .setting import SettingsStocks
from ..forms import StockForm
import mock
from common.utils import stocks
from common.utils.stocks import get_asset_description
#from mocked_utils import mocked_get_stock_description
from .mocked_utils import mocked_get_stock_description
from django.utils.translation import gettext_lazy as _


class TestStockForm(SettingsStocks):

    def test_valid_transaction_form(self):

        name = 'tatn'
        form = StockForm(data={'ticker': name})
        form.clean_ticker = lambda: name

        self.assertTrue(form.is_valid())

    def test_invalid_transaction_form(self):

        name = 'more than 10 symbols'
        form = StockForm(data={'ticker': name})
        form.clean_ticker = lambda: name

        self.assertFalse(form.is_valid())
