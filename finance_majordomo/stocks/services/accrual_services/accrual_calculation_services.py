from decimal import Decimal
from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.stocks.utils.currencies_utils import get_usd_rate
from finance_majordomo.stocks.models.accrual_models import AccrualsOfPortfolio
from finance_majordomo.stocks.services.transaction_services.\
    transaction_calculation_services import get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


def get_accrual_result_of_portfolio(
        portfolio: Portfolio,
        *,
        asset: Asset = None,
        currency: str = None,
        taxes_excluded: bool = True) -> Decimal:
    """
    :param portfolio: Portfolio model object
    :param asset: Asset model object
    :param currency: currency to map accrual results
        (only 'usd' is supported for now)
    :param taxes_excluded: flag that shows we need to get net accrual result
        without taxes (13 % according to russian taxation)
    :return: Decimal accrual result of specified Portfolio and Asset
        (if specified)
    """

    portfolio_accruals_received = AccrualsOfPortfolio.objects.filter(
        portfolio=portfolio, is_received=True)

    if asset:
        portfolio_accruals_received = portfolio_accruals_received.filter(
            dividend__asset=asset
        )

    currency_rate = Decimal('1')
    sum_accruals_received = Decimal('0')

    for accrual in portfolio_accruals_received:

        asset_id = accrual.dividend.asset.id
        date = accrual.dividend.date
        amount = accrual.dividend.amount

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_id, date=date)

        if currency.lower() == 'usd':
            currency_rate = get_usd_rate(accrual.dividend.date)

        sum_accruals_received += quantity * amount / currency_rate

    return sum_accruals_received if not taxes_excluded else\
        sum_accruals_received / Decimal(0.87)
