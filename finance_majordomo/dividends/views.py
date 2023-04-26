from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from finance_majordomo.dividends.models import Dividend
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import UsersStocks


class Dividends(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Dividend
    template_name = 'dividends/dividend_list.html'
    context_object_name = 'dividend'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Dividend list")
        
        dividend_list = []
        
        for div in Dividends.objects.all():
            stock_id = div.stock.id
            try:
                users_stock = UsersStocks.objects.get(user_id=self.request.user.id, stock_id=stock_id)
            except UsersStocks.DoesNotExist:
                continue
            div_date = div.date
        
        context['dividend_list'] = Dividend.objects.all()
        return context


class UsersDividends(LoginRequiredMixin, ListView):
    pass
