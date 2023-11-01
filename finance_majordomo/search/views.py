import json
from decimal import Decimal

from django.views import View
from moneyfmt import moneyfmt
from common.utils.stocks import get_security
import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, TemplateView

from .forms import SearchForm
from finance_majordomo.stocks.models import Stock, ProdCalendar
from finance_majordomo.transactions.models import Transaction

from django.utils.translation import gettext_lazy as _

from common.utils.stocks import get_asset_board_history, make_json_trade_info_dict, get_date_status, \
    get_stock_current_price, make_json_last_price_dict
from finance_majordomo.dividends.utils import get_stock_dividends, add_dividends_to_model
from ..transactions.utils import get_quantity, get_purchase_price
from ..dividends.utils import get_dividend_result


class Search(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        form = SearchForm()

        context = {
            'page_title': _("Search for assets"),
            'button_text': _("Search"),
            'form': form
        }

        return render(
            request,
            'base_create_and_update.html',
            context=context
        )

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)

        allowed_groups = ['stock_shares',
                          'stock_bonds',
                          #'stock_ppif'
                          ]

        if form.is_valid():
            search_data = form.cleaned_data.get('search_data')

            search_result = get_security(search_data)
            search_result_list = list(filter(
                lambda d: d['is_traded'] and d['group'] in allowed_groups,
                search_result))


            context = {
                'page_title': _("Search results"),
                'search_result_list':
                    search_result_list if search_result_list else None

            }

            return render(
                request,
                'search/search_result_list.html',
                context=context
            )
