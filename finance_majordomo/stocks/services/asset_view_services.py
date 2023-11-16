from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.db.models import QuerySet
from service_objects.fields import ModelField
from service_objects.services import Service

from finance_majordomo.stocks.models import Asset
from finance_majordomo.users.models import User, Portfolio


class GetAssetsOfUser(Service):

    user = ModelField(User)

    def process(self) -> QuerySet:
        self.user = self.cleaned_data.get('user')
        return self._get_assets_of_user()

    def _get_portfolios_of_user(self):
        return self.user.portfolio_set.all()

    def _get_assets_of_user(self):

        portfolios_of_user = self._get_portfolios_of_user()

        assets_of_user = Asset.objects.none()

        for portfolio in portfolios_of_user:

            assets_of_user |= Asset.objects.filter(
                id__in=portfolio.assetofportfolio_set.values('asset'))

        return assets_of_user


@dataclass
class PortfolioAssetItem:
    asset_name: str
    asset_quantity: Decimal
    id: int
    amount: Decimal
    sum: Decimal
    date: datetime.date
    is_received: bool
    is_upcoming: bool


class PortfolioAssetsViewContextService(Service):

    portfolio = ModelField(Portfolio)

    def process(self):
        self.portfolio = self.cleaned_data.get('portfolio')
        
        
