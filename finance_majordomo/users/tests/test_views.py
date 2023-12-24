import json
from http import HTTPStatus
from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _

#from .setting import SettingsUsers
from .. import views
from ..models import User, UserSettings
from ...stocks.tests.base_settings import BaseTest


class TestUsersViews(BaseTest):

    def setUp(self):
        self.usersstocks = reverse('stocks:users_stocks')
        self.list_url = reverse('users')
        self.create_url = reverse('create_user')
        self.login_url = reverse('login')
        self.add_stock = reverse('add_stock_to_user', kwargs={'pk_stock': 32})
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
        self.assertEqual(user_list[0].username, 'user1')
        self.assertEqual(user_list[2].username, 'user3')
        self.assertEqual(user_list[1].first_name, 'Timur')
        self.assertEqual(user_list[1].last_name, 'Timurov')
        self.assertTemplateUsed(response, 'users/user_list.html')

    def test_user_list_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.list_url)
        user_list = response.context.get('user_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0].username, 'user1')
        self.assertEqual(user_list[2].username, 'user3')
        self.assertEqual(user_list[0].first_name, 'Ivan')
        self.assertEqual(user_list[0].last_name, 'Ivanov')
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
        self.assertEqual(created_user.id, 5)
        self.assertRedirects(response, self.login_url)

    def test_set_fields_to_display_GET(self):

        response = self.client_authenticated.get(
            self.set_fields)

        fields_to_display = [field.name for field in UserSettings._meta.fields]

        form = response.context.get('form')

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(
            response.context.get('page_title'), _('Fields to display'))
        self.assertEqual(
            response.context.get('button_text'), _('Save'))
        self.assertTemplateUsed(response, 'users/display_options.html')
        self.assertEqual(len(fields_to_display) - 2, len(form.fields))

        for field in form.fields:
            self.assertTrue(field in fields_to_display)
            self.assertTrue(form.fields[field])

    def test_set_fields_to_display_POST(self):
        fields_display_data = {
            'show_quantity': True,
            'show_ticker': True,
            'show_percent_result': True,
            'show_current_price': False
        }

        response = self.client_authenticated.post(
            self.set_fields, fields_display_data)

        updated_user_settings = UserSettings.objects.get(
            user=self.user_authenticated)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        for field in updated_user_settings._meta.fields:
            field_name = field.name
            if field_name not in ['id', 'user']:
                field_value = getattr(
                    updated_user_settings, field_name)
                if field_name in ['show_ticker',
                                  'show_percent_result',
                                  'show_quantity']:
                    self.assertTrue(field_value)
                else:
                    self.assertFalse(field_value)





