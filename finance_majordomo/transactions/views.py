from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from finance_majordomo.stocks.models import Stock, StocksOfUser

from django.utils.translation import gettext_lazy as _

from finance_majordomo.transactions.forms import TransactionForm
from finance_majordomo.users.models import User
from finance_majordomo.transactions.models import Transaction
from ..stocks.views import AddStock, add_asset
from ..transactions.utils import validate_transaction
from ..dividends.utils import update_dividends_of_user


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
        context['page_title'] = self.request.user.username + " " + _(
            "transaction list")
        context['transaction_list'] = Transaction.objects.filter(
            user=self.request.user.id)
        return context


class AddTransaction(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = 'login'
    #form_class = TransactionForm()
    template_name = 'base_create_and_update.html'
    #alter for beauty for tests:
    #template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions')
    success_message = _("Transaction has been successfully added!")

    unsuccess_url = reverse_lazy('add_transaction')
    unsuccess_message = _("Transaction has not been added!")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Add new transaction")
        context['button_text'] = _("Add")
        return context

    def get(self, request, *args, **kwargs):

        asset_id = request.GET.get('asset_id')
        print(asset_id)
        asset_secid = request.GET.get('asset_secid')
        asset_group = request.GET.get('asset_group')

        initial_ticker = None

        if asset_secid:

            try:
                asset = Stock.objects.get(ticker=asset_secid)

            except Stock.DoesNotExist:
                # ADD ASSET TO DB
                asset = add_asset(asset_secid)

            transaction_form = TransactionForm(
                request=request,
                asset=Stock.objects.filter(id=asset.id))
            transaction_form.initial['ticker'] = asset.id

            return render(
                request,
                self.template_name,
                {'form': transaction_form,
                 'page_title': _("Add new transaction"),
                 'button_text': _('Add')
                 }
            )

        elif asset_id:
            initial_ticker = asset_id

        transaction_form = TransactionForm(request=request)
        transaction_form.initial['ticker'] = initial_ticker
        print(transaction_form.initial['ticker'])
        print(type(transaction_form.initial['ticker']))
        
        
        
        
        
        
        
        
        
        
        
        

        # if asset_id:
        #     #transaction_form.initial['ticker'] = asset_id
        #     initial_ticker = asset_id
        # 
        # elif asset_secid:
        # 
        #     try:
        #         asset = Stock.objects.get(ticker=asset_secid)
        # 
        #     except Stock.DoesNotExist:
        #         asset = add_asset(asset_secid)
        # 
        #     #transaction_form.initial['ticker'] = asset.id
        #     initial_ticker = asset.id
        # 
        # transaction_form = TransactionForm(asset=Stock.objects.filter(id=asset.id))
        # transaction_form.initial['ticker'] = initial_ticker

        return render(
            request,
            self.template_name,
            {'form': transaction_form,
             'page_title': _("Add new transaction"),
             'button_text': _('Add')
             }
        )

    def post(self, request, *args, **kwargs):

        form = TransactionForm(request.POST, request=request)

        if form.is_valid():

            asset_type = form.cleaned_data.get('asset_type')
            transaction_type = form.cleaned_data.get('transaction_type')
            ticker = form.cleaned_data.get('ticker')
            date = form.cleaned_data.get('date')
            price = form.cleaned_data.get('price')
            fee = form.cleaned_data.get('fee')
            quantity = form.cleaned_data.get('quantity')

            user = request.user

            # Если в ходе поиска добавляем первую транзакцию для актива, 
            # то добавляем актив в StocksOfUser
            if ticker.id not in user.stocksofuser_set.values_list('stock'):
                ticker.users.add(user)
                ticker.save()

            obj = Transaction.objects.create(
                asset_type=asset_type,
                transaction_type=transaction_type,
                user=user,
                ticker=ticker,
                date=date,
                price=price,
                fee=fee,
                quantity=quantity
            )

            obj.save()

            if obj.asset_type == 'STOCK':
                stock_obj = Stock.objects.get(id=obj.ticker.id)
                update_dividends_of_user(request, stock_obj, date, obj)

            messages.success(request, self.success_message)
            return redirect(self.success_url)

        #return super().post(request, *args, **kwargs)
        return render(
            request,
            self.template_name,
            {'form': form,
             'page_title': _("Add new transaction"),
             'button_text': _('Add')
             }
        )


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

        transaction = self.get_object()

        # править если в транзакциях будут не только стоки
        asset_obj = Stock.objects.get(latname=transaction.ticker)

        validation_dict = {
            'validator': 'delete_validator',
            'asset_obj': asset_obj,
            'transaction_type': transaction.transaction_type,
            'date': transaction.date,
            'quantity': transaction.quantity
        }

        if validate_transaction(self.request, validation_dict):
            print(asset_obj)
            print(''
                  'fffffffffffff')
            print(asset_obj.asset_type)
            if asset_obj.asset_type == 'stocks':
                print('update start')
                update_dividends_of_user(
                    request, asset_obj, transaction.date, transaction)

            return super().post(request, *args, **kwargs)

        else:
            messages.error(self.request, self.error_message)
            return redirect('transactions')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Delete transaction")
        context['button_text'] = _("Delete")
        context['delete_object'] = str(self.get_object())
        return context
