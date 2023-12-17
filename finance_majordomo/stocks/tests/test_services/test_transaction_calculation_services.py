import datetime
from decimal import Decimal
from finance_majordomo.stocks.services.transaction_services.\
    transaction_calculation_services import \
    get_asset_quantity_for_portfolio, get_purchase_price, \
    get_average_purchase_price
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.stocks.tests.test_services.conftest import \
    ExtraTransactionsSetUp


class TestTransactionCalculationServices(BaseTest, ExtraTransactionsSetUp):

    def test_get_asset_quantity_for_portfolio_no_date(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        quantity = get_asset_quantity_for_portfolio(
            portfolio_id=portfolio.id,
            asset_id=asset.id
        )

        self.assertEqual(quantity, 1)

    def test_get_asset_quantity_for_portfolio_with_date(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        quantity = get_asset_quantity_for_portfolio(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            date=datetime.datetime(year=2023, month=4, day=22)
        )

        self.assertEqual(quantity, 2)

    def test_get_purchase_price_no_date_no_curr(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        purchase_price = get_purchase_price(
            portfolio_id=portfolio.id,
            asset_id=asset.id
        )

        self.assertEqual(purchase_price, Decimal('2000'))

    def test_get_purchase_price_with_date_no_curr(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        purchase_price = get_purchase_price(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            date=datetime.datetime(year=2023, month=4, day=20)
        )

        self.assertEqual(purchase_price, Decimal('2000'))

    def test_get_purchase_price_with_date_with_curr(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        purchase_price = get_purchase_price(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            date=datetime.datetime(year=2023, month=4, day=20),
            currency='usd'
        )

        self.assertEqual(purchase_price, Decimal('24.4871'))

    def test_get_average_purchase_price_no_date_no_curr(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        purchase_price = get_average_purchase_price(
            portfolio_id=portfolio.id,
            asset_id=asset.id
        )

        self.assertEqual(purchase_price, Decimal('2000'))

    def test_get_average_purchase_price_with_date_no_curr(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        purchase_price = get_average_purchase_price(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            date=datetime.datetime(year=2023, month=4, day=20)
        )

        self.assertEqual(purchase_price, Decimal('1000'))

    def test_get_average_purchase_price_with_date_with_curr(self):
        portfolio = self.user_authenticated.current_portfolio
        asset = self.share_POSI

        purchase_price = get_average_purchase_price(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            date=datetime.datetime(year=2023, month=4, day=20),
            currency='usd'
        )

        self.assertEqual(purchase_price, Decimal('12.2436'))
