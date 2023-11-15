from service_objects.fields import ModelField
from service_objects.services import Service
from django import forms

from finance_majordomo.dividends.dividend_services.dividend_model_management_services import \
    UpdateAccrualsOfPortfolio
from finance_majordomo.dividends.utils import update_dividends_of_portfolio
from finance_majordomo.stocks.models import Asset
from finance_majordomo.transactions.models import Transaction
from django.utils.translation import gettext_lazy as _

from finance_majordomo.users.models import User
from finance_majordomo.users.utils.utils import get_current_portfolio


class CreateTransactionService(Service):
    transaction_type = forms.ChoiceField(
        choices=Transaction.transaction_type_choices)
    date = forms.DateField()
    price = forms.DecimalField(max_digits=8, decimal_places=2)
    fee = forms.DecimalField(max_digits=8, decimal_places=2, required=False)
    quantity = forms.IntegerField()
    asset = ModelField(Asset)
    accrued_interest = forms.DecimalField(
        max_digits=8, decimal_places=2, required=False)

    user = ModelField(User)

    def process(self):
        transaction_type = self.cleaned_data['transaction_type']
        date = self.cleaned_data['date']
        price = self.cleaned_data['price']
        fee = self.cleaned_data['fee']
        quantity = self.cleaned_data['quantity']
        asset = self.cleaned_data['asset']
        accrued_interest = self.cleaned_data.get('accrued_interest')

        user = self.cleaned_data.get('user')
        current_portfolio = get_current_portfolio(user)

        transaction_obj = Transaction.objects.create(
            transaction_type=transaction_type,
            portfolio=current_portfolio,
            asset=asset,
            date=date,
            price=price,
            accrued_interest=accrued_interest,
            fee=fee,
            quantity=quantity
        )

        print(transaction_obj)

        # Если в ходе поиска добавляем первую транзакцию для актива, 
        # то добавляем актив в AssetsOfUser
        if asset not in user.assetsofuser_set.all():
            asset.users.add(user)
            asset.save()

        if asset not in current_portfolio.assetofportfolio_set.all():
            current_portfolio.asset.add(asset)
            current_portfolio.save()

        if asset.group in ['stock_shares', 'stock_bonds']:
            UpdateAccrualsOfPortfolio.execute({
                'portfolio': current_portfolio,
                'transaction': transaction_obj
            })
            # update_dividends_of_portfolio(
            #     current_portfolio, asset.id, date, transaction_obj)

        return transaction_obj

    def post_process(self):
        # Send verification email (check out django-herald)
        print("POSTPROCESS")
        #VerifyEmailNotification(self.booking).send()