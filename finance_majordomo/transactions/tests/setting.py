import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ...dividends.models import Dividend, DividendsOfUser
from ...stocks.models import Stock, StocksOfUser
from ...transactions.models import Transaction


class SettingsTransactions(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user = get_user_model()

        cls.client_authenticated = Client()
        cls.user_authenticated = user.objects.create(
            username="user_authenticated",
            first_name="Authenticated",
            last_name="UserNotAdmin"
        )
        cls.client_authenticated.force_login(user.objects.last())

        cls.client_authenticated_another = Client()
        cls.user_authenticated_another = user.objects.create(
            username="user_authenticated_another",
            first_name="AuthenticatedAnother",
            last_name="UserNotAdminAnother"
        )
        cls.client_authenticated_another.force_login(user.objects.get(id=2))

        cls.client_unauthenticated = Client()
        cls.user_unauthenticated = user.objects.create(
            username="user_unauthenticated",
            first_name="NotAuthenticated",
            last_name="UserNotAdmin"
        )

        # For models, views tests
        cls.stock_id_1 = Stock.objects.create(
            ticker="LSNG",
            type="common_share",
            isin="isin_id_1",
            latname='lsng',
            issuedate=datetime.date(2000, 1, 1),
            isqualifiedinvestors=False,
            morningsession=False,
            eveningsession=False,
            stock_data={},
        )

        # For models, views tests
        cls.stock_id_2 = Stock.objects.create(
            ticker="LSNGP",
            type="preferred_share",
            isin="isin_id_2",
            latname='lsngp_lat',
            issuedate=datetime.date(2000, 1, 1),
            isqualifiedinvestors=False,
            morningsession=False,
            eveningsession=False,
            stock_data={},
        )

        # For utils tests
        cls.stock_id_3 = Stock.objects.create(
            ticker="TATN",
            type="common_share",
            isin="isin_id_3",
            latname='tatneft',
            issuedate=datetime.date(2000, 1, 1),
            isqualifiedinvestors=False,
            morningsession=False,
            eveningsession=False,
            stock_data={},
        )

        # For utils tests
        cls.stock_id_4 = Stock.objects.create(
            ticker="TATNP",
            type="preferred_share",
            isin="isin_id_4",
            latname='tatnp_lat',
            issuedate=datetime.date(2000, 1, 1),
            isqualifiedinvestors=False,
            morningsession=False,
            eveningsession=False,
            stock_data={},
        )

        cls.dividend_id_1 = Dividend.objects.create(
            stock_id=1,
            date="2000-01-01",
            amount="24.36",
        )

        cls.dividend_id_2 = Dividend.objects.create(
            stock_id=1,
            date="2000-01-02",
            amount="100000.00",
        )

        cls.dividend_of_user_id_1 = DividendsOfUser.objects.create(
            user=cls.user_authenticated,
            dividend=cls.dividend_id_1,
        )

        cls.dividend_of_user_id_2 = DividendsOfUser.objects.create(
            user=cls.user_authenticated,
            dividend=cls.dividend_id_2,
        )

        cls.dividend_of_user_id_2.is_received = True
        cls.dividend_of_user_id_2.save()

        cls.transaction_id_1 = Transaction.objects.create(
            transaction_type='BUY',
            asset_type='STOCK',
            user=cls.user_authenticated,
            ticker=cls.stock_id_1,
            date='1999-12-31',
            price='10',
            quantity=1
        )

        cls.transaction_id_2 = Transaction.objects.create(
            transaction_type='BUY',
            asset_type='STOCK',
            user=cls.user_authenticated,
            ticker=cls.stock_id_3,
            date='2018-01-01',
            price='100',
            quantity=4
        )

        cls.transaction_id_3 = Transaction.objects.create(
            transaction_type='SELL',
            asset_type='STOCK',
            user=cls.user_authenticated,
            ticker=cls.stock_id_3,
            date='2019-01-01',
            price='120',
            quantity=3
        )

        cls.transaction_id_4 = Transaction.objects.create(
            transaction_type='BUY',
            asset_type='STOCK',
            user=cls.user_authenticated,
            ticker=cls.stock_id_3,
            date='2020-01-01',
            price='80',
            quantity=2
        )

        cls.transaction_id_5 = Transaction.objects.create(
            transaction_type='SELL',
            asset_type='STOCK',
            user=cls.user_authenticated,
            ticker=cls.stock_id_3,
            date='2021-01-01',
            price='200',
            quantity=1
        )

        cls.transaction_id_6 = Transaction.objects.create(
            transaction_type='BUY',
            asset_type='STOCK',
            user=cls.user_authenticated_another,
            ticker=cls.stock_id_2,
            date='2021-01-01',
            price='200',
            quantity=1
        )
        
        cls.transaction_id_7 = Transaction.objects.create(
            transaction_type='SELL',
            asset_type='STOCK',
            user=cls.user_authenticated,
            ticker=cls.stock_id_3,
            date='2021-01-01',
            price='200',
            quantity=2
        )

        StocksOfUser.objects.create(
            user=cls.user_authenticated, stock=cls.stock_id_1)

        StocksOfUser.objects.create(
            user=cls.user_authenticated, stock=cls.stock_id_3)

        StocksOfUser.objects.create(
            user=cls.user_authenticated_another, stock=cls.stock_id_2)
