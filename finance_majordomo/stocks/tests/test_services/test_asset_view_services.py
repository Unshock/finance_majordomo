from datetime import datetime
from unittest.mock import patch

from finance_majordomo.stocks.models import AssetOfPortfolio
from finance_majordomo.stocks.services.asset_services.asset_view_services import \
    get_assets_of_user_qs, execute_portfolio_asset_view_context_service
from finance_majordomo.stocks.tests.base_settings import BaseTest
from finance_majordomo.users.models import Portfolio

FIXTURES_FOLDER = "fixtures"

UPDATE_CURRENCY_RATE = "finance_majordomo.stocks.services.asset_services." \
    "asset_view_services.update_currency_rates"

UPDATE_USD = "finance_majordomo.stocks.services.asset_services." \
    "asset_view_services.update_usd"

UPDATE_HISTORICAL_DATA = "finance_majordomo.stocks.services.asset_services." \
    "asset_view_services.update_historical_data"

GET_CURRENCY_RATE_DATETIME = \
    "finance_majordomo.stocks.services.currency_services." \
    "currency_management_services.get_today_date"


class AssetViewServicesTest(BaseTest):

    def test_get_assets_of_user_qs(self):
        new_portfolio = Portfolio.objects.create(
            user=self.user_authenticated,
            name='TestPortfolio',
            is_current=False
        )

        new_asset = self.share_POSI
        new_asset.pk, new_asset.isin, new_asset.secid = None, 'Unique', 'Unique'
        new_asset.save()

        AssetOfPortfolio.objects.create(
            portfolio=new_portfolio, asset=new_asset)

        assets_of_user = get_assets_of_user_qs(self.user_authenticated)

        self.assertEqual(len(assets_of_user), 4)
        self.assertIn(self.bond1, assets_of_user)
        self.assertIn(self.share_POSI, assets_of_user)
        self.assertIn(self.share_LSRG, assets_of_user)
        self.assertIn(new_asset, assets_of_user)

    def test_get_assets_of_user_qs_no_assets(self):
        assets_of_user = get_assets_of_user_qs(
            self.user_authenticated_no_assets)

        self.assertEqual(len(assets_of_user), 0)

    @patch(GET_CURRENCY_RATE_DATETIME)
    @patch(UPDATE_CURRENCY_RATE, lambda *args, **kwargs: None)
    @patch(UPDATE_USD, lambda *args, **kwargs: None)
    @patch(UPDATE_HISTORICAL_DATA, lambda *args, **kwargs: None)
    def test_execute_portfolio_asset_view_context_service(
            self, mocked_datetime):
        mocked_datetime.return_value = datetime(year=2023, month=5, day=18)

        portfolio_assets_data = execute_portfolio_asset_view_context_service(
            self.user_authenticated.current_portfolio)

        total_res = portfolio_assets_data['total_results']
        asset_list = portfolio_assets_data['asset_list']

        self.assertEqual(total_res['total_purchase_price'], '8 500.00')
        self.assertEqual(total_res['total_current_price'], '12 520.47')
        self.assertEqual(total_res['total_accruals_received'], '30.80')  # no taxes
        self.assertEqual(total_res['total_percent_result'], '+ 47.66%')
        self.assertEqual(
            total_res['total_financial_result_no_divs'], '4 020.47')
        self.assertEqual(
            total_res['total_financial_result_with_divs'], '4 051.27')
        self.assertEqual(
            total_res['total_rate_of_return'], '+ 47.66%')
        self.assertEqual(
            total_res['total_current_price_usd'], '155.02')
        self.assertEqual(
            total_res['total_financial_result_with_divs_usd'], '81.75')

        self.assertEqual(len(asset_list), 3)

        asset_1, asset_2, asset_3 = asset_list[0], asset_list[1], asset_list[2]

        self.assertEqual(asset_1.quantity, '5')
        self.assertEqual(asset_2.quantity, '5')
        self.assertEqual(asset_3.quantity, '1')

        self.assertEqual(asset_1.avg_purchase_price, '1 000.00')
        self.assertEqual(asset_2.avg_purchase_price, '500.00')
        self.assertEqual(asset_3.avg_purchase_price, '1 000.00')

        self.assertEqual(asset_1.purchase_price, '5 000.00')
        self.assertEqual(asset_2.purchase_price, '2 500.00')
        self.assertEqual(asset_3.purchase_price, '1 000.00')

        self.assertEqual(asset_1.current_price, '8 577.00')
        self.assertEqual(asset_2.current_price, '2 950.00')
        self.assertEqual(asset_3.current_price, '993.47')

        self.assertEqual(asset_1.accruals_received, '0.00')
        self.assertEqual(asset_2.accruals_received, '0.00')
        self.assertEqual(asset_3.accruals_received, '30.80')

        self.assertEqual(asset_1.avg_purchase_price_usd, '12.24')
        self.assertEqual(asset_2.avg_purchase_price_usd, '6.12')
        self.assertEqual(asset_3.avg_purchase_price_usd, '12.24')

        self.assertEqual(asset_1.purchase_price_usd, '61.22')
        self.assertEqual(asset_2.purchase_price_usd, '30.61')
        self.assertEqual(asset_3.purchase_price_usd, '12.24')

        self.assertEqual(asset_1.current_price_usd, '106.20')
        self.assertEqual(asset_2.current_price_usd, '36.53')
        self.assertEqual(asset_3.current_price_usd, '12.30')

        self.assertEqual(asset_1.accruals_received_usd, '0.00')
        self.assertEqual(asset_2.accruals_received_usd, '0.00')
        self.assertEqual(asset_3.accruals_received_usd, '0.38')

        self.assertEqual(asset_1.percentage_result_with_accruals, '+ 71.54%')
        self.assertEqual(asset_2.percentage_result_with_accruals, '+ 18.00%')
        self.assertEqual(asset_3.percentage_result_with_accruals, '+ 2.43%')

        self.assertEqual(asset_1.percentage_result_no_accruals, '+ 71.54%')
        self.assertEqual(asset_2.percentage_result_no_accruals, '+ 18.00%')
        self.assertEqual(asset_3.percentage_result_no_accruals, '- 0.65%')

        self.assertEqual(asset_1.financial_result_with_accruals, '3 577.00')
        self.assertEqual(asset_2.financial_result_with_accruals, '450.00')
        self.assertEqual(asset_3.financial_result_with_accruals, '24.27')

        self.assertEqual(asset_1.financial_result_no_accruals, '3 577.00')
        self.assertEqual(asset_2.financial_result_no_accruals, '450.00')
        self.assertEqual(asset_3.financial_result_no_accruals, '-6.53')

    @patch(GET_CURRENCY_RATE_DATETIME)
    @patch(UPDATE_CURRENCY_RATE, lambda *args, **kwargs: None)
    @patch(UPDATE_USD, lambda *args, **kwargs: None)
    @patch(UPDATE_HISTORICAL_DATA, lambda *args, **kwargs: None)
    def test_execute_portfolio_asset_view_context_service_no_assets(
            self, mocked_datetime):

        mocked_datetime.return_value = datetime(year=2023, month=5, day=18)

        portfolio_assets_data = execute_portfolio_asset_view_context_service(
            self.user_authenticated_no_assets.current_portfolio)

        total_res = portfolio_assets_data['total_results']
        asset_list = portfolio_assets_data['asset_list']

        self.assertEqual(total_res, {})
        self.assertEqual(asset_list, [])
