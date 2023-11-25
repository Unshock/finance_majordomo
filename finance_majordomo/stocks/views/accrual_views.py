from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView

from finance_majordomo.stocks.models.accrual_models import Dividend
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    TogglePortfolioDividendService
from finance_majordomo.stocks.services.accrual_services.dividend_view_services import \
    PortfolioAccrualViewContextService, portfolio_accrual_view_context_service
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.utils.utils import get_current_portfolio


class Dividends(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Dividend
    template_name = 'dividends/dividend_list.html'
    context_object_name = 'dividend'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Dividend list")

        portfolio = self.request.user.get_current_portfolio()

        accruals_data = portfolio_accrual_view_context_service(portfolio, 90)

        context['accrual_list'] = accruals_data.get('accrual_list')
        context['total_results'] = accruals_data.get('total_results')
        print(context)
        return context


class UsersDividends(LoginRequiredMixin, ListView):
    pass


class TogglePortfolioDiv(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Dividend
    login_url = 'login'

    def get(self, request, *args, **kwargs):

        portfolio = request.user.get_current_portfolio()
        dividend = Dividend.objects.get(id=kwargs.get('pk_dividend'))

        try:
            TogglePortfolioDividendService.execute({
                'portfolio': portfolio,
                'dividend': dividend,
            })

        except Exception as e:
            print(e)

        return redirect('stocks:dividends')
