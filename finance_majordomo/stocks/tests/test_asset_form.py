from .base_settings import BaseTest
from ..forms.asset_forms import StockForm


class TestStockForm(BaseTest):

    def test_valid_transaction_form(self):

        name = 'tatn'
        form = StockForm(data={'ticker': name})
        form.clean_ticker = lambda: name

        self.assertTrue(form.is_valid())

    def test_valid_transaction_form2(self):

        name = 'lsrg'
        form = StockForm(data={'ticker': name})
        #form.clean_ticker = lambda: name

        self.assertFalse(form.is_valid())

    # def test_invalid_transaction_form(self):
    # 
    #     name = 'more than 10 symbols'
    #     form = StockForm(data={'ticker': name})
    #     form.clean_ticker = lambda: name
    # 
    #     self.assertFalse(form.is_valid())
