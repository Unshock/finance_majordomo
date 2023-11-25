from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from finance_majordomo.stocks.forms.asset_forms import StockForm
from finance_majordomo.stocks.models.asset import Stock, Asset
from finance_majordomo.stocks.models.transaction_models import Transaction

from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.services.asset_services.asset_model_management_services import \
    create_asset_obj_from_description
from finance_majordomo.stocks.services.asset_services.asset_view_services import \
    PortfolioAssetsViewContextService, portfolio_asset_view_context_service
from finance_majordomo.stocks.services.asset_services.user_assets_services import get_current_portfolio


class Stocks(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Asset
    template_name = 'stocks/stock_list.html'
    context_object_name = 'stock'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Stock list")
        context['stock_list'] = Asset.objects.all()
        return context


class PortfolioAssets(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Asset
    template_name = 'stocks/user_stock_list.html'
    context_object_name = 'stock'

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)

        portfolio_assets_data = portfolio_asset_view_context_service(
            self.request.user.get_current_portfolio())

        asset_list = portfolio_assets_data.get('asset_list')
        total_results = portfolio_assets_data.get('total_results')

        context['page_title'] = self.request.user.username + " " + _(
            "stock list")
        context['fields_to_display'] = self.request.user.usersettings
        context['current_portfolio'] = get_current_portfolio(self.request.user)
        context['asset_list'] = asset_list
        context['total_results'] = total_results

        return context

    # def get_total_purchase_price(self, stock_list):
    #     total_purchase_price = sum(
    #         [stock['purchase_price'] for stock in stock_list]
    #     )
    #     return "{:.2f}".format(total_purchase_price)
    # 
    # def get_total_current_price(self, stock_list):
    #     total_current_price = sum(
    #         [float(stock['current_price']) for stock in stock_list]
    #     )
    #     return "{:.2f}".format(total_current_price)
    # 
    # def get_user_stock_data(self):
    #     request = self.request
    # 
    #     GetAssetsOfUser.execute({'user': self.request.user})
    # 
    #     user_assets = Asset.objects.filter(
    #         id__in=request.user.assetsofuser_set.values_list('asset'))
    #     
    #     print('QQQQQQQQQQQQQQQQQQQQQQ', user_assets)
    #     
    #     if user_assets:
    #         print(user_assets)
    # 
    #         current_portfolio = get_current_portfolio(request.user)
    #         
    #         print('333333333333333333333333333333333333333333333333', current_portfolio.get_assets_of_portfolio())
    #         
    #         a = Asset.objects.filter(id__in=current_portfolio.assetofportfolio_set.values_list('asset'))
    #         
    #         
    #         print(a, '555555555555555555555555555555555555555555555555555555555555555555555555555')
    #         for i in a:
    #             print(i)
    # 
    #         # print('==========$=====================')
    #         # print(request.user.stocksofuser_set.values_list('stock'))
    #         # print('==========$=====================')
    #         # 
    #         print(current_portfolio, current_portfolio.user)
    #         users_assets = Asset.objects.filter(
    #            id__in=current_portfolio.assetofportfolio_set.values_list('asset'))
    #         #users_assets = current_portfolio.asset.all()
    # 
    #         print('===============================')
    #         print(users_assets)
    #         assets_portfolio = current_portfolio.assetofportfolio_set.all()
    # 
    #         print('ASSETS OF PORTFOILO', assets_portfolio)
    #         print('ASSETS OF PORTFOILO',
    #               assets_portfolio[0].get_purchase_price())
    #         print('===============================')
    # 
    #         #print(request.user.stocksofuser_set.values_list('stock'))
    # 
    #         total_purchase_price = Decimal('0')
    #         total_current_price = Decimal('0')
    #         total_divs = Decimal('0')
    # 
    #         total_purchase_price_usd = Decimal('0')
    #         total_current_price_usd = Decimal('0')
    #         total_divs_usd = Decimal('0')
    # 
    #         user_stock_data = {'total_results': {},
    #                            'stock_list': []
    #                            }
    #         print('user asseets', user_assets)
    # 
    #         update_currency_rates()
    #         update_usd()
    # 
    #         for asset in user_assets:
    # 
    #             # update_history_data(stock)
    #             # update_today_data(stock)
    #             update_historical_data(asset)
    # 
    #             current_quantity = get_asset_quantity_for_portfolio(current_portfolio.id, asset.id)
    # 
    #             if current_quantity == 0:
    #                 continue
    # 
    #             avg_purchase_price = get_average_purchase_price(
    #                 current_portfolio.id, asset.id)
    #             print('7654321', avg_purchase_price)
    # 
    #             purchase_price = get_purchase_price(
    #                 current_portfolio.id, asset.id)
    #             purchase_price_usd = get_purchase_price(
    #                 current_portfolio.id, asset.id, currency='usd')
    # 
    #             total_purchase_price += purchase_price
    #             total_purchase_price_usd += purchase_price_usd
    # 
    #             current_price = self.get_current_price(asset)
    #             current_price_usd = self.get_current_price(asset, currency='usd')
    # 
    #             total_current_price += current_price
    #             total_current_price_usd += current_price_usd
    # 
    #             percent_result = self.get_percent_result(
    #                 purchase_price, current_price)
    # 
    #             money_result_without_divs = moneyfmt(
    #                 get_money_result(current_price, purchase_price), sep=' ')
    # 
    #             dividends_received = \
    #                 get_accrual_result_of_portfolio(current_portfolio)
    #             total_divs += dividends_received
    # 
    #             dividends_received_usd = get_accrual_result_of_portfolio(
    #                 current_portfolio, currency='usd')
    # 
    #             total_divs_usd += dividends_received_usd
    # 
    #             money_result_with_divs = moneyfmt(
    #                 get_money_result(
    #                     current_price + dividends_received,
    #                     purchase_price),
    #                 sep=' ')
    # 
    #             rate_of_return = self.get_percent_result(
    #                 purchase_price, current_price + dividends_received)
    # 
    #             user_stock_data['stock_list'].append(
    #                 {'id': asset.id,
    #                  'ticker': asset.secid,
    #                  'name': asset.name,
    #                  'currency': asset.currency,
    #                  'quantity': moneyfmt(
    #                      Decimal(current_quantity), sep=' ', places=0),
    #                  'purchase_price': moneyfmt(purchase_price, sep=' '),
    #                  'avg_purchase_price': moneyfmt(avg_purchase_price, sep=' ', curr='$'),
    #                  'current_price': moneyfmt(current_price, sep=' '),
    #                  'percent_result': percent_result,
    #                  'dividends_received': moneyfmt(dividends_received, sep=' '),
    #                  'money_result_without_divs': money_result_without_divs,
    #                  'money_result_with_divs': money_result_with_divs,
    #                  'rate_of_return': rate_of_return,
    #                  })
    #             print(type(moneyfmt(
    #                      Decimal(current_quantity), sep=' ', places=0)))
    # 
    #         total_financial_result_no_divs = total_current_price - total_purchase_price
    #         total_financial_result_with_divs = total_current_price + total_divs - total_purchase_price
    #         
    #         print(total_current_price_usd, total_divs_usd, total_purchase_price_usd)
    #         total_financial_result_with_divs_usd = total_current_price_usd + total_divs_usd - total_purchase_price_usd
    #         
    #         total_percent_result = self.get_percent_result(
    #             total_purchase_price, total_current_price)
    #         total_rate_of_return = self.get_percent_result(
    #             total_purchase_price, (total_financial_result_with_divs + total_purchase_price))
    # 
    #         user_stock_data['total_results'] = {
    #             'total_purchase_price': moneyfmt(total_purchase_price, sep=' '),
    #             'total_current_price': moneyfmt(total_current_price, sep=' '),
    #             'total_percent_result': total_percent_result,
    #             'total_divs': set_money_fmt(total_divs),
    #             'total_financial_result_no_divs': set_money_fmt(
    #                 total_financial_result_no_divs),
    #             'total_financial_result_with_divs': moneyfmt(
    #                 total_financial_result_with_divs, sep=' '),
    #             'total_rate_of_return': total_rate_of_return,
    # 
    #             'total_current_price_usd': moneyfmt(
    #                 total_current_price_usd, sep=' '),
    #             'total_financial_result_with_divs_usd': moneyfmt(
    #                 total_financial_result_with_divs_usd, sep=' ')
    #         }
    # 
    #         return user_stock_data
    #     return dict()
    # 
    # @staticmethod
    # def get_currency_rate(currency: str = None):
    #     if currency and currency.lower() == 'usd':
    #         currency_rate = CurrencyRate.objects.last().price_usd
    #     else:
    #         currency_rate = Decimal('1')
    # 
    #     return currency_rate
    # 
    # def get_current_price(self, asset, currency=None):
    #     currency_rate = self.get_currency_rate(currency)
    # 
    #     portfolio = get_current_portfolio(self.request.user)
    # 
    #     last_date_price = AssetsHistoricalData.objects.filter(
    #         asset=asset).order_by('-tradedate')[0].legalcloseprice
    # 
    #     current_quantity = get_asset_quantity_for_portfolio(
    #         portfolio.id, asset.id)
    # 
    #     current_price = current_quantity * last_date_price / currency_rate
    # 
    #     if asset.group == 'stock_bonds':
    #         bond = asset.get_related_object()
    #         current_price = current_price * bond.face_value / 100
    # 
    #     return Decimal(current_price)
    # 
    # def get_current_price_alt(self, stock):
    #     last_date_price = AssetsHistoricalData.objects.filter(
    #         asset=stock).order_by('-tradedate')[0].legalcloseprice
    # 
    #     current_quantity = get_quantity(self.request, stock)
    # 
    #     current_price = current_quantity * last_date_price
    #     return Decimal(current_price)
    # 
    # 
    # def get_current_price_usd(self, stock):
    #     last_date_price = AssetsHistoricalData.objects.filter(
    #         asset=stock).order_by('-tradedate')[0].legalcloseprice
    # 
    #     current_quantity = get_quantity(self.request, stock)
    #     current_usd_rate = CurrencyRate.objects.last().price_usd
    # 
    #     current_price = current_quantity * last_date_price / current_usd_rate
    #     return Decimal(current_price)

    # не исп get_current_price
    # def get_current_price(self, stock):
    # 
    #     stock_obj = StockData(stock)
    #     stock = stock_obj.actualize_stock_data()
    #     last_date_dt, status, update_time = stock_obj.get_data_last_date()
    #     #print('last_date_dt', last_date_dt)
    #     last_day_str = datetime.datetime.strftime(last_date_dt, '%Y-%m-%d')
    #     #stock_data = stock.stock_data
    # 
    #     #stock_data = Stock.objects.get(id=stock.id).stock_data
    #     stock_data_json = json.loads(stock.stock_data)
    # 
    #     #закомментирован неактуальный код
    #     #last_day = max(json_stock_data['TRADEINFO'].keys())
    #     #today = datetime.datetime.today().strftime('%Y-%m-%d')
    # 
    #     # if last_day < today:
    #     #
    #     #     actualizator = StockData(stock)
    #     #
    #     #     today = datetime.datetime.strptime(today, '%Y-%m-%d')
    #     #     last_day = datetime.datetime.strptime(last_day, '%Y-%m-%d')
    #     #
    #     #
    #     #     try:
    #     #         #print('daem stock', stock)
    #     #         #драить код
    #     #         AddStock.actualize_stock_data(stock, last_day)
    #     #         stock_data = Stock.objects.get(id=stock.id).stock_data
    #     #         json_stock_data = json.loads(stock_data)
    #     #         last_day = max(json_stock_data['TRADEINFO'].keys())
    #     #         #print('asd', stock_data)
    #     #     except Exception:
    #     #        raisreturn Decimal(qurrent_price)e Exception('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    #     # #print('last', last_day)
    # 
    #     current_quantity = get_quantity(self.request, stock)
    # 
    #     #print(stock_data_json['TRADEINFO'])
    #     #print('last_day_str', last_day_str)
    #     #print(stock_data_json['TRADEINFO'].get(last_day_str))
    # 
    #     last_day_price = stock_data_json["TRADEINFO"][last_day_str].get('CLOSE')
    # 
    #     #print(last_day_price, 'LAST DAY PRICE')
    # 
    #     if not last_day_price:
    #         last_day_price = stock_data_json["TRADEINFO"][last_day_str].get('LAST')
    # 
    #     current_price = current_quantity * last_day_price
    # 
    #     return Decimal(current_price)
    #     #ПРОВЕРИТЬ ЧТО ПОСЛЕДНЯЯ ДАТА АКТУАЛЬНА

    # @staticmethod
    # def get_percent_result(purchase_price, current_price):
    #     if current_price == 0 and purchase_price == 0:
    #         return '+ 0.00'
    #     if current_price > 0 and purchase_price > 0:
    #         result = (Decimal(current_price) - Decimal(
    #             purchase_price)) / Decimal(purchase_price)
    # 
    #         print(len(str(result)))
    #         return f'- {"{:.2%}".format(-result)}' if result < 0 else f'+ {"{:.2%}".format(result)}'
    #     #return '0'
    #     raise ValueError('current_price and purchase_price must be > 0')


# class StockData(object):
#     MAX_HOLIDAY_GAP = 10 #max holidays continuous sequence in russian prod calendar
#     def __init__(self, stock=None):
#         self.stock = stock
#         self.today = datetime.datetime.today()
#         if self.stock:
#             self.stock_data = json.loads(stock.stock_data)
# 
#     def get_data_last_date(self, trade_date_index=-1) -> tuple:
#         """
#         :return: returns the last date for the stock that is written in the DB
#         """
#         if self.stock_data:
# 
#             dates = list(self.stock_data['TRADEINFO'].keys())
#             dates.sort()
# 
#             date_str = dates[trade_date_index]
# 
#             date_dt = datetime.datetime.strptime(
#                 date_str, '%Y-%m-%d')
# 
#             #print(self.stock_data)
#             #print('LAST DAY:', date_str)
#             if self.stock_data['TRADEINFO'][date_str].get("CLOSE"):
#                 status = 'CLOSED'
#                 update_time = None
#             elif self.stock_data['TRADEINFO'][date_str].get("LAST"):
#                 status = 'LAST'
#                 update_time = self.stock_data['TRADEINFO'][date_str].get("UPDATE_TIME")
#             #print('STATUS:', status)
#             return date_dt, status, update_time
# 
#     def actualize_stock_data(self):
# 
#         today_status = self.get_and_update_date_status(
#             datetime.datetime.strftime(self.today, '%Y-%m-%d')).date_status
#         #print('TODAY STATUS:', today_status.date, today_status.date_status)
# 
#         if self.stock_data:
#             last_date_dt, status, update_time = self.get_data_last_date()
# 
#             if status == 'LAST' and today_status == 'Nonworking':
#                 last_date_dt, status, update_time = self.get_data_last_date(
#                     trade_date_index=-2)
# 
# 
#             last_date_str = datetime.datetime.strftime(last_date_dt, '%Y-%m-%d')
# 
#             actual_date_gap = (self.today - last_date_dt).days
# 
#             if actual_date_gap == 0 or (actual_date_gap == 0 and status == 'CLOSED'):
#                 if today_status == 'Working':
#                     return self.update_real_time_price()
#                 raise Exception('SOMETHING GONE WRONG WITH DATES')
# 
# 
# 
# 
#             elif actual_date_gap >= self.MAX_HOLIDAY_GAP:
#                 """
#                 The last day in stock data is different from today more than max holidays
#                 continuous sequence in russian prod calendar -
#                 must be updated anyway. Updating from the last date in DB.
#                 """
#                 self.update_stock_data(last_date_str)
# 
#                 if today_status == 'Working':
#                     self.update_real_time_price()
#                 return self.stock
# 
#             else:
#                 """
#                 There is a possibility that all the days in the gap are holidays -
#                 so need to find the last working day. Updating from the last date in DB.
#                 """user_stock_data
#                 #actual_last_date = self.today
#                 for gap in range(0, actual_date_gap):
#                     #print('gap', gap, 'for', self.stock.ticker, 'last_day', last_day, 'actual date gap', actual_date_gap)
#                     date_str = datetime.datetime.strftime((self.today - datetime.timedelta(gap)), '%Y-%m-%d')
#                     #print('datestr',date_str)
#                     try:
#                         prod_date = self.get_and_update_date_status(date_str)
#                         #print(prod_date,'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
#                     except ConnectionError:
#                         continue
# 
#                     if prod_date.date_status == 'Working':
#                         print('last_date', last_date_str)
#                         print('tod stat', today_status)
#                         self.update_stock_data(last_date_str)
#                         if today_status == 'Working':
#                             self.update_real_time_price()
#                         return self.stock
#                 return self.stock
# 
#     @staticmethod
#     def get_and_update_date_status(date: str):
#         try:
#             prod_date = ProdCalendar.objects.get(date=date)
#             #print('prod_date', prod_date.date, prod_date.date_status)
#         except ProdCalendar.DoesNotExist:
#             #print("PRODCALENDAR DATE DOESNT EXIST")
# 
#             try:
#                 date_status = get_date_status(date)
#             except ConnectionError:
#                 raise ConnectionError('ne smog poluchit date status from internet')
# 
#             prod_date = ProdCalendar()
#             prod_date.date = date
#             prod_date.date_status = date_status
#             prod_date.save()
# 
#         return prod_date
# 
#     def update_stock_data(self, start_date=None):
#         """
#         :param start_date: should be set if stock exist and has some stock data with last stock data date
#         :return: created or updates stock data using MOEX API from start_date
#         or from first historic date if start_date is None - returns updated stock object
#         """
#         stock_board_history = get_stock_board_history(self.stock.ticker, start_date)
#         stock_board_data_json = json.loads(make_json_trade_info_dict(stock_board_history))
# 
# 
# 
#         if self.stock_data:
#             """
#             if stock data already exist and should be updated
#             """
#             current_stock_data_json = self.stock_data
#             #print('start_date', start_date)
#             #print('CURRENT', current_stock_data_json['TRADEINFO'][start_date])
#             #print(start_date == datetime.datetime.today())
#             current_stock_data_json['TRADEINFO'].update(stock_board_data_json['TRADEINFO'])
# 
#             stock_data = json.dumps(current_stock_data_json)
#             self.stock.stock_data = stock_data
#             self.stock.save()
# 
#             return self.stock
# 
#         else:
#             """
#             if stock data does not exist and should be created first time
#             """
#             stock_data = json.dumps(stock_board_data_json)
#             self.stock.stock_data = stock_data
#             self.stock.save()
# 
#             return self.stock
# 
#     def update_real_time_price(self):
#         #print(f'START UPDATE RTP for {self.stock.name}')
# 
#         # In minutes
#         STANDARD_MOEX_LAG = 16
#         UPDATE_TIME_MINUTES = 60 - STANDARD_MOEX_LAG
# 
#         EVENING_CUT_OFF = datetime.datetime.strftime(self.today, '%Y-%m-%d 18:30:00')
# 
#         if self.stock_data:
#             """
#             if stock data already exist and should be updated
#             """
# 
# 
#             #NE DODELANO
#             last_day, _, update_time = self.get_data_last_date()
# 
#             if update_time:
# 
#                 # IF STOCK IS NOT ON EVENING SESSION AND UPDATE TIME LATER THAN 18:30:00 TODAY => NO NEED TO UPDATE
#                 if not self.stock.eveningsession and update_time > EVENING_CUT_OFF:
#                     return self.stock
# 
#                 time_gap = self.get_time_gap(update_time)
#                 #print('time_gap', time_gap, self.stock)
#                 if time_gap <= UPDATE_TIME_MINUTES:
#                     return self.stock
# 
#             last_price, new_update_time = get_stock_current_price(self.stock.ticker)
#             last_day_data = json.loads(make_json_last_price_dict(last_price, new_update_time))
#             #print(self.stock, last_day_data)
#             current_stock_data_json = self.stock_data
# 
#             current_stock_data_json['TRADEINFO'].update(last_day_data['TRADEINFO'])
# 
#             stock_data = json.dumps(current_stock_data_json)
#             self.stock.stock_data = stock_data
#             self.stock.save()
# 
#             return self.stock
# 
#     @staticmethod
#     def get_time_gap(update_time: str):
# 
#         TIME_ZONE_DELTA = 3
# 
#         offset = datetime.timezone(datetime.timedelta(hours=TIME_ZONE_DELTA))
#         current_time = datetime.datetime.now(offset)
#         current_time_dt = datetime.datetime.strptime(
#             datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S'),
#             '%Y-%m-%d %H:%M:%S')
# 
#         update_time_dt = datetime.datetime.strptime(
#             update_time, '%Y-%m-%d %H:%M:%S')
# 
#         duration = current_time_dt - update_time_dt
#         duration_in_s = duration.total_seconds()
#         minutes = divmod(duration_in_s, 60)[0]
# 
#         return minutes


class AddStock(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = 'login'
    form_class = StockForm
    template_name = 'base_create_and_update.html'

    success_url = reverse_lazy('stocks:stocks')
    success_message = _("Stock has been successfully added!")

    self_url = reverse_lazy('add_stock')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Add new stock")
        context['button_text'] = _("Add")
        return context

    def post(self, request, *args, **kwargs):

        form = StockForm(request.POST)

        if form.is_valid():

            stock_description = form.cleaned_data.get('stock_description')
            create_asset_obj_from_description(stock_description)

            messages.success(request, self.success_message)
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


    # # не используется?
    # @staticmethod
    # def actualize_stock_data(stock, start_date=None):
    # 
    #     today = datetime.datetime.today().strftime('%Y-%m-%d')
    #     today = datetime.datetime.strptime(today, '%Y-%m-%d')
    #     last_day = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    # 
    #     json_current_stock_data = json.loads(stock.stock_data)
    # 
    #     stock_board_history = get_asset_board_history(
    #         stock.secid, start_date)
    #     json_stock_board_data = json.loads(
    #         make_json_trade_info_dict(stock_board_history))
    # 
    #     #print('======')
    #     #print(json_stock_data['TRADEINFO'])
    #     #print('#======#')
    #     #print(json_stock_board_data, type(json_stock_board_data))
    #     #print(json_stock_board_data['TRADEINFO'])
    #     #print('##======##')
    # 
    #     json_current_stock_data['TRADEINFO'].update(
    #         json_stock_board_data['TRADEINFO'])
    # 
    #     #print('##########')
    #     #print(json_stock_data)
    #     #print('###########')
    #     #print('1', json_stock_data.keys())
    #     #print('2', json_stock_data['TRADEINFO'].keys())
    # 
    #     stock_data = json.dumps(json_current_stock_data)
    #     #stock.stock_data = stock_data
    #     #stock.save()
    # 
    #     return stock


class DeleteStock(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = 'login'
    model = Asset
    template_name = "base_delete.html"
    success_url = reverse_lazy('stocks:stocks')
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
            messages.error(request, _('error'))
            return redirect('stocks:stocks')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Delete stock")
        context['button_text'] = _("Delete")
        context['delete_object'] = str(
            Asset.objects.get(id=self.get_object().id))
        print(context['delete_object'])
        return context
