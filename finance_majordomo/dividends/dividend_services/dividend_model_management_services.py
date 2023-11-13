from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.dividends.models import Dividend, DividendsOfPortfolio
from finance_majordomo.users.models import Portfolio


class TogglePortfolioDividendService(Service):

    dividend = ModelField(Dividend)
    portfolio = ModelField(Portfolio)

    def process(self):
        dividend = self.cleaned_data['dividend']
        portfolio = self.cleaned_data['portfolio']

        dividend_of_portfolio = DividendsOfPortfolio.objects.get(
            portfolio=portfolio, dividend=dividend
        )

        if dividend_of_portfolio.is_received:
            dividend_of_portfolio.is_received = False
            dividend_of_portfolio.save()

        else:
            dividend_of_portfolio.is_received = True
            dividend_of_portfolio.save()
