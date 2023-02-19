from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.utils.translation import gettext_lazy as _

from finance_majordomo.stocks.models import Stock
from finance_majordomo.users.forms import RegisterUserForm, LoginUserForm
from finance_majordomo.users.models import User, UsersStocks


# Create your views here.

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
        form.instance.creator = self.request.user
        return super().form_valid(form)

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
        user = User.objects.get(id=kwargs['pk_user'])
        user.stocks.add(Stock.objects.get(id=kwargs['pk_stock']))
        user.save()
        return redirect('stocks')

# class AddStockToUser(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
#     success_message = _("Stock has been successfully added to user's stock list")
#     login_url = 'login'
#     #form_class = UpdateUserForm
#     model = UsersStocks
#     #template_name = "base_create_and_update.html"
#     success_url = reverse_lazy('stocks')
#     fields = ['user', 'stock']
#     pk_url_kwarg = 'pk_user'


    #success_message = _("User has been successfully updated!")

    # def dispatch(self, request, *args, **kwargs):
    #     if self.get_object().id == request.user.id \
    #             or request.user.is_staff:
    #         return super().dispatch(request, *args, **kwargs)
    #     message_text = _('You can\'t update other users')
    #     messages.error(request, message_text)
    #     return redirect('users')

    def post(self, request, **kwargs):
        self.object = self.get_object()

        print('AYAYAYAYAYAYA', request)
        print("get", self.get_object())
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            self.object.set_password(request.POST.get('password2'))
            self.object.save()
        return super().post(request, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Update users")
        context['button_text'] = _("Update")
        return context

class AddTransaction(SuccessMessageMixin, LoginRequiredMixin, View):
    pass






