from django.test import TestCase, Client

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
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_authenticated: Client = Client()
        cls.client_authenticated.force_login(User.objects.get(id=2))

        cls.client_unauthenticated: Client = Client()

        cls.client_authenticated_no_assets: Client = Client()
        cls.client_authenticated_no_assets.force_login(User.objects.get(id=3))



