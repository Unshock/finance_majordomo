from decimal import Decimal

from django.test import TestCase, Client

from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.models.accrual_models import Dividend, \
    AccrualsOfPortfolio
from finance_majordomo.stocks.models.currency import CurrencyRate
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.users.models import User


class BaseTest(TestCase):

    fixtures = [
        'user.json',
        'user_settings.json',
        'AssetsHistoricalData.json',
        'assets.json',
        'stocks.json',
        'transaction.json',
        'asset_of_portfolio.json',
        'portfolio.json',
        'Dividend.json',
        'accruals_of_portfolio.json',
        'currency_rate.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_authenticated: Client = Client()
        cls.client_authenticated.force_login(User.objects.get(id=2))
        cls.user_authenticated = User.objects.get(id=2)

        cls.client_unauthenticated: Client = Client()

        cls.client_authenticated_no_assets: Client = Client()
        cls.client_authenticated_no_assets.force_login(User.objects.get(id=3))
        cls.user_authenticated_no_assets = User.objects.get(id=3)

        cls.share_POSI = Asset.objects.get(id=30)
        cls.share_LSRG = Asset.objects.get(id=31)
        cls.bond1 = Asset.objects.get(id=32)

        cls.accrual1 = Dividend.objects.get(id=1)
        cls.accrual2 = Dividend.objects.get(id=2)
        cls.accrual3 = Dividend.objects.get(id=3)

        cls.usd_rate1 = CurrencyRate.objects.get(id=1)
        cls.usd_rate2 = CurrencyRate.objects.get(id=2)
        cls.usd_rate3 = CurrencyRate.objects.get(id=3)
        cls.usd_rate4 = CurrencyRate.objects.get(id=4)
        cls.usd_rate5 = CurrencyRate.objects.get(id=5)
        cls.usd_rate_current = CurrencyRate.objects.get(id=100)

        cls.accrual_of_portfolio1 = AccrualsOfPortfolio.objects.get(id=1)
        cls.accrual_of_portfolio2 = AccrualsOfPortfolio.objects.get(id=2)
        cls.accrual_of_portfolio3 = AccrualsOfPortfolio.objects.get(id=3)

        cls.transaction1 = Transaction.objects.get(id=1)
        cls.transaction2 = Transaction.objects.get(id=2)
        cls.transaction3 = Transaction.objects.get(id=3)


