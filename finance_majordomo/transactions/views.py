from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from finance_majordomo.stocks.forms import StockForm
from finance_majordomo.stocks.models import Stock

from django.utils.translation import gettext_lazy as _

from common.utils.stocks import validate_ticker, get_stock_board_history, make_json_trade_info_dict
from finance_majordomo.transactions.forms import TransactionForm
from finance_majordomo.users.models import User
from finance_majordomo.transactions.models import Transaction

# Create your views here.
class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Transaction
    template_name = 'transaction/transaction_list.html'
    context_object_name = 'transaction'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Transaction list")
        context['transaction_list'] = Transaction.objects.all()
        return context


class UsersTransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Transaction
    template_name = 'transaction/transaction_list.html'
    context_object_name = 'stock'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.request.user.username + " " + _("transaction list")
        context['transaction_list'] = Transaction.objects.filter(user=self.request.user.id)
        return context


class AddTransaction(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = 'login'
    form_class = TransactionForm
    template_name = 'base_create_and_update.html'
    success_url = reverse_lazy('transactions')
    success_message = _("Transaction has been successfully added!")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Add new transaction")
        context['button_text'] = _("Add")
        return context

    def post(self, request, *args, **kwargs):
        form = TransactionForm(request.POST)

        if form.is_valid():
            asset_type = form.cleaned_data.get('asset_type')
            transaction_type = form.cleaned_data.get('transaction_type')
            ticker = form.cleaned_data.get('ticker')
            date = form.cleaned_data.get('date')
            price = form.cleaned_data.get('price')
            fee = form.cleaned_data.get('fee')
            quantity = form.cleaned_data.get('quantity')

            user = User.objects.get(id=request.user.id)

            obj = Transaction()
            obj.asset_type = asset_type
            obj.transaction_type = transaction_type
            obj.user = user
            obj.ticker = ticker
            obj.date = date
            obj.price = price
            obj.fee = fee
            obj.quantity = quantity
            obj.save()

            messages.success(request, self.success_message)
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)