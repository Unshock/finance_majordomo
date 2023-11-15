from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView
from moneyfmt import moneyfmt

from finance_majordomo.dividends.models import Dividend, DividendsOfUser, \
    DividendsOfPortfolio
from .dividend_services.dividend_model_management_services import \
    TogglePortfolioDividendService
from .dividend_services.dividend_view_services import \
    PortfolioAccrualViewContextService
from ..transactions.services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from django.utils.translation import gettext_lazy as _

from ..users.utils.utils import get_current_portfolio


class Dividends(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Dividend
    template_name = 'dividends/dividend_list.html'
    context_object_name = 'dividend'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Dividend list")

        portfolio = get_current_portfolio(self.request.user)

        dividend_list, \
        total_divs_payable, \
        total_divs_received, \
        total_divs_upcoming = PortfolioAccrualViewContextService.execute(
            {'portfolio': portfolio,
             'days_delta': 90
             }
        )

        context['dividend_list'] = dividend_list
        context['total_divs_payable'] = total_divs_payable
        context['total_divs_received'] = total_divs_received
        context['total_divs_upcoming'] = total_divs_upcoming
        return context


class UsersDividends(LoginRequiredMixin, ListView):
    pass


class TogglePortfolioDiv(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Dividend
    login_url = 'login'

    def get(self, request, *args, **kwargs):

        portfolio = get_current_portfolio(request.user)
        dividend = Dividend.objects.get(id=kwargs.get('pk_dividend'))

        try:
            TogglePortfolioDividendService.execute({
                'portfolio': portfolio,
                'dividend': dividend,
            })

        except Exception as e:
            print(e)

        return redirect('dividends')
