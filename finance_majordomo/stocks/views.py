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

from finance_majordomo.stocks.forms import StockForm
from finance_majordomo.stocks.models import Stock, ProdCalendar
from finance_majordomo.transactions.models import Transaction

from django.utils.translation import gettext_lazy as _

from common.utils.stocks import validate_ticker, get_stock_board_history, make_json_trade_info_dict
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
        print(self.request.user.id)
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.request.user.username + " " + _("stock list")

        user_stock_data = self.get_user_stock_data()

        #users_stocks = Stock.objects.filter(usersstocks__user_id=self.request.user.id)
        #users_stocks = [(obj, self.get_current_quantity(self.request, obj.id), self.get_purchace_price(self.request, obj.id), self.get_current_price(obj.id)) for obj in users_stocks]
        #print(users_stocks)
        # print([el for el in users_stocks])
        # self.get_current_quantity(1)
        context['stock_list'] = user_stock_data
        return context

    def get_user_stock_data(self):
        request = self.request
        user_stocks = Stock.objects.filter(usersstocks__user_id=request.user.id)

        user_stock_data = []
        for stock in user_stocks:
            purchase_price = self.get_purchace_price(request, stock.id)
            current_quantity = self.get_current_quantity(request, stock.id)
            current_price = self.get_current_price(stock)
            percent_result = self.get_percent_result(purchase_price, current_price)

            user_stock_data.append({'stock': stock,
                                    'purchase_price': purchase_price,
                                    'current_quantity': current_quantity,
                                    'current_price': current_price,
                                    'percent_result': percent_result
                                    })

        return user_stock_data

    @staticmethod
    def get_current_quantity(request, stock_id):
        users_transacions = Transaction.objects.filter(user=User.objects.get(id=request.user.id))
        users_specific_asset_transacions = users_transacions.filter(ticker=Stock.objects.get(id=stock_id))
        result = 0
        for transaction in users_specific_asset_transacions:
            if transaction.transaction_type == "BUY":
                result += transaction.quantity
            elif transaction.transaction_type == "SELL":
                result -= transaction.quantity
            else:
                raise Exception('not buy or sell found')
        return result

    @staticmethod
    def get_purchace_price(request, stock_id):
        # С учетом метода FIFO
        users_transacions = Transaction.objects.filter(user=User.objects.get(id=request.user.id))
        users_specific_asset_transacions = sorted(users_transacions.filter(ticker=Stock.objects.get(id=stock_id)), key=lambda x: x.date)
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
            print('total_sold', total_sold)
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
        stock_data = Stock.objects.get(id=stock.id).stock_data
        json_stock_data = json.loads(stock_data)

        last_day = max(json_stock_data['TRADEINFO'].keys())
        today = datetime.datetime.today().strftime('%Y-%m-%d')

        if last_day < today:

            today = datetime.datetime.strptime(today, '%Y-%m-%d')
            last_day = datetime.datetime.strptime(last_day, '%Y-%m-%d')


            try:
                #print('daem stock', stock)
                #драить код
                AddStock.actualize_stock_data(stock, last_day)
                stock_data = Stock.objects.get(id=stock.id).stock_data
                json_stock_data = json.loads(stock_data)
                last_day = max(json_stock_data['TRADEINFO'].keys())
                #print('asd', stock_data)
            except Exception:
               raise Exception('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        #print('last', last_day)

        current_quantity = self.get_current_quantity(self.request, stock.id)

        last_day_price = json_stock_data["TRADEINFO"][last_day]['CLOSE']
        qurrent_price = current_quantity * last_day_price
        #print(qurrent_price)
        return qurrent_price
        #ПРОВЕРИТЬ ЧТО ПОСЛЕДНЯЯ ДАТА АКТУАЛЬНА

    @staticmethod
    def get_percent_result(purchase_price, current_price):
        #print(purchase_price, current_price, 'AAAAAAAAAAAAAAAAAAA')
        if current_price > 0 and purchase_price > 0:
            result = Decimal(current_price) / purchase_price
            return f'- {"{:.2%}".format((1 - result))}' if result < 1 else f'+ {"{:.2%}".format((result - 1))}'
        return None


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
            validated_ticker = validate_ticker(form.cleaned_data.get('ticker'))
            if validated_ticker:

                #Ищем инфу о ценах акции за весь период чтобы записать в JSONField
                stock_board_history = get_stock_board_history(validated_ticker['ticker'])
                json_stock_board_data = make_json_trade_info_dict(stock_board_history)

                obj = Stock()
                obj.ticker = validated_ticker['ticker']
                obj.name = validated_ticker['shortname']
                obj.stock_data = json_stock_board_data #str
                obj.save()
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