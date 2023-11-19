from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.db.models import QuerySet
from service_objects.fields import ModelField
from service_objects.services import Service

from common.utils.money_formatter import set_moneyfmt
from finance_majordomo.currencies.utils import update_currency_rates, update_usd
from finance_majordomo.dividends.dividend_services.accrual_calc_services import \
    get_accrual_result_of_portfolio
from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.services.user_assets_services import \
    get_current_price
from finance_majordomo.stocks.utils import update_historical_data
from finance_majordomo.transactions.services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio, get_average_purchase_price, \
    get_purchase_price
from finance_majordomo.users.models import User, Portfolio


class GetAssetsOfUser(Service):

    user = ModelField(User)

    def process(self) -> QuerySet(Asset):
        self.user = self.cleaned_data.get('user')
        return self._get_assets_of_user()

    def _get_portfolios_of_user(self):
        return self.user.portfolio_set.all()

    def _get_assets_of_user(self):

        portfolios_of_user = self._get_portfolios_of_user()

        assets_of_user = Asset.objects.none()

        for portfolio in portfolios_of_user:

            assets_of_user |= Asset.objects.filter(
                id__in=portfolio.assetofportfolio_set.values('asset'))

        return assets_of_user


# @dataclass
# class PortfolioAssetItem:
#     asset_name: str
#     asset_quantity: Decimal
#     id: int
#     amount: Decimal
#     sum: Decimal
#     date: datetime.date
#     is_received: bool
#     is_upcoming: bool


class PortfolioAssetItem:
    def __init__(self, portfolio: Portfolio, asset: Asset):
        
        if self._validate_arguments(portfolio, asset):
            self.portfolio = portfolio
            self.asset = asset
        
            self.asset_id = self.asset.id
            self.ticker = self.asset.secid
            self.name = self.asset.name
            self.currency = self.asset.currency
            
            self.quantity = self._get_asset_quantity(
                formatter=set_moneyfmt)
            self.avg_purchase_price = self._get_avg_purchase_price(
                formatter=set_moneyfmt)
            self.purchase_price = self._get_purchase_price(
                formatter=set_moneyfmt)
        
    @staticmethod
    def _validate_arguments(portfolio, asset):
        return isinstance(portfolio, Portfolio) and isinstance(asset, Asset)
    
    def _get_asset_quantity(self, formatter=None):
        quantity = get_asset_quantity_for_portfolio(
            self.portfolio.id, self.asset_id)
        
        if formatter is None:
            return quantity
        
        return formatter(quantity)
    
    def _get_avg_purchase_price(self, formatter=None):
        avg_purchase_price = get_average_purchase_price(
            self.portfolio.id, self.asset_id)

        if formatter is None:
            return avg_purchase_price

        return formatter(avg_purchase_price)
    
    
    def _get_purchase_price(self, formatter=None):
        purchase_price = get_purchase_price(self.portfolio.id, self.asset_id)

        if formatter is None:
            return purchase_price

        return formatter(purchase_price)
    
    def _get_current_price(self, formatter=None):
        current_price = get_current_price(self.portfolio.id, self.asset_id)

        if formatter is None:
            return current_price
    
        return formatter(current_price)

    def _get_accrual_received(self, formatter=None):
        accrual_received = get_accrual_result_of_portfolio(
            self.portfolio)

        if formatter is None:
            return accrual_received

        return formatter(accrual_received)


class Return:
    def __init__(self, initial_price, final_price):
        self.initial_price = initial_price
        self.final_price = final_price

 'current_price': moneyfmt(current_price, sep=' '),
 'percent_result': percent_result,
 'dividends_received': moneyfmt(dividends_received, sep=' '),
 'money_result_without_divs': money_result_without_divs,
 'money_result_with_divs': money_result_with_divs,
 'rate_of_return': rate_of_return,
 })


class PortfolioAssetsViewContextService(Service):

    portfolio = ModelField(Portfolio)

    def process(self):
        self.portfolio = self.cleaned_data.get('portfolio')
        portfolio_assets = self._get_assets_of_portfolio()
        if not portfolio_assets:
            return dict()
        return self._get_assets_of_portfoio_view_context(portfolio_assets)

    def _get_assets_of_portfolio(self):
        return self.portfolio.get_assets_of_portfolio()
    
    def _get_assets_of_portfolio_view_context(self, portfolio_assets) -> dict:
        total_purchase_price = Decimal('0')
        total_current_price = Decimal('0')
        total_divs = Decimal('0')

        total_purchase_price_usd = Decimal('0')
        total_current_price_usd = Decimal('0')
        total_divs_usd = Decimal('0')

        user_stock_data = {'total_data': {},
                           'asset_list': []
                           }

        try:
            update_currency_rates()
            update_usd()

        except Exception as e:
            print(e)

        for asset in portfolio_assets:

            # update_history_data(stock)
            # update_today_data(stock)
            try:
                update_historical_data(asset)
            except Exception as e:
                print(e)

            current_quantity = get_asset_quantity_for_portfolio(
                self.portfolio.id, asset.id)

            if current_quantity == 0:
                continue

            avg_purchase_price = get_average_purchase_price(
                self.portfolio.id, asset.id)
            purchase_price = get_purchase_price(
                self.portfolio.id, asset.id)
            purchase_price_usd = get_purchase_price(
                self.portfolio.id, asset.id, currency='usd')

            total_purchase_price += purchase_price
            total_purchase_price_usd += purchase_price_usd

            # create
            current_price = self.get_current_price(asset)
            current_price_usd = self.get_current_price(asset, currency='usd')

            total_current_price += current_price
            total_current_price_usd += current_price_usd

            percent_result = self.get_percent_result(
                purchase_price, current_price)

            money_result_without_divs = moneyfmt(
                get_money_result(current_price, purchase_price), sep=' ')

            dividends_received = \
                get_accrual_result_of_portfolio(current_portfolio)
            total_divs += dividends_received

            dividends_received_usd = get_accrual_result_of_portfolio(
                current_portfolio, currency='usd')

            total_divs_usd += dividends_received_usd

            money_result_with_divs = moneyfmt(
                get_money_result(
                    current_price + dividends_received,
                    purchase_price),
                sep=' ')

            rate_of_return = self.get_percent_result(
                purchase_price, current_price + dividends_received)

            user_stock_data['stock_list'].append(
                {'id': asset.id,
                 'ticker': asset.secid,
                 'name': asset.name,
                 'currency': asset.currency,
                 'quantity': moneyfmt(
                     Decimal(current_quantity), sep=' ', places=0),
                 'purchase_price': moneyfmt(purchase_price, sep=' '),
                 'avg_purchase_price': moneyfmt(avg_purchase_price, sep=' ',
                                                curr='$'),
                 'current_price': moneyfmt(current_price, sep=' '),
                 'percent_result': percent_result,
                 'dividends_received': moneyfmt(dividends_received, sep=' '),
                 'money_result_without_divs': money_result_without_divs,
                 'money_result_with_divs': money_result_with_divs,
                 'rate_of_return': rate_of_return,
                 })
            print(type(moneyfmt(
                Decimal(current_quantity), sep=' ', places=0)))

        total_financial_result_no_divs = total_current_price - total_purchase_price
        total_financial_result_with_divs = total_current_price + total_divs - total_purchase_price

        print(total_current_price_usd, total_divs_usd, total_purchase_price_usd)
        total_financial_result_with_divs_usd = total_current_price_usd + total_divs_usd - total_purchase_price_usd

        total_percent_result = self.get_percent_result(
            total_purchase_price, total_current_price)
        total_rate_of_return = self.get_percent_result(
            total_purchase_price,
            (total_financial_result_with_divs + total_purchase_price))

        user_stock_data['total_results'] = {
            'total_purchase_price': moneyfmt(total_purchase_price, sep=' '),
            'total_current_price': moneyfmt(total_current_price, sep=' '),
            'total_percent_result': total_percent_result,
            'total_divs': set_moneyfmt(total_divs),
            'total_financial_result_no_divs': set_moneyfmt(
                total_financial_result_no_divs),
            'total_financial_result_with_divs': moneyfmt(
                total_financial_result_with_divs, sep=' '),
            'total_rate_of_return': total_rate_of_return,

            'total_current_price_usd': moneyfmt(
                total_current_price_usd, sep=' '),
            'total_financial_result_with_divs_usd': moneyfmt(
                total_financial_result_with_divs_usd, sep=' ')
        }

        return user_stock_data
        
