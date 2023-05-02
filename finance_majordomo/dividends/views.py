import datetime
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from finance_majordomo.dividends.models import Dividend, DividendsOfUser
from ..transactions.utils import get_quantity
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import UsersStocks, User


class Dividends(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Dividend
    template_name = 'dividends/dividend_list.html'
    context_object_name = 'dividend'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Dividend list")

        dividend_list = []
        total_divs_payable = 0
        total_divs_recieved = 0
        total_divs_upcoming = 0

        user = self.request.user

        users_stocks_dividends = Dividend.objects.filter(stock__in=self.request.user.usersstocks_set.values_list('stock')).order_by('-date')

        #print(self.request.user.usersstocks_set.values_list('stock'))
        #print(users_stocks_dividends)

        for div in users_stocks_dividends:
            stock = div.stock
            date_str = div.date
            dividend = div.dividend

            date_today = datetime.datetime.today()
            date_dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            date_status = True if date_dt <= date_today else False

            try:
                dividend_of_user = DividendsOfUser.objects.get(user=user,
                                                               dividend=div)
                status = dividend_of_user.status
            except DividendsOfUser.DoesNotExist:
                status = False

            quantity_for_the_date = get_quantity(
                self.request, stock, date=date_str)

            if quantity_for_the_date > 0:
                total_div = Decimal(quantity_for_the_date * dividend)

                if date_status:
                    total_divs_payable += total_div
                    total_divs_recieved += total_div if status else 0

                else:
                    total_divs_upcoming += total_div

                dividend_list.append((div, quantity_for_the_date, total_div, status, date_status))

        context['dividend_list'] = dividend_list
        context['total_divs_payable'] = total_divs_payable
        context['total_divs_received'] = total_divs_recieved
        context['total_divs_upcoming'] = total_divs_upcoming
        return context


class UsersDividends(LoginRequiredMixin, ListView):
    pass

class AddDivToUser(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Dividend
    login_url = 'login'
    success_message = _("Stock has been successfully added to user's stock list")

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)

        dividend_id = kwargs['pk_dividend']
        dividend = Dividend.objects.get(id=dividend_id)

        try:
            dividend_of_user = DividendsOfUser.objects.get(user=user,
                                                           dividend=dividend)
        except DividendsOfUser.DoesNotExist:

            dividend.users.add(user)
            dividend.save()

            dividend_of_user = DividendsOfUser.objects.get(user=user,
                                                           dividend=dividend)
        dividend_of_user.status = True
        dividend_of_user.save()

        return redirect('dividends')


class RemoveDivFromUser(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Dividend
    login_url = 'login'
    success_message = _(
        "Stock has been successfully added to user's stock list")

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)

        dividend_id = kwargs['pk_dividend']
        dividend = Dividend.objects.get(id=dividend_id)

        try:
            dividend_of_user = DividendsOfUser.objects.get(user=user,
                                                           dividend=dividend)
        except DividendsOfUser.DoesNotExist:

            raise Exception('ne nashelsya sush dividend')

        dividend_of_user.status = False
        dividend_of_user.save()

        return redirect('dividends')