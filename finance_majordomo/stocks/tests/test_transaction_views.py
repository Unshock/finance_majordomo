import datetime
from decimal import Decimal
from unittest.mock import patch
from django import forms

from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _
from http import HTTPStatus

from .base_settings import BaseTest
from finance_majordomo.stocks.views import transaction_views
from finance_majordomo.stocks.models.transaction_models import Transaction
from ..forms.transaction_forms import TransactionForm


EXECUTE_TRANSACTION_FORM_SERVICE = \
    "finance_majordomo.stocks.views.transaction_views." \
    "execute_transaction_form_service"

EXECUTE_CREATE_TRANSACTION_SERVICE = \
    "finance_majordomo.stocks.views.transaction_views." \
    "execute_create_transaction_service"

RUN_TRANSACTION_VALIDATOR = \
    "finance_majordomo.stocks.views.transaction_views." \
    "validate_transaction"

EXECUTE_UPDATE_ACCRUALS_OF_PORTFOLIO = \
    "finance_majordomo.stocks.views.transaction_views." \
    "execute_update_accruals_of_portfolio"


class TestTransactionsViews(BaseTest):

    def setUp(self):
        self.list_all_transactions = reverse('stocks:transactions')
        self.list_user_transactions = reverse('stocks:user_transactions')
        self.add_transaction = reverse('stocks:add_transaction')
        self.delete_transaction = reverse(
            'stocks:delete_transaction', kwargs={'pk': 3}
        )
        self.login = reverse('login')
        self.search = reverse('stocks:search')
        self.add_transaction_with_id = \
            reverse('stocks:add_transaction') + '?asset_id=31'
        self.add_transaction_with_asset_secid_existing = \
            reverse('stocks:add_transaction') + '?asset_secid=POSI'
        self.add_transaction_with_asset_secid_nonexisting = \
            reverse('stocks:add_transaction') + '?asset_secid=GAZP'

    def test_urls_to_views(self):
        self.assertEqual(resolve(self.list_all_transactions).func.view_class,
                         transaction_views.TransactionList)
        self.assertEqual(resolve(self.list_user_transactions).func.view_class,
                         transaction_views.UsersTransactionList)
        self.assertEqual(resolve(self.add_transaction).func.view_class,
                         transaction_views.AddTransaction)
        # print(self.add_transaction_with_id)
        # self.assertEqual(resolve(self.add_transaction_with_id).func.view_class,
        #                 transaction_views.AddTransaction)
        self.assertEqual(resolve(self.delete_transaction).func.view_class,
                         transaction_views.DeleteTransaction)

    def test_transaction_list_GET(self):
        response = self.client_authenticated.get(self.list_all_transactions)
        transactions = response.context.get('transaction_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(transactions), 3)
        self.assertEqual(
            str(transactions[0]),
            'BUY x1.00 SU26222RMFS8 for 1000.00 on 2023-04-14'
        )
        self.assertEqual(
            str(transactions[1]),
            'BUY x5.00 LSRG for 500.00 on 2023-04-15'
        )
        self.assertEqual(
            str(transactions[2]),
            'BUY x5.00 POSI for 1000.00 on 2023-04-16'
        )
        self.assertEqual(transactions[0].date, datetime.date(2023, 4, 14))
        self.assertEqual(transactions[1].portfolio.user.username, 'user1')
        self.assertEqual(transactions[2].quantity, Decimal(5))
        self.assertEqual(transactions[0].price, Decimal('1000'))
        self.assertEqual(transactions[1].asset.isin, 'RU000A0JPFP0')
        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

        self.assertEqual(response.context.get('page_title'), "Transaction list")

    def test_user_transaction_list_GET(self):
        response = self.client_authenticated.get(self.list_user_transactions)
        transactions = response.context.get('transaction_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(transactions), 3)

        self.assertEqual(
            str(transactions[2]),
            'BUY x1.00 SU26222RMFS8 for 1000.00 on 2023-04-14'
        )
        self.assertEqual(
            str(transactions[1]),
            'BUY x5.00 LSRG for 500.00 on 2023-04-15'
        )
        self.assertEqual(
            str(transactions[0]),
            'BUY x5.00 POSI for 1000.00 on 2023-04-16'
        )

        self.assertEqual(transactions[2].date, datetime.date(2023, 4, 14))
        self.assertEqual(transactions[1].portfolio.user.username, 'user1')
        self.assertEqual(transactions[0].quantity, Decimal(5))
        self.assertEqual(transactions[2].price, Decimal('1000'))
        self.assertEqual(transactions[1].asset.isin, 'RU000A0JPFP0')
        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

        self.assertEqual(
            response.context.get('page_title'), "user1 transaction list"
        )

    def test_user_no_assets_transaction_list_GET(self):
        response = self.client_authenticated_no_assets.get(
            self.list_user_transactions)
        transactions = response.context.get('transaction_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(transactions.count(), 0)

        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

        self.assertEqual(
            response.context.get('page_title'),
            "user2 transaction list")

    def test_transaction_list_unauthenticated_client_GET(self):
        response = self.client_unauthenticated.get(
            self.list_all_transactions)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f'/login/?next={self.list_all_transactions}')

    def test_user_transaction_list_unauthenticated_client_GET(self):
        response = self.client_unauthenticated.get(
            self.list_user_transactions)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f'/login/?next={self.list_user_transactions}')

    def test_add_transaction_no_data_GET(self):
        response = self.client_authenticated.get(self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _("Add new transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Add"))
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    def test_add_transaction_no_data_user_has_no_assets_GET(self):
        response = self.client_authenticated_no_assets\
            .get(self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.search)

    @patch(EXECUTE_TRANSACTION_FORM_SERVICE, lambda **kwargs: forms.Form)
    def test_add_transaction_GET_with_asset_id(self):
        response = self.client_authenticated.get(
            self.add_transaction_with_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _("Add new transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Add"))
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    @patch(EXECUTE_TRANSACTION_FORM_SERVICE, lambda **kwargs: forms.Form)
    def test_add_transaction_GET_with_SECID(self):
        response = self.client_authenticated.get(
            self.add_transaction_with_asset_secid_existing)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _("Add new transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Add"))
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    @patch(EXECUTE_CREATE_TRANSACTION_SERVICE,
           lambda **kwargs: None)
    @patch(EXECUTE_TRANSACTION_FORM_SERVICE,
           lambda **kwargs: TransactionForm(data={'price': Decimal('1')}))  # valid Form
    def test_add_transaction_authenticated_POST(self):

        response = self.client_authenticated.post(
            self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.list_all_transactions)

    @patch(EXECUTE_CREATE_TRANSACTION_SERVICE, lambda **kwargs: None)
    @patch(EXECUTE_TRANSACTION_FORM_SERVICE,
           lambda **kwargs: forms.Form(data={}))  # valid Form
    def test_add_transaction_authenticated_POST(self):

        response = self.client_authenticated.post(
            self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.list_all_transactions)
        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

    @patch(EXECUTE_CREATE_TRANSACTION_SERVICE, lambda **kwargs: None)
    @patch(EXECUTE_TRANSACTION_FORM_SERVICE,
           lambda **kwargs: TransactionForm())  # invalid Form
    def test_add_transaction_authenticated_POST(self):

        response = self.client_authenticated.post(
            self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    def test_add_transaction_unauthenticated_POST(self):

        response = self.client_unauthenticated.post(
            self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f'/login/?next={self.add_transaction}')

    def test_delete_transaction_GET(self):
        response = self.client_authenticated.get(self.delete_transaction)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _("Delete transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Delete"))
        self.assertTemplateUsed(response, 'base_delete.html')

    @patch(RUN_TRANSACTION_VALIDATOR, lambda *args, **kwargs: True)
    @patch(EXECUTE_UPDATE_ACCRUALS_OF_PORTFOLIO, lambda *args, **kwargs: None)
    def test_delete_transaction_valid_authenticated_POST(self):
        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 3)
        self.assertTrue(Transaction.objects.last().id == 3)

        response = self.client_authenticated.post(self.delete_transaction)

        transactions = Transaction.objects.all()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(transactions.count(), 2)
        self.assertTrue(Transaction.objects.last().id == 2)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=3)
        self.assertRedirects(response, self.list_all_transactions)

    @patch(RUN_TRANSACTION_VALIDATOR, lambda *args, **kwargs: False)
    @patch(EXECUTE_UPDATE_ACCRUALS_OF_PORTFOLIO, lambda *args, **kwargs: None)
    def test_delete_transaction_non_valid_authenticated_POST(self):
        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 3)
        self.assertTrue(Transaction.objects.last().id == 3)

        response = self.client_authenticated.post(self.delete_transaction)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.list_all_transactions)
        self.assertEqual(transactions.count(), 3)
        self.assertTrue(Transaction.objects.last().id == 3)

    def test_delete_transaction_unauthenticated(self):

        delete_path = self.delete_transaction

        response = self.client_unauthenticated.get(self.delete_transaction)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f'/login/?next={delete_path}')

        response = self.client_unauthenticated.post(self.delete_transaction)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f'/login/?next={delete_path}')
