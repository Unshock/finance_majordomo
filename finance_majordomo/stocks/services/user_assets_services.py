from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from finance_majordomo.currencies.models import CurrencyRate
from finance_majordomo.dividends.utils import get_dividend_result_of_portfolio
from finance_majordomo.stocks.models import Asset, AssetsHistoricalData
from finance_majordomo.stocks.utils import update_historical_data
from finance_majordomo.transactions.services.transaction_calculation_services\
    import get_asset_quantity_for_portfolio, get_purchase_price
from finance_majordomo.users.models import Portfolio, User
from finance_majordomo.users.utils.utils import get_current_portfolio


def get_currency_rate(currency: str = None):
    if currency and currency.lower() == 'usd':
        currency_rate = CurrencyRate.objects.last().price_usd
    else:
        currency_rate = Decimal('1')

    return currency_rate


def get_current_price(user, asset, currency=None):
    currency_rate = get_currency_rate(currency)

    last_date_price = AssetsHistoricalData.objects.filter(
        asset=asset).order_by('-tradedate')[0].legalcloseprice
    
    portfolio = get_current_portfolio(user)
    
    current_quantity = get_asset_quantity_for_portfolio(portfolio.id, asset)

    current_price = current_quantity * last_date_price / currency_rate

    if asset.group == 'stock_bonds':
        bond = asset.get_related_object()
        current_price = current_price * bond.face_value / 100

    return Decimal(current_price)



class AssetItem:

    def __init__(self, id: str, secid: str, name: str, latname: str,
                 currency: str, asset_group: str, asset_type: str,
                 date: datetime.date = None, portfolio: Portfolio = None):

        self.id = id
        self.secid = secid
        self.name = name
        self.latname = latname
        self.currency = currency
        self.asset_group = asset_group
        self.asset_type = asset_type
        self.date = date
        self.portfolio = portfolio

        self.quantity = self._get_quantity()

    def _get_quantity(self):
        return get_asset_quantity_for_portfolio(self.portfolio.id, self.id, self.date)
    
    
    quantity = int
    purchase_price = Decimal
    purchase_price_usd = Decimal
    current_price = Decimal()
    current_price_usd = Decimal()
    dividends_received = Decimal()
    dividends_received_usd = Decimal


def get_portfolio_assets(user: User) -> list[AssetItem]:

    portfolio = get_current_portfolio(user)

    portfolio_assets_list = []

    portfolio_assets = Asset.objects.filter(
        id__in=portfolio.assetofportfolio_set.values_list('asset'))

    for asset in portfolio_assets:

        # update_history_data(stock)
        # update_today_data(stock)
        update_historical_data(asset)

        asset_item = AssetItem()
        asset_item.id = asset.id
        asset_item.secid = asset.secid
        asset_item.name = asset.name
        asset_item.latname = asset.latname
        asset_item.currency = asset.currency
        asset_item.group = asset.group
        asset_item.type = asset.type

        current_quantity = get_asset_quantity_for_portfolio(portfolio.id, asset.id)

        if current_quantity == 0:
            continue

        asset_item.purchase_price = get_purchase_price(
            portfolio.id, asset.id)
        asset_item.purchase_price_usd = get_purchase_price(
            portfolio.id, asset.id, currency='usd')

        asset_item.current_price = get_current_price(user, asset)
        asset_item.current_price_usd = get_current_price(
            user, asset, currency='usd')

        asset_item.dividends_received = get_dividend_result_of_portfolio(
            portfolio, asset.id)
        asset_item.dividends_received_usd = get_dividend_result_of_portfolio(
            portfolio, asset.id, currency='usd')

        portfolio_assets_list.append(asset_item)

    return portfolio_assets_list


def get_rate_of_return(cost_beg: Decimal, cost_end: Decimal) -> Decimal:
    return (cost_end - cost_beg) / cost_beg
