from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from functools import reduce
from typing import List

from django import forms
from django.db.models import QuerySet
from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.dividends.models import Dividend, DividendsOfPortfolio
from finance_majordomo.transactions.services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


@dataclass
class AccrualItem:
    asset_name: str
    asset_quantity: Decimal
    id: int
    amount: Decimal
    sum: Decimal
    date: datetime.date
    is_received: bool
    is_upcoming: bool


class PortfolioAccrualViewContextService(Service):
    portfolio = ModelField(Portfolio)
    days_delta = forms.IntegerField()

    def process(self):

        self.portfolio = self.cleaned_data.get('portfolio')

        portfolio_accruals = self._get_portfolio_accruals()

        accrual_list = self._get_accrual_list(portfolio_accruals)
        total_divs_payable = self._get_total_divs_payable(accrual_list)
        total_divs_received = self._get_total_divs_received(accrual_list)
        total_divs_upcoming = self._get_total_divs_upcoming(accrual_list)

        return accrual_list, total_divs_payable, total_divs_received, total_divs_upcoming

    def _get_portfolio_accruals(self):

        days_delta = timedelta(days=self.cleaned_data.get('days_delta'))

        # portfolio_accruals = Dividend.objects.filter(
        #     id__in=self.portfolio.dividendsofportfolio_set.values_list(
        #         'dividend'),
        #     date__lte=self._get_today_date() + days_delta
        # ).order_by('-date')

        portfolio_accruals = DividendsOfPortfolio.objects.filter(
            portfolio=self.portfolio,
            dividend__date__lte=self._get_today_date() + days_delta
        ).order_by('-dividend__date')

        return portfolio_accruals

    def _get_accrual_list(
            self, portfolio_accruals: QuerySet) -> List[AccrualItem]:

        portfolio_accruals_list = []

        for accrual in portfolio_accruals:

            accrual_date = accrual.dividend.date
            asset_quantity = get_asset_quantity_for_portfolio(
                self.portfolio.id, accrual.dividend.asset.id, accrual_date
            )

            if asset_quantity <= 0:
                continue
            
            accrual_amount = accrual.dividend.amount
            accrual_total = accrual_amount * asset_quantity
            accrual_id = accrual.dividend.id
            asset_name = accrual.dividend.asset.latname
            accrual_is_received = accrual.is_received
            accrual_is_upcoming = False if accrual_date <= \
                                           self._get_today_date() else True

            portfolio_accruals_list.append(AccrualItem(
                id=accrual_id,
                asset_name=asset_name,
                asset_quantity=asset_quantity,
                date=accrual_date,
                amount=accrual_amount,
                sum=accrual_total,
                is_received=accrual_is_received,
                is_upcoming=accrual_is_upcoming
            ))

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
