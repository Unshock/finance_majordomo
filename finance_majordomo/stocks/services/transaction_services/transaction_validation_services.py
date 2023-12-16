from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal


from finance_majordomo.stocks.models.transaction_models import Transaction
from .transaction_calculation_services import get_asset_quantity_for_portfolio

from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.users.models import User


TRANSACTION_TYPE = Literal["BUY", "SELL"]
VALIDATOR = Literal["add_validation", "delete_validation"]


@dataclass
class TransactionValidator:
    validation_type: VALIDATOR
    asset_id: int
    transaction_type: TRANSACTION_TYPE
    date: datetime.date
    quantity: Decimal


def validate_transaction(user: User, transaction: TransactionValidator) -> bool:
    validator = transaction.validation_type
    asset_id = transaction.asset_id
    transaction_type = transaction.transaction_type
    date = transaction.date
    quantity = transaction.quantity

    if transaction_type == 'SELL' and validator == 'delete_validation' or \
       transaction_type == 'BUY' and validator == 'add_validation':
        return True

    portfolio = user.current_portfolio

    portfolio_transactions = Transaction.objects.filter(
        portfolio=portfolio,
        asset=asset_id,
        date__gte=date).order_by('-date', 'transaction_type')

    transaction_dates = {trans.date for trans in portfolio_transactions}
    transaction_dates.add(date)

    transaction_dates_sorted = sorted(list(transaction_dates), reverse=True)

    for transaction_date in transaction_dates_sorted:
        day_end_balance = get_asset_quantity_for_portfolio(
                portfolio.id, asset_id, date=transaction_date) - quantity
        if day_end_balance < 0:
            return False
    return True


def is_accrued_interest_required(asset: Asset) -> bool:
    return True if asset.group == 'stock_bonds' else False
