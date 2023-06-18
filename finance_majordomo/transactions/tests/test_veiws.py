import datetime
from decimal import Decimal
from pprint import pprint

from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _
from http import HTTPStatus
from .setting import SettingsTransactions
from .. import views
from ..models import Transaction
from ...stocks.models import Stock


class TestTransactionsViews(SettingsTransactions):

    def setUp(self):
        self.list_all_transactions = reverse('transactions')
        self.list_user_transactions = reverse('user_transactions')
        self.add_transaction = reverse('add_transaction')
        self.add_transaction_with_asset = reverse(
            'add_transaction', kwargs={'asset_id': 3})
        self.delete_transaction = reverse(
            'delete_transaction', kwargs={'pk': 3})
        self.login = reverse('login')

    def test_urls_to_views(self):
        self.assertEqual(resolve(self.list_all_transactions).func.view_class,
                         views.TransactionList)
        self.assertEqual(resolve(self.list_user_transactions).func.view_class,
                         views.UsersTransactionList)
        self.assertEqual(resolve(self.add_transaction).func.view_class,
                         views.AddTransaction)
        self.assertEqual(
            resolve(self.add_transaction_with_asset).func.view_class,
            views.AddTransaction)
        self.assertEqual(resolve(self.delete_transaction).func.view_class,
                         views.DeleteTransaction)

    def test_transaction_list_GET(self):

        response = self.client_authenticated.get(self.list_all_transactions)
        transactions = response.context.get('transaction_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(transactions), 6)

        # it should be div_id_2 because of order_by -date:
        self.assertEqual(transactions[0].date,
                         datetime.date(1999, 12, 31))
        self.assertEqual(transactions[1].user.last_name, 'UserNotAdmin')
        self.assertEqual(transactions[2].quantity, 3)
        self.assertEqual(transactions[3].price, Decimal('80'))
        self.assertEqual(transactions[5].ticker.isin, 'isin_id_2')
        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

        self.assertEqual(response.context.get('page_title'), "Transaction list")

    def test_user_transaction_list_GET(self):

        response = self.client_authenticated.get(self.list_user_transactions)
        transactions = response.context.get('transaction_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(transactions), 5)

        # it should be div_id_2 because of order_by -date:
        self.assertEqual(transactions[0].date,
                         datetime.date(1999, 12, 31))
        self.assertEqual(transactions[1].user.last_name, 'UserNotAdmin')
        self.assertEqual(transactions[2].quantity, 3)
        self.assertEqual(transactions[3].price, Decimal('80'))
        self.assertEqual(transactions[4].ticker.isin, 'isin_id_3')
        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

        self.assertEqual(
            response.context.get('page_title'),
            "user_authenticated transaction list")

    def test_another_user_transaction_list_GET(self):

        response = self.client_authenticated_another.get(
            self.list_user_transactions)
        transactions = response.context.get('transaction_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(transactions.count(), 1)

        self.assertEqual(transactions[0].ticker.isin, 'isin_id_2')
        self.assertTemplateUsed(response, 'transactions/transaction_list.html')

        self.assertEqual(
            response.context.get('page_title'),
            "user_authenticated_another transaction list")

    def test_transaction_list_unauthenticated_client_GET(self):

        response = self.client_unauthenticated.get(
            self.list_all_transactions)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        response = self.client_unauthenticated.get(
            self.list_user_transactions)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_add_transaction_no_data_GET(self):

        response = self.client_authenticated.get(self.add_transaction)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _("Add new transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Add"))
        self.assertTemplateUsed(response, 'base_create_and_update.html')


    def test_add_transaction_with_data_GET(self):
        response = self.client_authenticated.get(
            self.add_transaction_with_asset)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['form'].initial, {'ticker': 3})
        self.assertEqual(
            response.context.get('page_title'), _("Add new transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Add"))
        self.assertTemplateUsed(response, 'base_create_and_update.html')

    def test_add_transaction_authenticated_POST(self):

        transaction_data = {
            'transaction_type': 'BUY',
            'asset_type': 'STOCK',
            'ticker': self.stock_id_3.id,
            'date': '2023-01-01',
            'price': '555',
            'quantity': 1
        }

        response = self.client_authenticated.post(
            self.add_transaction, data=transaction_data)

        transactions = Transaction.objects.all()
        last_transaction = transactions.last()
        print(last_transaction.ticker)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(transactions.count(), 7)
        self.assertEqual(last_transaction.date, datetime.date(2023, 1, 1))
        self.assertEqual(last_transaction.price, Decimal(555))
        self.assertEqual(last_transaction.user, self.user_authenticated)
        self.assertRedirects(response, self.list_all_transactions)

    def test_add_transaction_unauthenticated_POST(self):

        transaction_data = {
            'transaction_type': 'BUY',
            'asset_type': 'STOCK',
            'ticker': self.stock_id_3.id,
            'date': '2023-01-01',
            'price': '555',
            'quantity': 1
        }

        response = self.client_unauthenticated.post(
            self.add_transaction, data=transaction_data)

        transactions = Transaction.objects.all()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(transactions.count(), 6)

    def test_delete_transaction_GET(self):

        response = self.client_authenticated.get(self.delete_transaction)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('page_title'), _("Delete transaction"))
        self.assertEqual(
            response.context.get('button_text'), _("Delete"))
        self.assertTemplateUsed(response, 'base_delete.html')

    def test_delete_transaction_authenticated_POST(self):

        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 6)
        self.assertTrue(Transaction.objects.get(id=3).date,
                        datetime.date(2019, 1, 1))

        response = self.client_authenticated.post(self.delete_transaction)

        transactions = Transaction.objects.all()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(transactions.count(), 5)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=3)
        self.assertRedirects(response, self.list_all_transactions)

# dividends update have not been tested

    # 
    # def test_add_dividend_to_user_GET(self):
    # 
    #     dividends_of_user = DividendsOfUser.objects.all()
    #     div_of_user_id_1 = dividends_of_user.get(id=1)
    # 
    #     self.assertEqual(div_of_user_id_1.user, self.user_authenticated)
    #     self.assertEqual(div_of_user_id_1.dividend, self.dividend_id_1)
    #     self.assertEqual(div_of_user_id_1.is_received, False)
    # 
    #     response = self.client_authenticated.get(self.add_dividend)
    # 
    #     div_of_user_id_1 = dividends_of_user.get(id=1)
    #     self.assertEqual(div_of_user_id_1.is_received, True)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # 
    # def test_remove_dividend_from_user_GET(self):
    # 
    #     dividends_of_user = DividendsOfUser.objects.all()
    #     div_of_user_id_2 = dividends_of_user.get(id=2)
    # 
    #     self.assertEqual(div_of_user_id_2.user, self.user_authenticated)
    #     self.assertEqual(div_of_user_id_2.dividend, self.dividend_id_2)
    #     self.assertEqual(div_of_user_id_2.is_received, True)
    # 
    #     response = self.client_authenticated.get(self.remove_dividend)
    # 
    #     div_of_user_id_2 = dividends_of_user.get(id=1)
    #     self.assertEqual(div_of_user_id_2.is_received, False)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # 

    # def test_create_task_GET(self):
    #     response = self.client_authenticated.get(self.create_url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(
    #         response.context.get('page_title'), _('Create new task'))
    #     self.assertEqual(
    #         response.context.get('button_text'), _('Create'))
    #     self.assertTemplateUsed(response, 'base_create_and_update.html')
    # 
    # def test_create_task_GET_unauthenticated_client(self):
    #     response = self.client_unauthenticated.get(self.create_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_create_task_POST(self):
    #     self.assertEqual(Task.objects.all().count(), 3)
    # 
    #     task_data = {
    #         'name': 'Test_task_4',
    #         'description': 'Test_task_4_description',
    #         'status': self.status_id_2.id,
    #         'labels': self.test_label_id_1.id
    #     }
    # 
    #     response = self.client_authenticated.post(
    #         self.create_url, task_data)
    # 
    #     created_task = Task.objects.last()
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(Task.objects.all().count(), 4)
    #     self.assertEqual(created_task.name, 'Test_task_4')
    #     self.assertEqual(created_task.id, 4)
    #     self.assertEqual(created_task.creator.username, 'user_authenticated')
    #     self.assertRedirects(response, self.list_url)
    # 
    # def test_create_task_POST_unauthenticated_client(self):
    #     response = self.client_unauthenticated.post(self.create_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_update_task_GET(self):
    #     response = self.client_authenticated.get(self.update_url)
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(response.context.get('page_title'), _('Update task'))
    #     self.assertEqual(response.context.get('button_text'), _('Update'))
    #     self.assertTemplateUsed(response, 'base_create_and_update.html')
    # 
    # def test_update_task_GET_unauthenticated_client(self):
    #     response = self.client_unauthenticated.get(self.update_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_update_task_GET_client_not_creator(self):
    #     response = self.client_authenticated_not_creator.get(self.update_url)
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(response.context.get('page_title'), _('Update task'))
    #     self.assertEqual(response.context.get('button_text'), _('Update'))
    #     self.assertTemplateUsed(response, 'base_create_and_update.html')
    # 
    # def test_update_task_POST(self):
    #     self.assertEqual(Task.objects.all().count(), 3)
    # 
    #     task_data = {
    #         'name': 'Test_task_1_updated',
    #         'description': 'Test_task_1_description_updated',
    #         'status': self.status_id_2.id,
    #         'labels': self.test_label_id_1.id
    #     }
    # 
    #     response = self.client_authenticated.post(
    #         self.update_url, task_data)
    # 
    #     updated_task = Task.objects.get(id=1)
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(Task.objects.all().count(), 3)
    #     self.assertEqual(updated_task.name, 'Test_task_1_updated')
    #     self.assertEqual(updated_task.id, 1)
    #     self.assertEqual(updated_task.creator.username, 'user_authenticated')
    #     self.assertRedirects(response, self.list_url)
    # 
    # def test_update_task_POST_unauthenticated_client(self):
    #     response = self.client_unauthenticated.post(self.update_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_update_task_POST_client_not_creator(self):
    #     self.assertEqual(Task.objects.all().count(), 3)
    # 
    #     task_data = {
    #         'name': 'Test_task_1_updated',
    #         'description': 'Test_task_1_description_updated',
    #         'status': self.status_id_2.id,
    #         'labels': self.test_label_id_1.id
    #     }
    # 
    #     response = self.client_authenticated_not_creator.post(
    #         self.update_url, task_data)
    # 
    #     updated_task = Task.objects.get(id=1)
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(Task.objects.all().count(), 3)
    #     self.assertEqual(updated_task.name, 'Test_task_1_updated')
    #     self.assertEqual(updated_task.id, 1)
    #     self.assertEqual(updated_task.creator.username, 'user_authenticated')
    #     self.assertRedirects(response, self.list_url)
    # 
    # def test_delete_task_GET(self):
    #     response = self.client_authenticated.get(self.delete_url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(response.context.get('page_title'), _('Delete task'))
    #     self.assertEqual(response.context.get('button_text'), _('Delete'))
    #     self.assertTemplateUsed(response, 'base_delete.html')
    # 
    # def test_delete_task_GET_unauthenticated_client(self):
    #     response = self.client_unauthenticated.get(self.delete_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_delete_task_GET_client_not_creator(self):
    #     response = self.client_authenticated_not_creator.get(self.delete_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_delete_task_POST(self):
    #     self.assertEqual(Task.objects.all().count(), 3)
    # 
    #     response = self.client_authenticated.post(
    #         self.delete_url)
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(Task.objects.all().count(), 2)
    #     self.assertRedirects(response, self.list_url)
    # 
    # def test_delete_task_POST_unauthenticated_client(self):
    #     response = self.client_unauthenticated.post(self.delete_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_delete_task_POST_client_not_creator(self):
    #     self.assertEqual(Task.objects.all().count(), 3)
    # 
    #     response = self.client_authenticated_not_creator.post(
    #         self.delete_url)
    # 
    #     self.assertEqual(Task.objects.all().count(), 3)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(Task.objects.get(id=1).name, 'Test_task_1')
    # 
    # def test_detail_task_GET(self):
    #     response = self.client_authenticated.get(self.detail_url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(response.context.get('page_title'), _('Detailed task'))
    #     self.assertTemplateUsed(response, 'tasks/detail_task.html')
    # 
    # def test_detail_task_GET_unauthenticated_client(self):
    #     response = self.client_unauthenticated.get(self.detail_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    # 
    # def test_detail_task_GET_client_not_creator(self):
    #     response = self.client_authenticated_not_creator.get(self.detail_url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(response.context.get('page_title'), _('Detailed task'))
    #     self.assertTemplateUsed(response, 'tasks/detail_task.html')