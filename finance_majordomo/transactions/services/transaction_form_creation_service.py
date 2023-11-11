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
        self.accrued_interest_err_message = kwargs.pop('accrued_interest_err_message')
        super(CreateTransactionFormService, self).__init__(*args, **kwargs)

    asset_id = forms.IntegerField(required=False)
    asset_secid = forms.CharField(required=False)
    asset_group = forms.CharField(required=False)

    asset = ModelField(Asset, required=False)
    user = ModelField(User, required=True)

    def process(self):
        print('555', self.request)
        #setattr(self, 'form', TransactionForm())
        self._create_form()

        self._get_and_set_initial_asset_id()
        self._set_assets_to_display_to_form()
        self._add_accrued_interest_to_form()
        print('6666633333')
        #print(str(self.form), '51515151')

        return self.form

        asset_id = self.cleaned_data['asset_id']
        asset_secid = self.cleaned_data['asset_secid']
        asset_group = self.cleaned_data['asset_group']

        user = self.cleaned_data.get('user')


        assets_to_display_qs = self._get_assets_to_display_qs()



        if asset_secid and asset_group:

            self.form.fields['asset'].initial = get_or_create_asset_obj(asset_secid)

            if asset_group == 'stock_bonds':
                form.add_accrued_interest_field()

        elif asset_id:
            if Asset.objects.get(id=asset_id).group == 'stock_bonds':
                form.add_accrued_interest_field()
            self.form.fields['asset'].initial = asset_id

        if not assets_to_display_qs:
            return redirect('search')

        self.form.set_assets_to_display(assets_to_display_qs)

    def _get_and_set_initial_asset_id(self):
        print('11')
        print('1', self.cleaned_data['asset'])
        print(self.cleaned_data.items())
        print(self.cleaned_data.get('asset_secid'))
        print(self.cleaned_data.get('asset_id'))
        print(self.cleaned_data.get('asset'))

        if self.cleaned_data['asset']:
            print('getatr asset', self.asset)
            self.asset_id = self.asset.id

        asset_secid = self.cleaned_data.get('asset_secid')

        if asset_secid:
            asset = get_or_create_asset_obj(asset_secid)
            self.form.fields['asset'].initial = asset.id
            self.cleaned_data['asset_id'] = asset.id
            print(asset, '1112321312312312312312312312312312')
            print(self.form.fields['asset'].initial)
            print(asset.id)

        if self.cleaned_data['asset_id']:
            print(self.cleaned_data['asset_id'], '111111111111111111111111111111')
            self.form.fields['asset'].initial = self.cleaned_data['asset_id']

    def _set_assets_to_display_to_form(self):

        assets_to_display = self._get_assets_to_display_qs()

        if assets_to_display:
            self.form.set_assets_to_display(assets_to_display)

    def _get_assets_to_display_qs(self):

        user = self.cleaned_data.get('user')

        assets_to_display_qs = get_all_assets_of_user(user)
        print('4')

        if self.cleaned_data['asset_id']:
            assets_to_display_qs |= Asset.objects.filter(id=self.cleaned_data['asset_id'])
        #print('5')
        return assets_to_display_qs

    def _add_accrued_interest_to_form(self):
        print('1111')
        if self.cleaned_data['asset_id'] and Asset.objects.get(
                id=self.cleaned_data['asset_id']).group == 'stock_bonds':
            print('2222')
            self.form.add_accrued_interest_field()


    def _create_form(self):

        print(self.request, '666666666666666666')
        print(self.request.method)
        print(self.request.GET, type(self.request.GET))
        
        form_data = None if self.request.method == 'GET' else self.request.POST

        self.form = TransactionForm(
            form_data,
            user=self.cleaned_data.get('user'),
            accrued_interest_err_message=self.accrued_interest_err_message,
        )

