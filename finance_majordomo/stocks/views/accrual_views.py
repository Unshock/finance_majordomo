from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models.accrual_models import Accrual
from finance_majordomo.stocks.services.accrual_services.\
    dividend_model_management_services \
    import execute_toggle_portfolio_accrual_service
from finance_majordomo.stocks.services.accrual_services.dividend_view_services \
    import execute_portfolio_accrual_view_context_service


class Accruals(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Accrual
    template_name = 'dividends/dividend_list.html'
    context_object_name = 'accrual'

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Accruals list")

        portfolio = self.request.user.current_portfolio

        accruals_data = \
            execute_portfolio_accrual_view_context_service(portfolio, 90)

        context['accrual_list'] = accruals_data.get('accrual_list')
        context['total_results'] = accruals_data.get('total_results')

        return context


class UsersDividends(LoginRequiredMixin, ListView):
    pass


class TogglePortfolioDiv(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Accrual
    login_url = 'login'

    def get(self, request, *args, **kwargs):

        portfolio = request.user.current_portfolio
        accrual = Accrual.objects.get(id=kwargs.get('pk_accrual'))

        try:
            execute_toggle_portfolio_accrual_service(accrual, portfolio)

        except Exception as e:
            print(e, ' in ', execute_toggle_portfolio_accrual_service)

        return redirect('stocks:accruals')
