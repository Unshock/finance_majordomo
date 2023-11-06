from django.views import View
from common.utils.stocks import get_security
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from .forms import SearchForm
from django.utils.translation import gettext_lazy as _


class Search(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        form = SearchForm()

        context = {
            'page_title': _("Search for assets"),
            'button_text': _("Search"),
            'form': form
        }

        return render(
            request,
            'base_create_and_update.html',
            context=context
        )

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)

        allowed_groups = ['stock_shares',
                          'stock_bonds',
                          #'stock_ppif'
                          ]

        if form.is_valid():
            search_data = form.cleaned_data.get('search_data')

            search_result = get_security(search_data)
            print('search_result', search_result)
            search_result_list = list(filter(
                lambda d: d['is_traded'] and d['group'] in allowed_groups,
                search_result))


            context = {
                'page_title': _("Search results"),
                'search_result_list':
                    search_result_list if search_result_list else None

            }

            return render(
                request,
                'search/search_result_list.html',
                context=context
            )
