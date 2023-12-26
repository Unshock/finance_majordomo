from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.forms.asset_forms import StockForm
from finance_majordomo.stocks.models.asset import Asset
from finance_majordomo.stocks.services.asset_services.\
    asset_model_management_services \
    import create_asset_obj_from_description
from finance_majordomo.stocks.services.\
    asset_services.asset_view_services \
    import PortfolioAssetsViewContextService,\
    execute_portfolio_asset_view_context_service



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

        portfolio_assets_data = execute_portfolio_asset_view_context_service(
            self.request.user.current_portfolio)

        asset_list = portfolio_assets_data.get('asset_list')
        total_results = portfolio_assets_data.get('total_results')

        context['page_title'] = self.request.user.username + " " + _(
            "stock list")
        context['fields_to_display'] = self.request.user.usersettings
        context['current_portfolio'] = self.request.user.current_portfolio
        context['asset_list'] = asset_list
        context['total_results'] = total_results

        return context


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
