from django.urls import path
from finance_majordomo import views as v
from finance_majordomo.stocks.views \
    import accrual_views, asset_views, search_views, transaction_views

app_name = 'stocks'

urlpatterns = [
    path('', v.index, name='home'),

    path('search/', search_views.Search.as_view(), name='search'),
    path('stocks/', asset_views.Stocks.as_view(), name='stocks'),
    path('stocks/my/', asset_views.PortfolioAssets.as_view(),
         name='users_stocks'),
    path('stocks/add/', asset_views.AddStock.as_view(), name='add_stock'),
    path('stocks/<int:pk>/delete/', asset_views.DeleteStock.as_view(),
         name='delete_asset'),

    path('dividends/', accrual_views.Accruals.as_view(),
         name='accruals'),
    path('dividends/my', accrual_views.UsersDividends.as_view(),
         name='users_dividends'),
    path('dividends/toggle_dividend/<int:pk_accrual>', accrual_views.
         TogglePortfolioDiv.as_view(), name="toggle_portfolio_div"),

    path('transactions', transaction_views.TransactionList.as_view(),
         name="transactions"),
    path('transactions/my/', transaction_views.UsersTransactionList.as_view(),
         name="user_transactions"),
    path('transactions/create/', transaction_views.AddTransaction.as_view(),
         name="add_transaction"),
    path('transactions/<int:pk>/delete/', transaction_views.
         DeleteTransaction.as_view(), name="delete_transaction")
]
