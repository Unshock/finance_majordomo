import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from finance_majordomo.stocks.models import Stock, StocksOfUser, Bond, Asset
from finance_majordomo.transactions.models import Transaction
from finance_majordomo.stocks.views import UsersStocks
from .utils import validate_transaction

from common.utils.stocks import validate_ticker, get_stock_description

from bootstrap4.widgets import RadioSelectButtonGroup


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransactionForm(ModelForm):

    # def __init__(self, user, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    # 
    #     self.fields['ticker'].queryset = Stock.objects.filter(
    #         id__in=user.stocksofuser_set.values_list('stock'))

        #print(user, user.stocksofuser_set.values_list('stock'))
        #print(Stock.objects.filter(id__in=user.stocksofuser_set.values_list('stock')))

        #     StocksOfUser.objects.filter(user=user)
        # print(StocksOfUser.objects.filter(user=user))
        # if ticker.id not in user.stocksofuser_set.values_list('stock')


    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        self.assets_to_display = kwargs.pop('assets_to_display', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        self.fields['ticker'].label = _('Share')
        self.fields['ticker'].empty_label = _('Choose stock from the list')
        self.fields['ticker'].queryset = self.assets_to_display

        # print('3', self.fields['ticker'].queryset)
        # print('4', self.assets_to_display, type(self.assets_to_display))
        # if self.request.method == "GET":
        #     print('get')
        #     # print('1', Stock.objects.filter(
        #     #     id__in=self.request.user.stocksofuser_set.values_list('stock')))
        #     # 
        #     # self.fields['ticker'].qeuryset = Asset.objects.filter(
        #     #     id__in=self.request.user.assetsofuser_set.values_list('asset'))
        #     print('5', self.fields['ticker'].queryset)
        # 
        #     self.fields['ticker'].queryset = self.assets_to_display
        # 
        #     print('6', self.fields['ticker'].queryset)
        #     # print('2', self.fields['ticker'].queryset)
        # 
        #     # if self.asset:
        #     #     self.fields['ticker'].queryset |= self.asset
        # 
        if self.request.method == "POST":

            self.fields['ticker'].queryset = Asset.objects.all()

        #super(TransactionForm, self).__init__(*args, **kwargs)
        # self.helper = FormHelper()
        # self.helper.form_id = 'id-exampleForm'
        # self.helper.form_class = 'blueForms'
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'submit_survey'
        # 
        # self.helper.add_input(Submit('submit', 'Submit'))

    transaction_type = forms.ChoiceField(
        #initial='BUY',

        label=_('Transaction type'),
        choices=Transaction.transaction_type_choices,
        widget=RadioSelectButtonGroup(
            # тут опassetции для каждой радио кнопки - хотелось бы расположить их все отцентрованно
            attrs={'class': 'form-check-inline d-inline-flex justify-content-center',

                   }
        ),
    )

    # ticker = forms.ModelChoiceField(
    #     label=_('Share'),
    #     #queryset=Stock.objects.all(),
    #     #queryset=Stock.objects.filter(user=self.user),
    #     empty_label=_('Choose stock from the list'),
    # 
    #     )

    # ticker_new = forms.CharField(
    #     label=_("Ticker"),
    # )

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

        asset_obj = cleaned_data.get('ticker')
        transaction_type = cleaned_data.get('transaction_type')
        date = cleaned_data.get('date')
        quantity = cleaned_data.get('quantity')

        if asset_obj and transaction_type and date and quantity:

            validate_dict = {
                'validator': 'add_validator',
                #'asset_obj': Stock.objects.get(latname=ticker.latname),
                'asset_obj': asset_obj,
                'transaction_type': transaction_type,
                'date': date,
                'quantity': quantity
            }

            if not validate_transaction(self.request, validate_dict):
                raise ValidationError(_(
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

    def clean_fee(self):
        fee = self.cleaned_data.get('fee')
        if fee is not None and fee < 0:
            raise ValidationError(_("Fee must be more or equal 0"))
        return fee

    def clean_date(self):
        date = self.cleaned_data.get('date')
        asset = self.cleaned_data.get('ticker')

        # print(self.cleaned_data)
        # print('asset', type(asset), asset)
        # print(Stock.objects.get(latname=asset.latname))
        #issuedate = Stock.objects.get(latname=asset).issuedate
        print(self.cleaned_data.items())
        issuedate = asset.issuedate
        issuedate = datetime.datetime.strftime(issuedate, '%Y-%m-%d')
        if date < issuedate:
            raise ValidationError(
                _("The stock started trading after the specified date") +
                f" ({issuedate})"
            )
        return date

    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'ticker',
            #'ticker_new',
            'date',
            'price',
            'fee',
            'quantity',
        ]

