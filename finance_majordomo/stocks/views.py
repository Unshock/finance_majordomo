from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from finance_majordomo.stocks.forms import StockForm
from finance_majordomo.stocks.models import Stock

from django.utils.translation import gettext_lazy as _

from common.utils.stocks import validate_ticker


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
            obj = Stock()
            obj.ticker = validated_ticker['ticker']
            obj.name = validated_ticker['shortname']
            obj.save()
            #return super().post(request, *args, **kwargs)

            messages.success(request, self.success_message)
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


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