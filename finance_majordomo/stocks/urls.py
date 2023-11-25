from django.urls import path
from finance_majordomo.stocks import views
from finance_majordomo import views as v

app_name = 'stocks'

urlpatterns = [
    path('', v.index, name='home'),
    path(
        'search/',
        views.search_views.Search.as_view(),
        name='search'
    ),
    path(
        'stocks/',
        views.asset_views.Stocks.as_view(),
        name='stocks'
    ),
    path(
        'stocks/my/',
        views.asset_views.PortfolioAssets.as_view(),
        name='users_stocks'
    ),
    path(
        'stocks/add/',
        views.asset_views.AddStock.as_view(),
        name='add_stock'
    ),
    path(
        'stocks/<int:pk>/delete/',
        views.asset_views.DeleteStock.as_view(),
        name='delete_asset'
    ),
    path(
        'dividends/',
        views.accrual_views.Dividends.as_view(),
        name='dividends'
    ),
    path(
        'dividends/my',
        views.accrual_views.UsersDividends.as_view(),
        name='users_dividends'
    ),
    path(
        'dividends/toggle_dividend/<int:pk_dividend>',
        views.accrual_views.TogglePortfolioDiv.as_view(),
        name="toggle_portfolio_div"
    ),
    path(
        'transactions',
        views.transaction_views.TransactionList.as_view(),
        name="transactions"
    ),
    path(
        'transactions/my/',
        views.transaction_views.UsersTransactionList.as_view(),
        name="user_transactions"
    ),
    path(
        'transactions/create/',
        views.transaction_views.AddTransaction.as_view(),
        name="add_transaction"
    ),
    path(
        'transactions/<int:pk>/delete/',
        views.transaction_views.DeleteTransaction.as_view(),
        name="delete_transaction"
    )
]
