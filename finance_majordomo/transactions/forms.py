import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock, StocksOfUser, Bond, Asset
from finance_majordomo.transactions.models import Transaction
from finance_majordomo.stocks.views import UsersStocks
from .services.transaction_validation_services import validate_transaction, \
    TransactionValidator

from common.utils.stocks import validate_ticker, get_stock_description

from bootstrap4.widgets import RadioSelectButtonGroup

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransactionForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        self.assets_to_display = kwargs.pop('assets_to_display', None)
        self.accrued_interest = kwargs.pop('accrued_interest', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        if self.request.method == "GET":
            self.fields['asset'] = forms.ModelChoiceField(
                queryset=self.assets_to_display,
                label=_('Asset'),
                empty_label=_('Choose stock from the list')
            )

        if self.request.method == "POST":
            self.fields['asset'] = forms.ModelChoiceField(
                queryset=Asset.objects.all(),
            )

        if self.accrued_interest:

            self.fields['accrued_interest'] = forms.DecimalField(
                max_digits=8,
                decimal_places=2,
                label=_('Accrued Interest'),
                widget=forms.TextInput(
                    attrs={"class": "form-control",
                           "rows": "10",
                           "cols": "40",
                           }
                )
            )

            self.fields['accrued_interest'].required = True

        self.order_fields(
            field_order=['transaction_type',
                         'asset',
                         'date',
                         'quantity',
                         'price',
                         'accrued_interest',
                         'fee'
                         ]
        )

    transaction_type = forms.ChoiceField(

        label=_('Transaction type'),
        choices=Transaction.transaction_type_choices,
        widget=RadioSelectButtonGroup(
            # тут опassetции для каждой радио кнопки - хотелось бы расположить их все отцентрованно
            attrs={
                'class': 'form-check-inline d-inline-flex justify-content-center',

                }
        ),
    )

    date = forms.CharField(
        label=_('Date'),
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "placeholder": _('YYYY-MM-DD'),
                   "rows": "10",
                   "cols": "40",
                   }
        ),
    )

    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label=_('Price'),
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "rows": "10",
                   "cols": "40",
                   }
        )
    )

    fee = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label=_('Fee'),
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
        required=False
    )

    quantity = forms.IntegerField(
        label=_('Quantity'),
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "rows": "10",
                   "cols": "40",
                   }
        )
    )

    def clean(self):

        cleaned_data = super().clean()

        #print('cleaned_data', self.cleaned_data)
        #print('cleaned_data', cleaned_data)

        asset_obj = cleaned_data.get('asset')
        transaction_type = cleaned_data.get('transaction_type')
        date = cleaned_data.get('date')
        quantity = cleaned_data.get('quantity')

        if asset_obj and transaction_type and date and quantity:

            transaction_validator = TransactionValidator(
                validation_type='add_validation',
                asset_id=asset_obj.id,
                transaction_type=transaction_type,
                date=date,
                quantity=quantity
            )

            if not validate_transaction(self.request.user,
                                        transaction_validator):
                raise forms.ValidationError(_(
                    'Such a SELL would raise a short sale situation. '
                    'Short sales are not supported! '
                    'Please check the transaction type, date and quantity'))

        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError(_("Price must be more than 0"))
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError(_("Quantity must be more than 0"))
        return quantity

    def clean_accrued_interest(self):
        accrued_interest = self.cleaned_data.get('accrued_interest')
        if accrued_interest and accrued_interest < 0:
            raise ValidationError(_("Accrued interest must not be less than 0"))
        return accrued_interest

    def clean_fee(self):
        fee = self.cleaned_data.get('fee')
        if fee is not None and fee < 0:
            raise ValidationError(_("Fee must be more or equal 0"))
        return fee

    def clean_date(self):

        date = self.cleaned_data.get('date')
        asset = self.cleaned_data.get('asset')

        issuedate = asset.issuedate
        issuedate = datetime.datetime.strftime(issuedate, '%Y-%m-%d')
        if date < issuedate:
            raise ValidationError(
                _("The stock started trading after the specified date") +
                f" ({issuedate})"
            )
        return date
