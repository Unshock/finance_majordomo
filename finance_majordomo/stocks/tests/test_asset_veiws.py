from django.urls import reverse, resolve
from http import HTTPStatus
from unittest.mock import patch
from .base_settings import BaseTest
from ..views import asset_views
from ..models.asset import Asset
from ...users.models import Portfolio, User


class TestStocksViews(BaseTest):

    def setUp(self):
        self.list_url = reverse('stocks:stocks')
        self.add_asset = reverse('stocks:add_stock')
        self.portfolio_assets = reverse('stocks:users_stocks')
        self.delete_asset = reverse('stocks:delete_asset', kwargs={'pk': 4})

    def test_urls_to_views(self):
        self.assertEqual(resolve(self.list_url).func.view_class,
                         asset_views.Stocks)
        self.assertEqual(resolve(self.add_asset).func.view_class,
                         asset_views.AddStock)
        self.assertEqual(resolve(self.portfolio_assets).func.view_class,
                         asset_views.PortfolioAssets)
        self.assertEqual(resolve(self.delete_asset).func.view_class,
                         asset_views.DeleteStock)

    def test_assets_list_GET(self):

        response = self.client_authenticated.get(self.list_url)
        assets = response.context.get('object_list')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(assets), 3)

        self.assertEqual(assets[0], Asset.objects.get(id=30))
        self.assertEqual(assets[1].secid, 'LSRG')
        self.assertEqual(assets[2], Asset.objects.get(id=32))

        self.assertTemplateUsed(response, 'stocks/stock_list.html')

    def test_portfolio_assets_empty_list_GET(self):
        response = self.client_authenticated_no_assets.get(
            self.portfolio_assets
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('asset_list'), list())
        self.assertEqual(response.context.get('total_results'), dict())

        self.assertTemplateUsed(response, 'stocks/user_stock_list.html')

    @patch("finance_majordomo.stocks.views.asset_views."
           "execute_portfolio_asset_view_context_service",
           lambda *args: {'total_results': {'total': '10'},
                          'asset_list': ['AssetObj']})
    def test_portfolio_assets_list_GET(self):
        response = self.client_authenticated.get(
            self.portfolio_assets
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('asset_list'), ['AssetObj'])
        self.assertEqual(response.context.get('total_results'), {'total': '10'})
        self.assertEqual(
            response.context.get('current_portfolio'),
            Portfolio.objects.get(id=2)
        )
        self.assertEqual(
            response.context.get('fields_to_display'),
            User.objects.get(id=2).usersettings
        )
        self.assertTemplateUsed(response, 'stocks/user_stock_list.html')

    def test_asset_list_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_portfolio_asset_list_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.portfolio_assets)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_add_asset_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.add_asset)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_delete_asset_GET_unauthenticated_client(self):
        response = self.client_unauthenticated.get(self.delete_asset)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        #print(response.context.get('stock_list'))
        #assets = response.context.get('object_list')
            # 
            # self.assertEqual(response.status_code, HTTPStatus.OK)
            # self.assertEqual(len(assets), 3)
            # 
            # self.assertEqual(assets[0], Asset.objects.get(id=30))
            # self.assertEqual(assets[1].secid, 'LSRG')
            # self.assertEqual(assets[2], Asset.objects.get(id=32))
            # 
            # self.assertTemplateUsed(response, 'stocks/stock_list.html')
        # response = self.client_authenticated.get(self.list_url)
        # dividends = response.context.get('dividend_list')
        # 
        # self.assertEqual(response.status_code, HTTPStatus.OK)
        # self.assertEqual(len(dividends), 2)
        # 
        # # it should be div_id_2 because of order_by -date:
        # self.assertEqual(dividends[0]['div_obj'].amount, Decimal('100000.00'))
        # self.assertEqual(dividends[1]['div_obj'].id, 1)
        # self.assertEqual(dividends[0]['div_obj'].stock.ticker, "LSNG")
        # self.assertEqual(dividends[0]['is_received'], True)
        # self.assertEqual(dividends[1]['is_received'], False)
        # self.assertTemplateUsed(response, 'dividends/dividend_list.html')
    # 
    # def test_dividend_list_another_user_GET(self):
    # 
    #     response = self.client_authenticated_another.get(self.list_url)
    #     dividends = response.context.get('dividend_list')
    # 
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertEqual(len(dividends), 0)
    #     self.assertTemplateUsed(response, 'dividends/dividend_list.html')
    # 
    # def test_dividend_list_GET_unauthenticated_client(self):
    #     response = self.client_unauthenticated.get(self.list_url)
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
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