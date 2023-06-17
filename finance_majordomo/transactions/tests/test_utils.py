from _decimal import Decimal
import requests_mock

from ..models import Transaction
from .setting import SettingsTransactions
from ..utils import get_quantity, get_purchase_price, get_average_purchase_price


class TestTransactionsUtils(SettingsTransactions):

    def setUp(self):

        self.transacton_id_2 = Transaction.objects.create(
            transaction_type='BUY',
            asset_type='STOCK',
            user=self.user_authenticated,
            ticker=self.stock_id_3,
            date='2018-01-01',
            price='100',
            quantity=4
        )

        self.transacton_id_3 = Transaction.objects.create(
            transaction_type='SELL',
            asset_type='STOCK',
            user=self.user_authenticated,
            ticker=self.stock_id_3,
            date='2019-01-01',
            price='120',
            quantity=3
        )

        self.transacton_id_4 = Transaction.objects.create(
            transaction_type='BUY',
            asset_type='STOCK',
            user=self.user_authenticated,
            ticker=self.stock_id_3,
            date='2020-01-01',
            price='80',
            quantity=2
        )

        self.transacton_id_5 = Transaction.objects.create(
            transaction_type='SELL',
            asset_type='STOCK',
            user=self.user_authenticated,
            ticker=self.stock_id_3,
            date='2021-01-01',
            price='200',
            quantity=1
        )

    def test_get_quantity(self):

        with requests_mock.Mocker() as r:

            r.user = self.user_authenticated

            result = get_quantity(r, self.stock_id_3)

            self.assertEqual(result, 2)
            self.assertTrue(isinstance(result, int))

            result = get_quantity(r, self.stock_id_3, date='2019-01-01')

            self.assertEqual(result, 1)
            self.assertTrue(isinstance(result, int))

            result = get_quantity(r, self.stock_id_3, date='2018-12-31')

            self.assertEqual(result, 4)
            self.assertTrue(isinstance(result, int))

    #Stopped raise of ValueError for now
    # def test_get_quantity_value_error_1(self):
    # 
    #     with requests_mock.Mocker() as r:
    # 
    #         r.user = self.user_authenticated
    # 
    #         self.transacton_value_error_1 = Transaction.objects.create(
    #             transaction_type='SELL',
    #             asset_type='STOCK',
    #             user=self.user_authenticated,
    #             ticker=self.stock_id_3,
    #             date='2019-12-31',
    #             price='200',
    #             quantity=100
    #         )
    # 
    #         with self.assertRaises(ValueError):
    #             get_quantity(r, self.stock_id_3, date='2020-01-01')
    # 
    # def test_get_quantity_value_error_2(self):
    # 
    #     with requests_mock.Mocker() as r:
    # 
    #         r.user = self.user_authenticated
    # 
    #         self.transacton_value_error_2 = Transaction.objects.create(
    #             transaction_type='SELL',
    #             asset_type='STOCK',
    #             user=self.user_authenticated,
    #             ticker=self.stock_id_3,
    #             date='2005-12-31',
    #             price='200',
    #             quantity=100
    #         )
    # 
    #         with self.assertRaises(ValueError):
    #             get_quantity(r, self.stock_id_3, date='2020-01-01')

    def test_get_purchase_price_1(self):
        with requests_mock.Mocker() as r:

            r.user = self.user_authenticated

            result = get_purchase_price(r, self.stock_id_3)

            self.assertTrue(isinstance(result, Decimal))
            self.assertEqual(result, Decimal(160))

    def test_get_purchase_price_2(self):

        Transaction.objects.last().delete()

        with requests_mock.Mocker() as r:

            r.user = self.user_authenticated

            result = get_purchase_price(r, self.stock_id_3)

            self.assertTrue(isinstance(result, Decimal))
            self.assertEqual(result, Decimal(260))

    def test_get_average_purchase_price(self):

        Transaction.objects.last().delete()

        with requests_mock.Mocker() as r:

            r.user = self.user_authenticated

            result = get_average_purchase_price(r, self.stock_id_3)

            self.assertTrue(isinstance(result, Decimal))
            self.assertEqual(result, Decimal(Decimal(260) / 3))

            result = get_average_purchase_price(
                r, self.stock_id_3, date='2018-06-01')

            self.assertTrue(isinstance(result, Decimal))
            self.assertEqual(result, Decimal(100))
 