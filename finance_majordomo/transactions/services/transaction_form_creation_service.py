from django.http import QueryDict
from service_objects.fields import ModelField
from service_objects.services import Service
from django import forms

from finance_majordomo.stocks.models import Asset
from finance_majordomo.stocks.services.asset_services import \
    get_or_create_asset_obj, get_all_assets_of_user
from finance_majordomo.transactions.forms import TransactionForm
from finance_majordomo.users.models import User
from finance_majordomo.users.utils.utils import get_current_portfolio

class CreateTransactionFormService(Service):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(CreateTransactionFormService, self).__init__(*args, **kwargs)

    asset_id = forms.IntegerField(required=False)
    asset_secid = forms.CharField(required=False)
    asset_group = forms.CharField(required=False)
    primary_boardid = forms.CharField(required=False)
    accrued_interest_err_message = forms.CharField()

    user = ModelField(User, required=True)

    def process(self):
        self._create_form()

        self._get_and_set_initial_asset_id()
        self._set_assets_to_display_to_form()
        self._add_accrued_interest_to_form()

        return self.form

    def _get_and_set_initial_asset_id(self):

        self.asset_id = self.cleaned_data.get('asset_id')
        asset_secid = self.cleaned_data.get('asset_secid')
        primary_boardid = self.cleaned_data.get('primary_boardid')

        if asset_secid:
            asset = get_or_create_asset_obj(asset_secid, primary_boardid)
            self.asset_id = asset.id

        self.form.fields['asset'].initial = self.asset_id

    def _set_assets_to_display_to_form(self):

        assets_to_display = self._get_assets_to_display_qs()

        if assets_to_display:
            self.form.set_assets_to_display(assets_to_display)

        else:
            raise ValueError('No assets to display found')

    def _get_assets_to_display_qs(self):

        user = self.cleaned_data.get('user')
        assets_to_display_qs = get_all_assets_of_user(user)

        if self.asset_id:
            assets_to_display_qs |= Asset.objects.filter(id=self.asset_id)

        return assets_to_display_qs

    def _add_accrued_interest_to_form(self):
        if self.asset_id and Asset.objects.get(
                id=self.asset_id).group == 'stock_bonds':
            self.form.add_accrued_interest_field()

    def _create_form(self):

        form_data = None if self.request.method == 'GET' else self.request.POST

        self.form = TransactionForm(
            form_data,
            user=self.cleaned_data.get('user'),
            accrued_interest_err_message=self.cleaned_data.get(
                'accrued_interest_err_message'),
        )

