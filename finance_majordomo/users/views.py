import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models import Stock
from finance_majordomo.users.forms import RegisterUserForm, LoginUserForm, FieldsUserForm
from finance_majordomo.users.models import User, Portfolio
from .utils.utils import set_fields_to_user
from .utils.fields_to_display import FIELDS_TO_DISPLAY


# Create your views here.
from ..assets.models import Asset


class UserList(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_list'] = User.objects.all()
        return context


class CreateUser(SuccessMessageMixin, CreateView):
    form_class = RegisterUserForm
    template_name = "base_create_and_update.html"
    success_url = reverse_lazy('login')
    success_message = _("User has been successfully registered")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create new user")
        context['button_text'] = _("Register user")
        return context

    def form_valid(self, form):
        # form.instance.creator = self.request.user
        user = form.save()
        set_fields_to_user(user)

        #craete one and only for now portfolio for user
        Portfolio.objects.create(name='Portfolio No. 1',
                                 user=user,
                                 is_current=True
                                 )

        return super().form_valid(form)

    # def post(self, request):
    #     super(CreateUser, self).post(request)
    #     print(request)
    #     user = User.objects.get(id=request.user.id)
    #     set_fields_to_user(user)
    #
    #     return redirect(self.success_url)
    # def post(self, request, *args, **kwargs):
    #
    #     form = RegisterUserForm(request.POST)
    #
    #     if form.is_valid():
    #
    #         user = User.objects.get(id=request.user.id)
    #         user_fields_to_display = json.loads(user.fields_to_display)
    #
    #         for key, value in form.cleaned_data.items():
    #             if key in fields_to_display:
    #                 user_fields_to_display[key] = value
    #
    #         json_user_fields_to_display = json.dumps(user_fields_to_display)
    #
    #         user.fields_to_display = json_user_fields_to_display
    #         user.save()
    #
    #         messages.success(request, self.success_message)
    #         return redirect(self.success_url)
    #     return render(request, self.template_name, {'form': form,
    #                                                 'page_title': _("Fields to display"),
    #                                                 'button_text': _("Save")
    #                                                 })

class LoginUser(SuccessMessageMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'base_create_and_update.html'

    success_message = _("User has been successfully registered")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context["page_title"] = _("Login")
        context['button_text'] = _("Enter")
        return context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    messages.info(request, _('You have been successfully logged out!'))
    return redirect('home')


class AddStockToUser(SuccessMessageMixin, LoginRequiredMixin, View):
    model = User
    login_url = 'login'
    success_message = _("Stock has been successfully added to user's stock list")

    def get(self, request, *args, **kwargs):
        stock = Stock.objects.get(id=kwargs['pk_stock'])        
        stock.users.add(request.user)
        stock.save()

        return redirect('stocks')

        # user = User.objects.get(id=kwargs['pk_user'])
        # user.stocks.add(Stock.objects.get(id=kwargs['pk_stock']))
        # user.save()
        # return redirect('stocks')

    #success_message = _("User has been successfully updated!")

    # def dispatch(self, request, *args, **kwargs):
    #     if self.get_object().id == request.user.id \
    #             or request.user.is_staff:
    #         return super().dispatch(request, *args, **kwargs)
    #     message_text = _('You can\'t update other users')
    #     messages.error(request, message_text)
    #     return redirect('users')


    #кажется не нужна
    # def post(self, request, **kwargs):
    #     self.object = self.get_object()
    # 
    #     #print('AYAYAYAYAYAYA', request)
    #     #print("get", self.get_object())
    #     password1 = request.POST.get('password1')
    #     password2 = request.POST.get('password2')
    #     if password1 == password2:
    #         self.object.set_password(request.POST.get('password2'))
    #         self.object.save()
    #     return super().post(request, **kwargs)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['page_title'] = _("Update users")
    #     context['button_text'] = _("Update")
    #     return context


class AddAssetToPortfolio(SuccessMessageMixin, LoginRequiredMixin, View):
    model = Portfolio
    login_url = 'login'
    success_message = _("Asset has been successfully added to portfolio")

    def get(self, request, *args, **kwargs):
        asset = Asset.objects.get(id=kwargs['pk_asset'])
        current_portfolio = Portfolio.objects.filter(
            user=request.user,
            is_current=True)
        asset.portfolios.add(current_portfolio)
        asset.save()

        return redirect('stocks')


class SetFieldsToDisplay(SuccessMessageMixin, LoginRequiredMixin, View):
    model = User
    form_class = FieldsUserForm
    template_name = 'users/display_options.html'
    success_message = _("Display options have been successfully set")
    success_url = reverse_lazy('users_stocks')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Fields to display")
        context['button_text'] = _("Save")
        return context

    def get(self, request, *args, **kwargs):
        display_form = FieldsUserForm()

        user_fields_to_display = json.loads(request.user.fields_to_display)


        for key, value in user_fields_to_display.items():
            display_form.initial[key] = value

        return render(
            request,
            self.template_name,
            {'form': display_form,
             'page_title': _("Fields to display"),
             'button_text': _("Save")
             }
        )

    def post(self, request, *args, **kwargs):

        form = FieldsUserForm(request.POST)

        if form.is_valid():

            fields_to_display = FIELDS_TO_DISPLAY
            user_fields_to_display = dict()

            for key, value in form.cleaned_data.items():
                if key in fields_to_display:

                    user_fields_to_display[key] = value

            set_fields_to_user(request.user, user_fields_to_display)

            messages.success(request, self.success_message)
            return redirect(self.success_url)

        #should not be raised
        return render(
            request,
            self.template_name,
            {'form': form,
             'page_title': _("Fields to display"),
             'button_text': _("Save")
             }
        )
