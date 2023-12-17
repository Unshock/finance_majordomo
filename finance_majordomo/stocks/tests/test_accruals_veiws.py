from decimal import Decimal
from http import HTTPStatus
from unittest.mock import patch, Mock
from django.urls import reverse, resolve


from .base_settings import BaseTest
from ..models.accrual_models import AccrualsOfPortfolio
from ..services.accrual_services.accrual_calculation_services import \
    get_accrual_result_of_portfolio
from ..views import accrual_views


EXECUTE_PORTFOLIO_ACCRUAL_VIEW_CONTEXT_SERVICE = \
    "finance_majordomo.stocks.views.accrual_views." \
    "execute_portfolio_accrual_view_context_service"


class TestAccrualViews(BaseTest):

    def setUp(self):
        self.accruals = reverse('stocks:dividends')
        self.users_accruals = reverse('stocks:users_dividends')
        self.toggle_accrual =\
            reverse('stocks:toggle_portfolio_div', kwargs={'pk_dividend': 3})

    def test_urls_to_views(self):
        self.assertEqual(resolve(self.accruals).func.view_class,
                         accrual_views.Dividends)
        self.assertEqual(resolve(self.users_accruals).func.view_class,
                         accrual_views.UsersDividends)
        self.assertEqual(resolve(self.toggle_accrual).func.view_class,
                         accrual_views.TogglePortfolioDiv)

    def test_portfolio_accruals_empty_list_GET(self):
        response = self.client_authenticated_no_assets.get(self.accruals)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('accrual_list'), [])
        self.assertEqual(response.context.get('total_results'),
                         {
                             'total_divs_payable': None,
                             'total_divs_received': None,
                             'total_divs_upcoming': None
                         }
                         )

        self.assertTemplateUsed(response, 'dividends/dividend_list.html')

    @patch(EXECUTE_PORTFOLIO_ACCRUAL_VIEW_CONTEXT_SERVICE)
    def test_portfolio_accruals_list_GET(self, accrual_view_service_mocked):

        AccrualItem = Mock()  # need to toggle accrual.id in template

        accrual_view_service_mocked.return_value = {
            'total_results': {'total': '10'},
            'accrual_list': [AccrualItem]
        }

        response = self.client_authenticated.get(self.accruals)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context.get('accrual_list'), [AccrualItem])
        self.assertEqual(response.context.get('total_results'), {'total': '10'})
        self.assertEqual(response.context.get('page_title'), "Dividend list")

        self.assertTemplateUsed(response, 'dividends/dividend_list.html')

    def test_toggle_portfolio_accrual_GET(self):

        self.assertFalse(self.accrual_of_portfolio3.is_received)

        response = self.client_authenticated.get(self.toggle_accrual)

        accrual_of_portfolio3 = AccrualsOfPortfolio.objects.get(
            portfolio=self.accrual_of_portfolio3.portfolio,
            dividend=self.accrual_of_portfolio3.dividend
        )

        self.assertTrue(accrual_of_portfolio3.is_received)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.accruals)
