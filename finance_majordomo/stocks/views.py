import json
from decimal import Decimal

import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist

from finance_majordomo.stocks.forms import StockForm
from finance_majordomo.stocks.models import Stock, ProdCalendar
from finance_majordomo.transactions.models import Transaction

from django.utils.translation import gettext_lazy as _

from common.utils.stocks import validate_ticker, get_stock_board_history, make_json_trade_info_dict, get_date_status, \
    get_stock_current_price, make_json_last_price_dict, get_stock_description
from finance_majordomo.users.models import User


class Stocks(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Stock
    template_name = 'stocks/stock_list.html'
    context_object_name = 'stock'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Stock list")
        context['stock_list'] = Stock.objects.all()
        return context


class UsersStocks(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Stock
    transaction = Transaction
    template_name = 'stocks/user_stock_list.html'
    context_object_name = 'stock'

    def get_context_data(self, *, object_list=None, **kwargs):
        #print(self.request.user.id)
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.request.user.username + " " + _("stock list")

        user_stock_data = self.get_user_stock_data()

        total_price = {'total_purchase_price': self.get_total_purchase_price(user_stock_data),
                       'total_current_price': self.get_total_current_price(user_stock_data),
                       'total_percent_result': self.get_percent_result(
                           Decimal(self.get_total_purchase_price(user_stock_data)),
                           Decimal(self.get_total_current_price(user_stock_data))
                       )
                       }


        #users_stocks = Stock.objects.filter(usersstocks__user_id=self.request.user.id)
        #users_stocks = [(obj, self.get_current_quantity(self.request, obj.id), self.get_purchace_price(self.request, obj.id), self.get_current_price(obj.id)) for obj in users_stocks]
        #print(users_stocks)
        # print([el for el in users_stocks])
        # self.get_current_quantity(1)
        context['fields_to_display'] = json.loads(self.request.user.fields_to_display)
        print('FIELDS_TO', context['fields_to_display'])
        context['stock_list'] = user_stock_data
        context['total_price'] = total_price
        return context

    def get_total_purchase_price(self, stock_list):
        total_purchase_price = sum([stock['purchase_price'] for stock in stock_list])
        return "{:.2f}".format(total_purchase_price)

    def get_total_current_price(self, stock_list):
        total_current_price = sum([float(stock['current_price']) for stock in stock_list])
        return "{:.2f}".format(total_current_price)

    def get_user_stock_data(self):
        request = self.request
        user_stocks = Stock.objects.filter(usersstocks__user_id=request.user.id)

        #print(user_stocks)

        user_stock_data = []
        for stock in user_stocks:
            current_quantity = self.get_current_quantity(request, stock.id)

            if current_quantity == 0:
                continue

            purchase_price = self.get_purchace_price(request, stock.id)
            current_price = self.get_current_price(stock)
            percent_result = self.get_percent_result(purchase_price, current_price)

            user_stock_data.append({'id': stock.id,
                                    'ticker': stock.ticker,
                                    'name': stock.name,
                                    'currency': stock.currency,
                                    'quantity': current_quantity,
                                    'purchase_price': purchase_price,
                                    'current_price': "{:.2f}".format(current_price),
                                    'percent_result': percent_result
                                    })

        return user_stock_data

    @staticmethod
    def get_current_quantity(request, stock_id, date=None):
        users_transactions = Transaction.objects.filter(user=User.objects.get(id=request.user.id))
        users_specific_asset_transactions = users_transactions.filter(ticker=Stock.objects.get(id=stock_id)).order_by('date')
        #print(users_specific_asset_transactions, '1')

        if date:
            users_specific_asset_transactions = users_specific_asset_transactions.filter(date__lte=date)
        #print(users_specific_asset_transacions)
        #a = users_specific_asset_transacions.order_by('date')
        #if date is None:
        #    g = UsersStocks.get_current_quantity(request, stock_id, '2023-02-22')
        #    if date is None:
        #        print(stock_id, 'ALTER G', g)
        #for el in a:
        #    print(el.date)
        #print(a)

        result = 0
        date = None
        previous_date = None

        for transaction in users_specific_asset_transactions:
            #print(date, prev_date)
            if date != previous_date and result < 0:
                raise ValueError('quantity cant be lower than 0')
            #print(transaction, transaction.date)
            previous_date = date
            date = transaction.date

            if transaction.transaction_type == "BUY":
                result += transaction.quantity
            elif transaction.transaction_type == "SELL":
                if previous_date is None:
                    raise ValueError('quantity cant be lower than 0')
                result -= transaction.quantity
            else:
                raise Exception('not buy or sell found')
        return result

    @staticmethod
    def get_purchace_price(request, stock_id):
        # С учетом метода FIFO
        users_transacions = Transaction.objects.filter(user=User.objects.get(id=request.user.id))
        users_specific_asset_transacions = users_transacions.filter(ticker=Stock.objects.get(id=stock_id)).order_by('date')
        result = 0
        purchase_list = []
        total_sold = 0
        purchase_price = 0
        for transaction in users_specific_asset_transacions:
            if transaction.transaction_type == "BUY":
                result += transaction.quantity
                purchase_list.append({
                    'quantity': transaction.quantity,
                    'price': transaction.price
                })
            elif transaction.transaction_type == "SELL":
                result -= transaction.quantity
                total_sold += transaction.quantity
            else:
                raise Exception('not buy nor sell')

        for elem in purchase_list:
            #print('total_sold', total_sold)
            if elem['quantity'] >= total_sold:
                elem['quantity'] -= total_sold
                total_sold = 0

            else:
                sold = elem['quantity']
                elem['quantity'] = 0
                total_sold -= sold

            purchase_price += elem['quantity'] * elem['price']

            if total_sold < 0:
                raise Exception('тотал меньше 0')


        return purchase_price

        #return result

    def get_current_price(self, stock):

        stock_obj = StockData(stock)
        stock = stock_obj.actualize_stock_data()
        last_date_dt, status, update_time = stock_obj.get_data_last_date()
        #print('last_date_dt', last_date_dt)
        last_day_str = datetime.datetime.strftime(last_date_dt, '%Y-%m-%d')
        #stock_data = stock.stock_data

        #stock_data = Stock.objects.get(id=stock.id).stock_data
        stock_data_json = json.loads(stock.stock_data)

        #закомментирован неактуальный код
        #last_day = max(json_stock_data['TRADEINFO'].keys())
        #today = datetime.datetime.today().strftime('%Y-%m-%d')

        # if last_day < today:
        #
        #     actualizator = StockData(stock)
        #
        #     today = datetime.datetime.strptime(today, '%Y-%m-%d')
        #     last_day = datetime.datetime.strptime(last_day, '%Y-%m-%d')
        #
        #
        #     try:
        #         #print('daem stock', stock)
        #         #драить код
        #         AddStock.actualize_stock_data(stock, last_day)
        #         stock_data = Stock.objects.get(id=stock.id).stock_data
        #         json_stock_data = json.loads(stock_data)
        #         last_day = max(json_stock_data['TRADEINFO'].keys())
        #         #print('asd', stock_data)
        #     except Exception:
        #        raise Exception('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        # #print('last', last_day)

        current_quantity = self.get_current_quantity(self.request, stock.id)

        #print(stock_data_json['TRADEINFO'])
        #print('last_day_str', last_day_str)
        #print(stock_data_json['TRADEINFO'].get(last_day_str))

        last_day_price = stock_data_json["TRADEINFO"][last_day_str].get('CLOSE')

        #print(last_day_price, 'LAST DAY PRICE')

        if not last_day_price:
            last_day_price = stock_data_json["TRADEINFO"][last_day_str].get('LAST')

        qurrent_price = current_quantity * last_day_price
        #print(qurrent_price)
        return qurrent_price
        #ПРОВЕРИТЬ ЧТО ПОСЛЕДНЯЯ ДАТА АКТУАЛЬНА

    @staticmethod
    def get_percent_result(purchase_price, current_price):
        if current_price == 0 and purchase_price == 0:
            return '+ 0.00'
        if current_price > 0 and purchase_price > 0:
            result = Decimal(current_price) / Decimal(purchase_price)
            
            return f'- {"{:.2%}".format((1 - result))}' if result < 1 else f'+ {"{:.2%}".format((result - 1))}'
        #return '0'
        raise ValueError('current_price and purchase_price must be > 0')

class StockData(object):
    MAX_HOLIDAY_GAP = 10 #max holidays continuous sequence in russian prod calendar
    def __init__(self, stock=None):
        self.stock = stock
        self.today = datetime.datetime.today()
        if self.stock:
            self.stock_data = json.loads(stock.stock_data)

    def get_data_last_date(self, trade_date_index=-1):
        """
        :return: returns the last date for the stock that is written in the DB
        """
        if self.stock_data:

            dates = list(self.stock_data['TRADEINFO'].keys())
            dates.sort()

            date_str = dates[trade_date_index]

            date_dt = datetime.datetime.strptime(
                date_str, '%Y-%m-%d')

            #print(self.stock_data)
            #print('LAST DAY:', date_str)
            if self.stock_data['TRADEINFO'][date_str].get("CLOSE"):
                status = 'CLOSED'
                update_time = None
            elif self.stock_data['TRADEINFO'][date_str].get("LAST"):
                status = 'LAST'
                update_time = self.stock_data['TRADEINFO'][date_str].get("UPDATE_TIME")
            #print('STATUS:', status)
            return date_dt, status, update_time
    def actualize_stock_data(self):

        today_status = self.get_and_update_date_status(datetime.datetime.strftime(self.today, '%Y-%m-%d')).date_status
        #print('TODAY STATUS:', today_status.date, today_status.date_status)

        if self.stock_data:
            last_date_dt, status, update_time = self.get_data_last_date()

            if status == 'LAST' and today_status == 'Nonworking':
                last_date_dt, status, update_time = self.get_data_last_date(trade_date_index=-2)


            last_date_str = datetime.datetime.strftime(last_date_dt, '%Y-%m-%d')

            actual_date_gap = (self.today - last_date_dt).days

            if actual_date_gap == 0 or (actual_date_gap == 0 and status == 'CLOSED'):
                if today_status == 'Working':
                    return self.update_real_time_price()
                raise Exception('SOMETHING GONE WRONG WITH DATES')




            elif actual_date_gap >= self.MAX_HOLIDAY_GAP:
                """
                The last day in stock data is different from today more than max holidays
                continuous sequence in russian prod calendar -
                must be updated anyway. Updating from the last date in DB.
                """
                self.update_stock_data(last_date_str)

                if today_status == 'Working':
                    self.update_real_time_price()
                return self.stock

            else:
                """
                There is a possibility that all the days in the gap are holidays -
                so need to find the last working day. Updating from the last date in DB.
                """
                #actual_last_date = self.today
                for gap in range(0, actual_date_gap):
                    #print('gap', gap, 'for', self.stock.ticker, 'last_day', last_day, 'actual date gap', actual_date_gap)
                    date_str = datetime.datetime.strftime((self.today - datetime.timedelta(gap)), '%Y-%m-%d')
                    print('datestr',date_str)
                    try:
                        prod_date = self.get_and_update_date_status(date_str)
                        #print(prod_date,'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                    except ConnectionError:
                        continue

                    if prod_date.date_status == 'Working':
                        print('last_date', last_date_str)
                        print('tod stat', today_status)
                        self.update_stock_data(last_date_str)
                        if today_status == 'Working':
                            self.update_real_time_price()
                        return self.stock
                return self.stock

    @staticmethod
    def get_and_update_date_status(date: str):
        try:
            prod_date = ProdCalendar.objects.get(date=date)
            #print('prod_date', prod_date.date, prod_date.date_status)
        except ProdCalendar.DoesNotExist:
            #print("PRODCALENDAR DATE DOESNT EXIST")

            try:
                date_status = get_date_status(date)
            except ConnectionError:
                raise ConnectionError('ne smog poluchit date status from internet')

            prod_date = ProdCalendar()
            prod_date.date = date
            prod_date.date_status = date_status
            prod_date.save()

        return prod_date

    def update_stock_data(self, start_date=None):
        """
        :param start_date: should be set if stock exist and has some stock data with last stock data date
        :return: created or updates stock data using MOEX API from start_date
        or from first historic date if start_date is None - returns updated stock object
        """
        stock_board_history = get_stock_board_history(self.stock.ticker, start_date)
        stock_board_data_json = json.loads(make_json_trade_info_dict(stock_board_history))



        if self.stock_data:
            """
            if stock data already exist and should be updated
            """
            current_stock_data_json = self.stock_data
            #print('start_date', start_date)
            #print('CURRENT', current_stock_data_json['TRADEINFO'][start_date])
            #print(start_date == datetime.datetime.today())
            current_stock_data_json['TRADEINFO'].update(stock_board_data_json['TRADEINFO'])

            stock_data = json.dumps(current_stock_data_json)
            self.stock.stock_data = stock_data
            self.stock.save()

            return self.stock

        else:
            """
            if stock data does not exist and should be created first time
            """
            stock_data = json.dumps(stock_board_data_json)
            self.stock.stock_data = stock_data
            self.stock.save()

            return self.stock

    def update_real_time_price(self):
        #print(f'START UPDATE RTP for {self.stock.name}')

        # In minutes
        STANDARD_MOEX_LAG = 16
        UPDATE_TIME_MINUTES = 60 - STANDARD_MOEX_LAG

        EVENING_CUT_OFF = datetime.datetime.strftime(self.today, '%Y-%m-%d 18:30:00')

        if self.stock_data:
            """
            if stock data already exist and should be updated
            """


            #NE DODELANO
            last_day, _, update_time = self.get_data_last_date()

            if update_time:

                # IF STOCK IS NOT ON EVENING SESSION AND UPDATE TIME LATER THAN 18:30:00 TODAY => NO NEED TO UPDATE
                if self.stock.eveningsession == '0' and update_time > EVENING_CUT_OFF:
                    return self.stock

                time_gap = self.get_time_gap(update_time)
                #print('time_gap', time_gap, self.stock)
                if time_gap <= UPDATE_TIME_MINUTES:
                    return self.stock

            last_price, new_update_time = get_stock_current_price(self.stock.ticker)
            last_day_data = json.loads(make_json_last_price_dict(last_price, new_update_time))
            #print(self.stock, last_day_data)
            current_stock_data_json = self.stock_data

            current_stock_data_json['TRADEINFO'].update(last_day_data['TRADEINFO'])

            stock_data = json.dumps(current_stock_data_json)
            self.stock.stock_data = stock_data
            self.stock.save()

            return self.stock

    @staticmethod
    def get_time_gap(update_time: str):

        TIME_ZONE_DELTA = 3

        offset = datetime.timezone(datetime.timedelta(hours=TIME_ZONE_DELTA))
        current_time = datetime.datetime.now(offset)
        current_time_dt = datetime.datetime.strptime(
            datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S'),
            '%Y-%m-%d %H:%M:%S')

        update_time_dt = datetime.datetime.strptime(
            update_time, '%Y-%m-%d %H:%M:%S')

        duration = current_time_dt - update_time_dt
        duration_in_s = duration.total_seconds()
        minutes = divmod(duration_in_s, 60)[0]

        return minutes



class AddStock(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = 'login'
    form_class = StockForm
    template_name = 'base_create_and_update.html'
    success_url = reverse_lazy('stocks')
    success_message = _("Stock has been successfully added!")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Add new stock")
        context['button_text'] = _("Add")
        return context

    def post(self, request, *args, **kwargs):
        form = StockForm(request.POST)

        if form.is_valid():
            #validated_ticker = validate_ticker(form.cleaned_data.get('ticker'))
            stock_description = get_stock_description(form.cleaned_data.get('ticker'))
            if stock_description:

                ticker = stock_description.get('SECID')
                name = stock_description.get('SHORTNAME')
                isin = stock_description.get('ISIN')
                currency = 'RUR' if stock_description.get('FACEUNIT') == 'SUR' else stock_description.get('FACEUNIT')
                latname = stock_description.get('LATNAME')
                isqualifiedinvestors = stock_description.get('ISQUALIFIEDINVESTORS')
                issuedate = stock_description.get('ISSUEDATE')
                morningsession = stock_description.get('MORNINGSESSION', '0')
                eveningsession = stock_description.get('EVENINGSESSION', '0')
                typename = stock_description.get('TYPENAME')
                group = stock_description.get('GROUP')
                type = stock_description.get('TYPE')
                groupname = stock_description.get('GROUPNAME')

                check_list = [ticker, name, isin, currency, latname, isqualifiedinvestors, issuedate, morningsession, eveningsession, typename, group, type, groupname]

                if None in check_list:
                    print("SOMETHING HAVE NOT BEEN LOADED - GOT NONE")

                #Ищем инфу о ценах акции за весь период чтобы записать в JSONField
                stock_board_history = get_stock_board_history(ticker)
                json_stock_board_data = make_json_trade_info_dict(stock_board_history)

                obj = Stock()
                obj.ticker = ticker
                obj.name = name
                obj.isin = isin
                obj.currency = currency
                obj.latname = latname
                obj.isqualifiedinvestors = isqualifiedinvestors
                obj.issuedate = issuedate
                obj.morningsession = morningsession
                obj.eveningsession = eveningsession
                obj.typename = typename
                obj.group = group
                obj.type = type
                obj.groupname = groupname

                #obj.save()
                #StockData(obj).update_stock_data()

                obj.stock_data = json_stock_board_data #str
                obj.save()


                # add dividend for stock
            #return super().post(request, *args, **kwargs)


                messages.success(request, self.success_message)
                return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    @staticmethod
    def actualize_stock_data(stock, start_date=None):

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        last_day = datetime.datetime.strptime(start_date, '%Y-%m-%d')



        json_current_stock_data = json.loads(stock.stock_data)

        stock_board_history = get_stock_board_history(stock.ticker, start_date)
        json_stock_board_data = json.loads(make_json_trade_info_dict(stock_board_history))

        #print('======')
        #print(json_stock_data['TRADEINFO'])
        #print('#======#')
        #print(json_stock_board_data, type(json_stock_board_data))
        #print(json_stock_board_data['TRADEINFO'])
        #print('##======##')

        json_current_stock_data['TRADEINFO'].update(json_stock_board_data['TRADEINFO'])

        #print('##########')
        #print(json_stock_data)
        #print('###########')
        #print('1', json_stock_data.keys())
        #print('2', json_stock_data['TRADEINFO'].keys())

        stock_data = json.dumps(json_current_stock_data)
        stock.stock_data = stock_data
        stock.save()

        return stock




    def form_valid(self, form):
    #
        form.instance.creator = self.request.user
    #
    #     # print('aaaaaaa', form.cleaned_data['ticker'])
    #     # obj = Stock()
    #     # obj.name = validate_ticker(form.cleaned_data['ticker'])
    #     # obj.save
    #
    #     # data = form.cleaned_data
    #     # print(data)
    #     # print(validate_ticker(data['ticker']))
        return super().form_valid(form)


class DeleteStock(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = 'login'
    model = Stock
    template_name = "base_delete.html"
    success_url = reverse_lazy('stocks')
    success_message = _("Stock has been successfully deleted!")

    # def dispatch(self, request, *args, **kwargs):
    #     if self.get_object().creator.id == request.user.id \
    #             or request.user.is_staff:
    #         return super().dispatch(request, *args, **kwargs)
    #     messages.error(request, _('You can delete only your labels'))
    #     return redirect('labels')

    def post(self, request, *args, **kwargs):

        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _(
                'Label that is given to the task can not be deleted'))
            return redirect('labels')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Delete stock")
        context['button_text'] = _("Delete")
        context['delete_object'] = str(
            Stock.objects.get(id=self.get_object().id))
        return context