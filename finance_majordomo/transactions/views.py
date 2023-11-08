import django.core.exceptions
import service_objects.errors
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from finance_majordomo.stocks.models import Asset, AssetOfPortfolio

from django.utils.translation import gettext_lazy as _

from finance_majordomo.transactions.forms import TransactionForm

from finance_majordomo.transactions.models import Transaction
from .services.transaction_model_management_services import \
    CreateTransactionService
from .services.transaction_validation_services import validate_transaction, \
    TransactionValidator, is_accrued_interest_required
from ..stocks.services.asset_services import get_or_create_asset_obj, \
    get_all_assets_of_user
from ..stocks.services.user_assets_services import get_current_portfolio


from ..dividends.utils import update_dividends_of_portfolio


class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transaction'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Transaction list")
        context['transaction_list'] = Transaction.objects.all().order_by('date')
        return context


class UsersTransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'stock'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.request.user.username + " " + _(
            "transaction list")
        context['transaction_list'] = Transaction.objects.filter(
            portfolio=get_current_portfolio(self.request.user))\
            .order_by('-date')

        return context


class AddTransaction(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = 'login'
    template_name = 'base_create_and_update.html'

    success_url = reverse_lazy('transactions')
    success_message = _("Transaction has been successfully added!")

    accrued_interest_err_message = _(
        'Accrued Interest is required for the bond group asset')

    unsuccess_url = reverse_lazy('add_transaction')
    unsuccess_message = _("Transaction has not been added!")

    form = TransactionForm()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Add new transaction")
        context['button_text'] = _("Add")
        return context

    def get(self, request, *args, **kwargs):
        assets_to_display_qs = get_all_assets_of_user(request.user)

        asset_id = request.GET.get('asset_id')
        asset_secid = request.GET.get('asset_secid')
        asset_group = request.GET.get('asset_group')

        initial_asset = None
        accrued_interest = False

        if asset_secid and asset_group:

            print('a')

            asset_obj = get_or_create_asset_obj(asset_secid)
            asset_obj_qs = Asset.objects.filter(id=asset_obj.id)

            assets_to_display_qs |= asset_obj_qs
            initial_asset = asset_obj

            self.form.fields['asset'].initial = initial_asset


            if asset_group == 'stock_bonds':
                accrued_interest = True

        elif asset_id:
            print()
            if Asset.objects.get(id=asset_id).group == 'stock_bonds':
                accrued_interest = True
            self.form.fields['asset'].initial = asset_id

        if not assets_to_display_qs:
            return redirect('search')

        self.form.set_assets_to_display(assets_to_display_qs)
        # transaction_form = TransactionForm(
        #     request=request,
        #     assets_to_display=assets_to_display_qs,
        #     accrued_interest=accrued_interest,
        #     accrued_interest_err_message=self.accrued_interest_err_message
        # )
        # transaction_form.initial['asset'] = initial_asset

        return render(
            request,
            self.template_name,
            {'form': self.form,#transaction_form,
             'page_title': _("Add new transaction"),
             'button_text': _('Add')
             }
        )

    def post(self, request, *args, **kwargs):

        form = TransactionForm(
            request.POST,
            request=request,
            accrued_interest=request.POST.get('accrued_interest'),
            accrued_interest_err_message=self.accrued_interest_err_message
        )

        if form.is_valid():
            try:
                CreateTransactionService.execute({
                    'transaction_type': form.cleaned_data['transaction_type'],
                    'date': form.cleaned_data['date'],
                    'price': form.cleaned_data['price'],
                    'fee': form.cleaned_data['fee'],
                    'quantity': form.cleaned_data['quantity'],
                    'asset': form.cleaned_data['asset'],
                    'accrued_interest': form.cleaned_data.get(
                        'accrued_interest'),

                    'user': request.user
                })

                messages.success(request, self.success_message)
                return redirect(self.success_url)

            except Exception as e:
                print(e)

        elif self.accrued_interest_err_message in form.errors.get('__all__'):
            form.add_accrued_interest_field()

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

        asset_obj = transaction.asset

        transaction_validator = TransactionValidator(
            validation_type='delete_validation',
            asset_id=asset_obj.id,
            transaction_type=transaction.transaction_type,
            date=transaction.date,
            quantity=transaction.quantity
        )

        if validate_transaction(self.request.user, transaction_validator):

            update_dividends_of_portfolio(
                portfolio=get_current_portfolio(request.user),
                asset_id=asset_obj.id,
                date=transaction.date,
                transaction=transaction
            )

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
