import json
from http import HTTPStatus
from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _

from .setting import SettingsUsers
from .. import views
from ..models import User
from ..utils.fields_to_display import FIELDS_TO_DISPLAY
from ...stocks.models import StocksOfUser


class TestUsersViews(SettingsUsers):

    def setUp(self):
        self.list_url = reverse('users')
        self.create_url = reverse('create_user')
        self.login_url = reverse('login')
        self.add_stock = reverse('add_stock_to_user', kwargs={'pk_stock': 1})
        self.set_fields = reverse('set_fields')

    def test_urls_to_views(self):
        self.assertEqual(resolve(self.list_url).func.view_class,
                         views.UserList)
        self.assertEqual(resolve(self.create_url).func.view_class,
                         views.CreateUser)
        self.assertEqual(resolve(self.login_url).func.view_class,
                         views.LoginUser)
        self.assertEqual(resolve(self.add_stock).func.view_class,
                         views.AddStockToUser)
        self.assertEqual(resolve(self.set_fields).func.view_class,
                         views.SetFieldsToDisplay)

    def test_user_list_GET(self):

        response = self.client_authenticated.get(self.list_url)
        user_list = response.context.get('user_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0].username, 'user_authenticated')
        self.assertEqual(user_list[2].username, 'user_unauthenticated')
        self.assertEqual(user_list[1].first_name, 'AuthenticatedAnother')
        self.assertEqual(user_list[1].last_name, 'UserNotAdminAnother')
        self.assertTemplateUsed(response, 'users/user_list.html')

    def test_user_list_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.list_url)
        user_list = response.context.get('user_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0].username, 'user_authenticated')
        self.assertEqual(user_list[2].username, 'user_unauthenticated')
        self.assertEqual(user_list[1].first_name, 'AuthenticatedAnother')
        self.assertEqual(user_list[1].last_name, 'UserNotAdminAnother')
        self.assertTemplateUsed(response, 'users/user_list.html')

    def test_create_user_GET(self):
        response = self.client_authenticated.get(self.create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _('Create new user'))
        self.assertEqual(
            response.context.get('button_text'), _('Register user'))
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    def test_create_user_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _('Create new user'))
        self.assertEqual(
            response.context.get('button_text'), _('Register user'))
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    def test_create_user_POST(self):
        self.assertEqual(User.objects.all().count(), 3)

        user_data = {
            'username': 'Test_user',
            'first_name': 'Test_user_first_name',
            'last_name': 'Test_user_last_name',
            'password1': 'TestPassword987654',
            'password2': 'TestPassword987654'
        }

        response = self.client_unauthenticated.post(
            self.create_url, user_data)

        created_user = User.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(User.objects.all().count(), 4)
        self.assertEqual(created_user.username, 'Test_user')
        self.assertEqual(created_user.first_name, 'Test_user_first_name')
        self.assertEqual(created_user.last_name, 'Test_user_last_name')
        self.assertTrue(created_user.password)
        self.assertEqual(created_user.id, 4)
        self.assertRedirects(response, self.login_url)

    def test_add_stock_to_user(self):

        self.assertEqual(StocksOfUser.objects.filter(user_id=1).count(), 0)
        self.assertEqual(StocksOfUser.objects.all().count(), 0)

        response = self.client_authenticated.get(
            self.add_stock)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(StocksOfUser.objects.filter(user_id=1).count(), 1)
        self.assertEqual(StocksOfUser.objects.all().count(), 1)
        self.assertEqual(
            StocksOfUser.objects.get(user_id=1).stock.isin, 'isin_id_1')

    def test_set_fields_to_display_GET(self):

        response = self.client_authenticated.get(
            self.set_fields)

        form = response.context.get('form')

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(
            response.context.get('page_title'), _('Fields to display'))
        self.assertEqual(
            response.context.get('button_text'), _('Save'))
        self.assertTemplateUsed(response, 'users/display_options.html')

        for field in form.fields:
            self.assertTrue(field in FIELDS_TO_DISPLAY)
            self.assertTrue(form.fields[field])

    def test_set_fields_to_display_POST(self):

        fields_display_data = {
            'quantity': False,
            'ticker': True
        }

        response = self.client_authenticated.post(
            self.set_fields, fields_display_data)

        user_affected = User.objects.get(id=1)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        for key, value in json.loads(user_affected.fields_to_display).items():
            if key == 'ticker':
                self.assertTrue(value)
            else:
                self.assertFalse(value)





