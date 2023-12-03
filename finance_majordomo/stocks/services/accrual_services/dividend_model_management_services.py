from datetime import datetime

from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.stocks.models.accrual_models import Dividend, AccrualsOfPortfolio
from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.stocks.models.transaction_models import Transaction
from finance_majordomo.stocks.services.transaction_services.transaction_calculation_services import \
    get_asset_quantity_for_portfolio
from finance_majordomo.users.models import Portfolio


def execute_toggle_portfolio_accrual_service(accrual: Dividend,
                                             portfolio: Portfolio):
    """
    :param accrual: Accrual model object
    :param portfolio: Portfolio model object
    :return: returns nothing but toggles receiving (received/not received) of 
        specified Accrual in specified Portfolio
    """

    TogglePortfolioDividendService.execute({
        'accrual': accrual,
        'portfolio': portfolio
    })


class TogglePortfolioDividendService(Service):

    accrual = ModelField(Dividend)
    portfolio = ModelField(Portfolio)

    def process(self):
        accrual = self.cleaned_data['accrual']
        portfolio = self.cleaned_data['portfolio']

        accrual_of_portfolio = AccrualsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=accrual
        )

        if accrual_of_portfolio.is_received:
            accrual_of_portfolio.is_received = False
            accrual_of_portfolio.save()

        else:
            accrual_of_portfolio.is_received = True
            accrual_of_portfolio.save()


def execute_accrual_model_filling_service(asset: Asset, accrual_dict: dict):
    """
    :param asset: Asset model object
    :param accrual_dict: dictionary of accruals
    :return: returns nothing fills Accrual model of Asset with accruals from
        specified accrual dictionary
    """
    AccrualModelFillingService.execute({
        'asset': asset,
        'accrual_dict': accrual_dict
    })


class AccrualModelFillingService(Service):

    def __init__(self, *args, **kwargs):
        self.accruals_dict = kwargs.pop('accruals_dict')
        super().__init__(*args, **kwargs)

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
                    # logging!
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


def execute_update_accruals_of_portfolio(
        portfolio: Portfolio, transaction: Transaction):
    """
    :param portfolio: Asset model object
    :param transaction: Transaction model object
    :return: adding of deleting Transaction offers changes of accruals of
        the specified portfolio so the func updates portfolio accrual data
    """
    UpdateAccrualsOfPortfolio.execute({
        'portfolio': portfolio,
        'transaction': transaction
    })


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
