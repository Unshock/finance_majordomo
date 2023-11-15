from decimal import Decimal

from finance_majordomo.currencies.utils import get_usd_rate
from finance_majordomo.dividends.models import Dividend, DividendsOfPortfolio
from finance_majordomo.transactions.services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


def get_accrual_result_of_portfolio(
        portfolio: Portfolio,
        currency: str = None,
        taxes_excluded: bool = True) -> Decimal:

    portfolio_dividends_received = DividendsOfPortfolio.objects.filter(
        portfolio=portfolio, is_received=True)

    currency_rate = Decimal('1')
    sum_dividends_received = Decimal('0')

    for div in portfolio_dividends_received:

        asset_id = div.dividend.asset.id
        date = div.dividend.date
        amount = div.dividend.amount

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_id, date=date)

        if currency == 'usd':
            currency_rate = get_usd_rate(div.dividend.date)

        sum_dividends_received += quantity * amount / currency_rate

    return sum_dividends_received * Decimal(0.87)\
        if taxes_excluded else sum_dividends_received
