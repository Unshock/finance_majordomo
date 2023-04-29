from .models import Transaction
from ..users.models import User


def get_quantity(request, asset_obj, date=None) -> int:

    stock_id = asset_obj.id

    users_specific_asset_transactions = Transaction.objects.filter(
        user=request.user, ticker=stock_id).order_by('date')

    #users_transactions = Transaction.objects.filter(
    #    user=User.objects.get(id=request.user.id))
    #users_specific_asset_transactions = users_transactions.filter(
    #    ticker=Stock.objects.get(id=stock_id)).order_by('date')
    # print(users_specific_asset_transactions, '1')

    if date:
        users_specific_asset_transactions = users_specific_asset_transactions.filter(
            date__lte=date)

    quantity = 0
    date = None
    previous_date = None

    for transaction in users_specific_asset_transactions:
        if date != previous_date and quantity < 0:
            raise ValueError('quantity can\'t be lower than 0')

        previous_date = date
        date = transaction.date

        if transaction.transaction_type == "BUY":
            quantity += transaction.quantity
        elif transaction.transaction_type == "SELL":
            if previous_date is None:
                raise ValueError('quantity cant be lower than 0')
            quantity -= transaction.quantity
        else:
            raise Exception('not buy or sell found')
    return quantity