from django.views import View
from common.utils.stocks import get_security
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from .forms import SearchForm, SearchResultForm
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
                          # 'stock_ppif'
                          ]

        allowed_boardids = [
            'TQBR',
            'TQOB',
            'TQCB',
        ]

        if form.is_valid():
            search_data = form.cleaned_data.get('search_data')

            search_result = get_security(search_data)

            search_result_list = list(filter(
                lambda sec: sec['is_traded'] and
                            sec['group'] in allowed_groups and
                            sec['primary_boardid'] in allowed_boardids and
                            sec['secid'].isupper(),
                search_result))

            # forms_list = []
            # 
            # for search_item in search_result_list:
            #     forms_list.append(
            #         SearchResultForm(initial={
            #             'secid': search_item.get('secid'),
            #             'shortname': search_item.get('shortname'),
            #             'regnumber': search_item.get('regnumber'),
            #             'name': search_item.get('name'),
            #             'isin': search_item.get('isin'),
            #             'type': search_item.get('type'),
            #             'group': search_item.get('group'),
            #             'primary_boardid': search_item.get('primary_boardid'),
            #         })
            #     )

            context = {
                'page_title': _("Search results"),
                'search_result_list':
                    search_result_list if search_result_list else None,
            }

            return render(
                request,
                'search/search_result_list.html',
                context=context
            )
