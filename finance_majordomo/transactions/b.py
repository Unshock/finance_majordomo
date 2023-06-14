    def validate_form(self, form):

        error_text = _('Such a SELL would raise a short sale situation. '
                       'Short sales are not supported!')
        # form = TransactionForm(self.request.POST)
        transaction_type = form.cleaned_data.get('transaction_type')

        stock_latname = form.cleaned_data.get('ticker')
        date = form.cleaned_data.get('date')

        stock = Stock.objects.get(latname=stock_latname)
        print(stock.issuedate)
        issuedate = datetime.datetime.strftime(stock.issuedate, '%Y-%m-%d')

        print(issuedate)

        if date < issuedate:
            form.add_error('date', _('The stock started trading'
                                     ' after the specified date'))
            return False

        if transaction_type == 'BUY':
            return True

        quantity = form.cleaned_data.get('quantity')
        day_end_balance = get_quantity(self.request, stock,
                                       date=date) - quantity

        if day_end_balance < 0:
            form.add_error('quantity', error_text)
            return False

        users_transactions = Transaction.objects.filter(
            user=User.objects.get(id=self.request.user.id))
        users_specific_asset_transactions = users_transactions.filter(
            ticker=stock.id).order_by('date')
        users_specific_asset_transactions = users_specific_asset_transactions.filter(date__gt=date)

        print(users_specific_asset_transactions)

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