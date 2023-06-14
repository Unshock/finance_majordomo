    def validate_deletion(self):

        transaction = Transaction.objects.get(id=self.get_object().id)
        transaction_type = transaction.transaction_type

        if transaction_type == 'SELL':
            return True

        quantity = transaction.quantity
        ticker = transaction.ticker
        date = transaction.date

        stock = Stock.objects.get(latname=ticker)
        day_end_balance = get_quantity(self.request, stock,
                                       date=date) - quantity

        if day_end_balance < 0:
            return False

        users_transactions = Transaction.objects.filter(user=User.objects.get(id=self.request.user.id))
        users_specific_asset_transactions = users_transactions.filter(ticker=stock.id).order_by('date')
        users_specific_asset_transactions = users_specific_asset_transactions.filter(date__gt=date)

        if len(users_specific_asset_transactions) == 0:
            return True

        cur_date = date

        for transaction in users_specific_asset_transactions:

            prev_date = cur_date
            cur_date = transaction.date

            if prev_date != cur_date and day_end_balance < 0:
                return False

            if transaction.transaction_type == "BUY":
                day_end_balance += transaction.quantity
            elif transaction.transaction_type == "SELL":
                day_end_balance -= transaction.quantity
            else:
                raise Exception('not BUY or SELL found')

        if day_end_balance < 0:
            return False
        return True