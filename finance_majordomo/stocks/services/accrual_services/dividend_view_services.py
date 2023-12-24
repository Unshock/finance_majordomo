from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

from django import forms
from django.db.models import QuerySet
from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.stocks.models.accrual_models import AccrualsOfPortfolio
from finance_majordomo.stocks.services.transaction_services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


@dataclass
class AccrualItem:
    """
    Instance to collect accruals data and indicators to show in view
    """
    asset_name: str
    asset_quantity: Decimal
    id: int
    amount: Decimal
    sum: Decimal
    date: datetime.date
    is_received: bool
    is_upcoming: bool


def execute_portfolio_accrual_view_context_service(
        portfolio: Portfolio, days_delta: int):
    """
    :param portfolio: Portfolio model object
    :param days_delta: shows the latest day on which accruals are paid
        (by default 90 days (1Q) is used). Used to limit future payments.
    :return: dictionary like:
        {'total_results': {'total_divs_payable': Decimal,
                           'total_divs_received': Decimal,
                           'total_divs_upcoming': Decimal
                           }
         'accrual_list': [AccrualItem]
         }
    """
    return PortfolioAccrualViewContextService.execute(
        {'portfolio': portfolio,
         'days_delta': days_delta
         }
    )


class PortfolioAccrualViewContextService(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.portfolio_accrual_data = {
            'total_results': {
                'total_divs_payable': None,
                'total_divs_received': None,
                'total_divs_upcoming': None
            },
            'accrual_list': []
        }

    portfolio = ModelField(Portfolio)
    days_delta = forms.IntegerField()

    def process(self):

        self.portfolio = self.cleaned_data.get('portfolio')

        portfolio_accruals = self._get_portfolio_accruals()
        if not portfolio_accruals:
            print(self.portfolio_accrual_data)
            return self.portfolio_accrual_data

        self._fill_context_with_accrual_context_data(portfolio_accruals)
        return self.portfolio_accrual_data

    def _fill_context_with_accrual_context_data(self, portfolio_accruals):
        accrual_item_list = self._get_accrual_item_list(portfolio_accruals)
        self.portfolio_accrual_data['accrual_list'] = accrual_item_list
        self.portfolio_accrual_data['total_results']['total_divs_payable'] =\
            self._get_total_divs_payable(accrual_item_list)
        self.portfolio_accrual_data['total_results']['total_divs_received'] =\
            self._get_total_divs_received(accrual_item_list)
        self.portfolio_accrual_data['total_results']['total_divs_upcoming'] =\
            self._get_total_divs_upcoming(accrual_item_list)

    def _get_portfolio_accruals(self):

        days_delta = timedelta(days=self.cleaned_data.get('days_delta'))

        portfolio_accruals = AccrualsOfPortfolio.objects.filter(
            portfolio=self.portfolio,
            accrual__date__lte=self._get_today_date() + days_delta
        ).order_by('-accrual__date')

        return portfolio_accruals

    def _get_accrual_item_list(
            self, portfolio_accruals: QuerySet) -> List[AccrualItem]:

        portfolio_accruals_list = []

        for accrual in portfolio_accruals:

            accrual_date = accrual.accrual.date
            asset_quantity = get_asset_quantity_for_portfolio(
                self.portfolio.id, accrual.accrual.asset.id, accrual_date
            )

            if asset_quantity <= 0:
                continue

            accrual_amount = accrual.accrual.amount
            accrual_total = accrual_amount * asset_quantity
            accrual_id = accrual.accrual.id
            asset_name = accrual.accrual.asset.latname
            accrual_is_received = accrual.is_received
            accrual_is_upcoming = False if accrual_date <= \
                                           self._get_today_date() else True

            portfolio_accruals_list.append(
                AccrualItem(
                    id=accrual_id,
                    asset_name=asset_name,
                    asset_quantity=asset_quantity,
                    date=accrual_date,
                    amount=accrual_amount,
                    sum=accrual_total,
                    is_received=accrual_is_received,
                    is_upcoming=accrual_is_upcoming
                )
            )

        return portfolio_accruals_list

    @staticmethod
    def _get_total_divs_payable(portfolio_accruals_list):

        return sum(a.sum for a in portfolio_accruals_list if not a.is_upcoming)

    @staticmethod
    def _get_total_divs_received(portfolio_accruals_list):

        return sum(a.sum for a in portfolio_accruals_list
                   if not a.is_upcoming and a.is_received
                   )

    @staticmethod
    def _get_total_divs_upcoming(portfolio_accruals_list):
        return sum(a.sum for a in portfolio_accruals_list if a.is_upcoming)

    @staticmethod
    def _get_today_date():
        return datetime.today().date()
