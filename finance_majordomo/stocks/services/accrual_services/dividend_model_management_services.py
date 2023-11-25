from datetime import datetime

from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.stocks.models.accrual_models import Dividend, AccrualsOfPortfolio
from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.services.transaction_services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


class TogglePortfolioDividendService(Service):

    dividend = ModelField(Dividend)
    portfolio = ModelField(Portfolio)

    def process(self):
        dividend = self.cleaned_data['dividend']
        portfolio = self.cleaned_data['portfolio']

        dividend_of_portfolio = AccrualsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=dividend
        )

        if dividend_of_portfolio.is_received:
            dividend_of_portfolio.is_received = False
            dividend_of_portfolio.save()

        else:
            dividend_of_portfolio.is_received = True
            dividend_of_portfolio.save()


class FillAccrualModel(Service):

    def __init__(self, *args, **kwargs):
        self.accruals_dict = kwargs.pop('accruals_dict')
        super(FillAccrualModel, self).__init__(*args, **kwargs)

    asset = ModelField(Asset)

    def process(self):
        self.asset = self.cleaned_data.get('asset')
        self._fill_accrual_model()

    def _get_self_asset_type(self):
        types_dict = {
            'preferred_share': 'preferred_share',
            'common_share': 'common_share',
            'ofz_bond': 'bond',
            'corporate_bond': 'bond'
        }

        return types_dict.get(self.asset.type)

    def _fill_accrual_model(self):
        asset_type = self._get_self_asset_type()

        for date, accrual_value in self.accruals_dict.items():

            if accrual_value[asset_type]['div']:
                amount = accrual_value[asset_type]['value']

            else:
                continue

            try:
                existing_div = Dividend.objects.get(asset=self.asset, date=date)

                if not existing_div.amount == amount:
                    print('Dividend has been changed while updating. '
                          'Probably mistake!')
                continue

            except Dividend.DoesNotExist:
                self._create_accrual_model_item(date, amount)

        self.asset.latest_accrual_update = datetime.today()
        self.asset.latest_dividend_update = datetime.today()
        self.asset.save()

    def _create_accrual_model_item(self, date, amount):
        dividend = Dividend.objects.create(
            date=date,
            asset=self.asset,
            amount=amount
        )
        dividend.save()


class UpdateAccrualsOfPortfolio(Service):

    portfolio = ModelField(Portfolio)
    transaction = ModelField(Transaction)

    def process(self):

        self.portfolio = self.cleaned_data.get('portfolio')
        self.transaction = self.cleaned_data.get('transaction')

        self._update_accruals_of_portfolio(
            self._get_accruals_transaction_affects()
        )

    def _get_accruals_transaction_affects(self):
        asset = self.transaction.asset
        date = self.transaction.date

        return Dividend.objects.filter(asset=asset, date__gte=date)

    def _create_accrual_of_portfolio(self, accrual):

        AccrualsOfPortfolio.objects.create(
            portfolio=self.portfolio,
            dividend=accrual,
            is_received=False
        )

    def _update_accruals_of_portfolio(self, accruals):

        for accrual in accruals:
            tr_type = self.transaction.transaction_type
            quantity = self.transaction.quantity
            asset = self.transaction.asset
            date = self.transaction.date

            trans_date_quantity = get_asset_quantity_for_portfolio(
                self.portfolio, asset, date
            )

            trans_date_quantity += quantity if tr_type == 'BUY' else -quantity

            try:
                dividend_of_portfolio = AccrualsOfPortfolio.objects.get(
                    portfolio=self.portfolio,
                    dividend=accrual)

                if quantity <= 0:
                    dividend_of_portfolio.is_received = False

            except AccrualsOfPortfolio.DoesNotExist:
                self._create_accrual_of_portfolio(accrual)

                


def update_dividends_of_portfolio(
        portfolio, asset_id, date=None, transaction=None):
    asset_dividends = Dividend.objects.filter(asset=asset_id)

    if date:
        asset_dividends = asset_dividends.filter(date__gte=date)

    for div in asset_dividends:

        tr_quantity = transaction.quantity if transaction.transaction_type == \
                                              'BUY' else transaction.quantity * -1

        quantity = get_asset_quantity_for_portfolio(
            portfolio.id, asset_id, date=div.date) + tr_quantity

        print('DIVIDEND QUANTITTY', quantity, tr_quantity,
              quantity - tr_quantity)

        try:
            dividend_of_portfolio = AccrualsOfPortfolio.objects.get(
                portfolio=portfolio,
                dividend=div)

            if quantity <= 0:
                dividend_of_portfolio.is_received = False

        except AccrualsOfPortfolio.DoesNotExist:
            dividend_of_portfolio = AccrualsOfPortfolio.objects.create(
                portfolio=portfolio,
                dividend=div,
                is_received=False
            )
        print(dividend_of_portfolio)
        dividend_of_portfolio.save()