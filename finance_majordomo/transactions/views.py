from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from finance_majordomo.stocks.forms import StockForm
from finance_majordomo.stocks.models import Stock

from django.utils.translation import gettext_lazy as _

from common.utils.stocks import validate_ticker, get_stock_board_history, make_json_trade_info_dict
from finance_majordomo.transactions.forms import TransactionForm
from finance_majordomo.users.models import User
from finance_majordomo.transactions.models import Transaction
from finance_majordomo.stocks.views import UsersStocks

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

    unsuccess_url = reverse_lazy('add_transaction')
    unsuccess_message = _("Transaction has not been added!")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Add new transaction")
        context['button_text'] = _("Add")
        return context

    def post(self, request, *args, **kwargs):
        form = TransactionForm(request.POST)
        #print('f', form.cleaned_data)
        if form.is_valid():
            if self.validate_form(form):
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
            return render(request, self.template_name, {'form': form,
                                                        'page_title': _("Add new transaction"),
                                                        'button_text': _("Add")
                                                        })

        return render(request, self.template_name, {'form': form,
                                                    'page_title': _("Add new transaction"),
                                                    'button_text': _('Add')
                                                    })


            # else:
            #     #form.errors()
            #     messages.error(request, self.unsuccess_message)
            #     return redirect(self.unsuccess_url)
        #return super().post(request, *args, **kwargs)

    def validate_form(self, form):

        error_text = _('Such a SELL would raise a short sale situation. '
                       'Short sales are not supported!')
        # form = TransactionForm(self.request.POST)
        transaction_type = form.cleaned_data.get('transaction_type')

        if transaction_type == 'BUY':
            return True

        quantity = form.cleaned_data.get('quantity')
        ticker = form.cleaned_data.get('ticker')
        date = form.cleaned_data.get('date')

        stock = Stock.objects.get(name=ticker)
        day_end_balance = UsersStocks.get_current_quantity(self.request, stock.id, date=date) - quantity

        if day_end_balance < 0:
            form.add_error('quantity', error_text)
            return False

        users_transactions = Transaction.objects.filter(user=User.objects.get(id=self.request.user.id))
        users_specific_asset_transactions = users_transactions.filter(ticker=stock.id).order_by('date')
        users_specific_asset_transactions = users_specific_asset_transactions.filter(date__gt=date)

        print(users_specific_asset_transactions)

        if len(users_specific_asset_transactions) == 0:
            return True

        cur_date = date

        for transaction in users_specific_asset_transactions:
            print(transaction)
            print('transaction_date: ', transaction.date)

            prev_date = cur_date
            cur_date = transaction.date

            if prev_date != cur_date and day_end_balance < 0:
                form.add_error('quantity', error_text)
                return False

            if transaction.transaction_type == "BUY":
                day_end_balance += transaction.quantity
            elif transaction.transaction_type == "SELL":
                day_end_balance -= transaction.quantity
            else:
                raise Exception('not BUY or SELL found')

        if day_end_balance < 0:
            form.add_error('quantity', error_text)
            return False
        return True

        #
        # print("VALIDATION")
        # print('tika', form.cleaned_data.get('ticker'))
        # stock = Stock.objects.get(name=form.cleaned_data['ticker'])
        # print(stock)
        # total_stocks = UsersStocks.get_current_quantity(self.request, stock.id)
        # print(form.cleaned_data['quantity'], '999', total_stocks)
        #
        # print(form.cleaned_data.get('transaction_type'), form.cleaned_data.get('quantity'))
        # if form.cleaned_data['transaction_type'] == 'SELL' and form.cleaned_data['quantity'] > total_stocks:
        #     form.add_error('quantity', _('You don\'t have enough stocks'))
        #     return False
        # return True

    def form_valid(self, form):
        print("VALIDATION 2 ")
        form.instance.creator = self.request.user
        print('validation 2 ok')
        return super().form_valid(form)

class DeleteTransaction(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = 'login'
    model = Transaction
    template_name = "base_delete.html"
    success_url = reverse_lazy('transactions')
    success_message = _("Transaction has been successfully deleted!")
    error_message = _('Delete of this BUY would raise a short sale situation. '
                      'Short sales are not supported!')

    # def dispatch(self, request, *args, **kwargs):
    #     if self.get_object().creator.id == request.user.id \
    #             or request.user.is_staff:
    #         return super().dispatch(request, *args, **kwargs)
    #     messages.error(request, _('You can delete only your labels'))
    #     return redirect('labels')

    def post(self, request, *args, **kwargs):

        if self.validate_deletion():
            return super().post(request, *args, **kwargs)

        else:
            messages.error(self.request, self.error_message)
            return redirect('transactions')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Delete stock")
        context['button_text'] = _("Delete")
        context['delete_object'] = str(
            Transaction.objects.get(id=self.get_object().id))
        return context

    def validate_deletion(self):

        transaction = Transaction.objects.get(id=self.get_object().id)
        transaction_type = transaction.transaction_type

        if transaction_type == 'SELL':
            return True

        quantity = transaction.quantity
        ticker = transaction.ticker
        date = transaction.date

        stock = Stock.objects.get(name=ticker)
        day_end_balance = UsersStocks.get_current_quantity(self.request, stock.id, date=date) - quantity

        if day_end_balance < 0:
            return False

        users_transactions = Transaction.objects.filter(user=User.objects.get(id=self.request.user.id))
        users_specific_asset_transactions = users_transactions.filter(ticker=stock.id).order_by('date')
        users_specific_asset_transactions = users_specific_asset_transactions.filter(date__gt=date)

        if len(users_specific_asset_transactions) == 0:
            return True

        cur_date = date

        for transaction in users_specific_asset_transactions:

            prev_date = cur_date
            cur_date = transaction.date

            if prev_date != cur_date and day_end_balance < 0:
                return False

            if transaction.transaction_type == "BUY":
                day_end_balance += transaction.quantity
            elif transaction.transaction_type == "SELL":
                day_end_balance -= transaction.quantity
            else:
                raise Exception('not BUY or SELL found')

        if day_end_balance < 0:
            return False
        return True

def validate_transaction(request, ticker, quantity, date):
    transaction = Transaction.objects.get(id=self.get_object().id)
    transaction_type = transaction.transaction_type

    if transaction_type == 'SELL':
        return True

    quantity = transaction.quantity
    ticker = transaction.ticker
    date = transaction.date

    stock = Stock.objects.get(name=ticker)
    day_end_balance = UsersStocks.get_current_quantity(request, stock.id, date=date) - quantity

    if day_end_balance < 0:
        return False

    users_transactions = Transaction.objects.filter(user=User.objects.get(id=self.request.user.id))
    users_specific_asset_transactions = users_transactions.filter(ticker=stock.id).order_by('date')
    users_specific_asset_transactions = users_specific_asset_transactions.filter(date__gt=date)

    if len(users_specific_asset_transactions) == 0:
        return True

    cur_date = date

    for transaction in users_specific_asset_transactions:

        prev_date = cur_date
        cur_date = transaction.date

        if prev_date != cur_date and day_end_balance < 0:
            return False

        if transaction.transaction_type == "BUY":
            day_end_balance += transaction.quantity
        elif transaction.transaction_type == "SELL":
            day_end_balance -= transaction.quantity
        else:
            raise Exception('not BUY or SELL found')

    if day_end_balance < 0:
        return False
    return True
# не используется, не доделана - можно задраить