from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.db.models import QuerySet
from service_objects.fields import ModelField
from service_objects.services import Service

from common.utils.values_formatters import set_money_fmt, set_percentage_fmt
from finance_majordomo.currencies.utils import update_currency_rates, update_usd
from finance_majordomo.dividends.dividend_services.accrual_calc_services import \
    get_accrual_result_of_portfolio
from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.services.asset_services import \
    get_current_asset_price_per_asset
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

            self.quantity = self._get_asset_quantity()

            self.avg_purchase_price = self._get_avg_purchase_price()
            self.purchase_price = self._get_purchase_price()
            self.current_price_per_asset = self._get_current_price_per_asset()
            self.current_price = self._get_current_price_total()
            self.accruals_received = self._get_accrual_received()

            self.avg_purchase_price_usd = self._get_avg_purchase_price(
                currency='usd')
            self.purchase_price_usd = self._get_purchase_price(
                currency='usd')
            self.current_price_per_asset_usd =\
                self._get_current_price_per_asset(currency='usd')
            self.current_price_usd = self._get_current_price_total()
            self.accruals_received_usd = self._get_accrual_received(
                currency='usd')

            asset_result = AssetResult(
                self.purchase_price, self.current_price, self.accruals_received)
            self.percentage_result_with_accruals = \
                asset_result.get_percentage_result_with_accruals()
            self.percentage_result_no_accruals = \
                asset_result.get_percentage_result_with_no_accruals()
            self.financial_result_with_accruals = \
                asset_result.get_financial_result_with_accruals()
            self.financial_result_no_accruals = \
                asset_result.get_financial_result_no_accruals()

    @staticmethod
    def _validate_arguments(portfolio, asset):
        return isinstance(portfolio, Portfolio) and isinstance(asset, Asset)

    def _get_asset_quantity(self, formatter=None):
        quantity = get_asset_quantity_for_portfolio(
            self.portfolio.id, self.asset_id)

        return formatter(quantity) if formatter else quantity

    def _get_avg_purchase_price(self, currency=None, formatter=None):
        avg_purchase_price = get_average_purchase_price(
            self.portfolio.id, self.asset_id, currency=currency)

        return formatter(avg_purchase_price) if\
            formatter else avg_purchase_price

    def _get_purchase_price(self, currency=None, formatter=None):
        purchase_price = get_purchase_price(
            self.portfolio.id, self.asset_id, currency=currency
        )

        return formatter(purchase_price) if formatter else purchase_price

    def _get_current_price_per_asset(self, currency=None, formatter=None):
        current_price = get_current_asset_price_per_asset(
            self.asset, currency=currency)

        return formatter(current_price) if formatter else current_price

    def _get_current_price_total(self, formatter=None):
        current_price_total = self.current_price_per_asset * self.quantity

        return formatter(current_price_total)\
            if formatter else current_price_total

    def _get_current_price_total_usd(self, formatter=None):
        current_price_total = self.current_price_per_asset_usd * self.quantity

        return formatter(current_price_total)\
            if formatter else current_price_total

    def _get_accrual_received(self, currency=None, formatter=None):
        accrual_received = get_accrual_result_of_portfolio(
            self.portfolio, currency=currency)

        return formatter(accrual_received) if formatter else accrual_received

    def format_all_fields(self):
        self.quantity = set_money_fmt(self.quantity, places=0)

        self.avg_purchase_price = set_money_fmt(self.avg_purchase_price)
        self.purchase_price = set_money_fmt(self.purchase_price)
        self.current_price = set_money_fmt(self.current_price)
        self.accruals_received = set_money_fmt(self.accruals_received)

        self.avg_purchase_price_usd = set_money_fmt(self.avg_purchase_price_usd)
        self.purchase_price_usd = set_money_fmt(self.purchase_price_usd)
        self.current_price_usd = set_money_fmt(self.current_price_usd)
        self.accruals_received_usd = set_money_fmt(self.accruals_received_usd)

        self.percentage_result_with_accruals = set_percentage_fmt(
            self.percentage_result_with_accruals)
        self.percentage_result_no_accruals = set_percentage_fmt(
            self.percentage_result_no_accruals)
        self.financial_result_with_accruals = set_money_fmt(
            self.financial_result_with_accruals)
        self.financial_result_no_accruals = set_money_fmt(
            self.financial_result_no_accruals)


class AssetResult:
    def __init__(
            self, initial_price, final_price, accruals_received=Decimal('0')):
        if self._validate_price(initial_price)\
                and self._validate_price(final_price)\
                and self._validate_price(accruals_received):

            self.initial_price = initial_price
            self.final_price = final_price
            self.accruals_received = accruals_received

    def get_percentage_result_with_no_accruals(self, formatter=None):
        if self.initial_price == 0 and self.final_price == 0:
            result = Decimal('0')
        elif self.final_price > 0 and self.initial_price > 0:
            result = (Decimal(self.final_price) - Decimal(self.initial_price))\
                     / Decimal(self.initial_price)
        else:
            raise ValueError('initial_price and final_price must be >= 0')

        return formatter(result) if formatter else result

    def get_percentage_result_with_accruals(self, formatter=None):
        if self.initial_price == 0 and\
                (self.final_price + self.accruals_received) == 0:
            result = Decimal('0')
        elif (self.final_price + self.accruals_received) > 0 and\
                self.initial_price > 0:
            result = (
                    (
                            Decimal(self.final_price)
                            + Decimal(self.accruals_received) 
                            - Decimal(self.initial_price)
                     ) / Decimal(self.initial_price)
                   )
        else:
            raise ValueError('initial_price and final_price must be >= 0')

        return formatter(result) if formatter else result

    def get_financial_result_no_accruals(self, formatter=None):
        result = Decimal(self.final_price) - Decimal(self.initial_price)

        return formatter(result) if formatter else result

    def get_financial_result_with_accruals(self, formatter=None):
        result = Decimal(self.final_price)\
                 + Decimal(self.accruals_received)\
                 - Decimal(self.initial_price)

        return formatter(result) if formatter else result

    @staticmethod
    def _validate_price(price):
        return price >= 0 and type(price) in [Decimal, int, float]


class PortfolioAssetsViewContextService(Service):

    portfolio = ModelField(Portfolio)

    def process(self) -> dict:
        self.portfolio = self.cleaned_data.get('portfolio')
        portfolio_assets = self._get_assets_of_portfolio()
        if not portfolio_assets:
            return dict()
        return self._get_assets_of_portfolio_view_context(portfolio_assets)

    def _get_assets_of_portfolio(self):
        return self.portfolio.get_assets_of_portfolio()

    def _get_assets_of_portfolio_view_context(self, portfolio_assets) -> dict:
        total_purchase_price = Decimal('0')
        total_current_price = Decimal('0')
        total_accruals_received = Decimal('0')

        total_purchase_price_usd = Decimal('0')
        total_current_price_usd = Decimal('0')
        total_accruals_received_usd = Decimal('0')

        portfolio_assets_data = {'total_data': {},
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

            portfolio_asset = PortfolioAssetItem(self.portfolio, asset)

            total_purchase_price += portfolio_asset.purchase_price
            total_purchase_price_usd += portfolio_asset.purchase_price_usd
            total_current_price += portfolio_asset.current_price
            total_current_price_usd += portfolio_asset.current_price_usd
            total_accruals_received += portfolio_asset.accruals_received
            total_accruals_received_usd += portfolio_asset.accruals_received_usd

            portfolio_asset.format_all_fields()
            portfolio_assets_data['asset_list'].append(portfolio_asset)

            # # create
            # current_price = self.get_current_price(asset)
            # current_price_usd = self.get_current_price(asset, currency='usd')
            # 
            # total_current_price += current_price
            # total_current_price_usd += current_price_usd
            # 
            # percent_result = self.get_percent_result(
            #     purchase_price, current_price)
            # 
            # money_result_without_divs = moneyfmt(
            #     get_money_result(current_price, purchase_price), sep=' ')
            # 
            # dividends_received = \
            #     get_accrual_result_of_portfolio(current_portfolio)
            # total_divs += dividends_received
            # 
            # dividends_received_usd = get_accrual_result_of_portfolio(
            #     current_portfolio, currency='usd')
            # 
            # total_divs_usd += dividends_received_usd
            # 
            # money_result_with_divs = moneyfmt(
            #     get_money_result(
            #         current_price + dividends_received,
            #         purchase_price),
            #     sep=' ')
            # 
            # rate_of_return = self.get_percent_result(
            #     purchase_price, current_price + dividends_received)
            # 
            # user_stock_data['stock_list'].append(
            #     {'id': asset.id,
            #      'ticker': asset.secid,
            #      'name': asset.name,
            #      'currency': asset.currency,
            #      'quantity': moneyfmt(
            #          Decimal(current_quantity), sep=' ', places=0),
            #      'purchase_price': moneyfmt(purchase_price, sep=' '),
            #      'avg_purchase_price': moneyfmt(avg_purchase_price, sep=' ',
            #                                     curr='$'),
            #      'current_price': moneyfmt(current_price, sep=' '),
            #      'percent_result': percent_result,
            #      'dividends_received': moneyfmt(dividends_received, sep=' '),
            #      'money_result_without_divs': money_result_without_divs,
            #      'money_result_with_divs': money_result_with_divs,
            #      'rate_of_return': rate_of_return,
            #      })
            # print(type(moneyfmt(
            #     Decimal(current_quantity), sep=' ', places=0)))

        total_results = AssetResult(
            total_purchase_price, total_current_price, total_accruals_received)
        total_results_usd = AssetResult(
            total_purchase_price_usd,
            total_current_price_usd,
            total_accruals_received
        )

        portfolio_assets_data['total_results'] = {
            'total_purchase_price': set_money_fmt(total_purchase_price),
            'total_current_price': set_money_fmt(total_current_price),
            'total_percent_result':
                set_percentage_fmt(
                    total_results.get_percentage_result_with_accruals()),
            'total_accruals_received': set_money_fmt(total_accruals_received),
            'total_financial_result_no_divs': set_money_fmt(
                total_results.get_financial_result_no_accruals()),
            'total_financial_result_with_divs': set_money_fmt(
                total_results.get_financial_result_with_accruals()),
            'total_rate_of_return': set_percentage_fmt(
                total_results.get_percentage_result_with_accruals()),

            'total_current_price_usd': set_money_fmt(
                total_current_price_usd),
            'total_financial_result_with_divs_usd': set_money_fmt(
                total_results_usd.get_financial_result_with_accruals())
        }

        return portfolio_assets_data
