from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal


from finance_majordomo.transactions.models import Transaction
from .transaction_calculation_services import get_asset_quantity_for_portfolio
from finance_majordomo.users.utils.utils import get_current_portfolio
from ...users.models import User


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

    portfolio = get_current_portfolio(user)

    portfolio_transactions = Transaction.objects.filter(
        portfolio=portfolio,
        asset=asset_id,
        date__gte=date).order_by('-date', 'transaction_type')

    transaction_dates = sorted(
        list({trans.date for trans in portfolio_transactions}), reverse=True)

    for transaction_date in transaction_dates:
        day_end_balance = get_asset_quantity_for_portfolio(
                portfolio.id, asset_id, date=transaction_date) - quantity

        if day_end_balance < 0:
            return False
    return True
