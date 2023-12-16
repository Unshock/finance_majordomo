from decimal import Decimal
from .base_settings import BaseTest
from ..services.accrual_services.accrual_calculation_services import \
    get_accrual_result_of_portfolio



class TestAccrualViews(BaseTest):

    def test_get_accrual_result_of_portfolio(self):

        portfolio = self.user_authenticated.current_portfolio
        result = get_accrual_result_of_portfolio(portfolio)
        self.assertEqual(result, self.accrual2.amount * Decimal('0.87'))

    def test_get_accrual_result_of_portfolio_no_tax(self):

        portfolio = self.user_authenticated.current_portfolio
        result = get_accrual_result_of_portfolio(
            portfolio, taxes_excluded=False)
        self.assertEqual(result, self.accrual2.amount)

    def test_get_accrual_result_of_portfolio_asset_specified(self):

        portfolio = self.user_authenticated.current_portfolio
        result = get_accrual_result_of_portfolio(
            portfolio, asset=self.share_POSI
        )
        self.assertEqual(result, Decimal('0') * Decimal('0.87'))

    def test_get_accrual_result_of_portfolio_asset_specified_usd(self):

        # uses get_currency_rate()

        portfolio = self.user_authenticated.current_portfolio
        result = get_accrual_result_of_portfolio(
            portfolio, asset=self.bond1, currency='usd'
        )

        accrual_price = self.accrual2.amount
        usd_rate = self.usd_rate4.price_usd

        self.assertEqual(
            result, accrual_price * Decimal('0.87') / usd_rate
        )
