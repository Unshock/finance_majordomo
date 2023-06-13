import datetime
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from moneyfmt import moneyfmt

from finance_majordomo.dividends.models import Dividend, DividendsOfUser
from ..stocks.models import StocksOfUser
from ..transactions.utils import get_quantity
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import User


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
        total_divs_received = 0
        total_divs_upcoming = 0

        user = self.request.user

        dividends_of_user = Dividend.objects.filter(
            id__in=user.dividendsofuser_set.values_list('dividend'))\
            .order_by('-date')

        for div_obj in dividends_of_user:
            stock = div_obj.stock
            amount = div_obj.amount

            date_dt = div_obj.date
            date_str = datetime.datetime.strftime(date_dt, '%Y-%m-%d')
            date_today_dt = datetime.datetime.today().date()

            is_upcoming = False if date_dt <= date_today_dt else True

            is_received = DividendsOfUser.objects.get(
                user=user, dividend=div_obj).is_received

            quantity_for_the_date = get_quantity(
                self.request, stock, date=date_str)

            if quantity_for_the_date > 0:
                total_div = Decimal(quantity_for_the_date * amount)

                if not is_upcoming:
                    total_divs_payable += total_div
                    total_divs_received += total_div if is_received else 0

                else:
                    total_divs_upcoming += total_div

                dividend_list.append({
                    'div_obj': div_obj,
                    'date': date_str,
                    'quantity': quantity_for_the_date,
                    'total_div': total_div,
                    'is_received': is_received,
                    'is_upcoming': is_upcoming,
                })

        total_divs_payable = moneyfmt(
            total_divs_payable * Decimal(0.87), sep=' ')

        total_divs_received = moneyfmt(
            total_divs_received * Decimal(0.87), sep=' ')

        context['dividend_list'] = dividend_list
        context['total_divs_payable'] = total_divs_payable
        context['total_divs_received'] = total_divs_received
        context['total_divs_upcoming'] = total_divs_upcoming
        return context


class UsersDividends(LoginRequiredMixin, ListView):
    pass

class AddDivToUser(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Dividend
    login_url = 'login'
    success_message = _("Stock has been successfully added to user's stock list")

    def get(self, request, *args, **kwargs):
        user = request.user

        dividend_id = kwargs['pk_dividend']
        dividend = Dividend.objects.get(id=dividend_id)

        try:
            dividend_of_user = DividendsOfUser.objects.get(user=user,
                                                           dividend=dividend)
        except DividendsOfUser.DoesNotExist:
            raise Exception('such dividend has not been found')
            #dividend.users.add(user)
            #dividend.save()
            # dividend_of_user = DividendsOfUser.objects.get(user=user,
            #                                                dividend=dividend)
        print(dividend_of_user.is_received)
        dividend_of_user.is_received = True
        dividend_of_user.save()
        print(dividend_of_user.is_received)
        return redirect('dividends')


class RemoveDivFromUser(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Dividend
    login_url = 'login'
    success_message = _(
        "Stock has been successfully added to user's stock list")

    def get(self, request, *args, **kwargs):
        user = request.user

        dividend_id = kwargs['pk_dividend']
        dividend = Dividend.objects.get(id=dividend_id)

        try:
            dividend_of_user = DividendsOfUser.objects.get(user=user,
                                                           dividend=dividend)
        except DividendsOfUser.DoesNotExist:

            raise Exception('such dividend has not been found')

        dividend_of_user.is_received = False
        dividend_of_user.save()


        return redirect('dividends')