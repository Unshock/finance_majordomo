from django.urls import path
from finance_majordomo.dividends import views

urlpatterns = [
    path('', views.Dividends.as_view(), name='dividends'),
    path('my/', views.UsersDividends.as_view(), name='users_dividends'),
    path('toggle_dividend/<int:pk_dividend>/',
         views.TogglePortfolioDiv.as_view(), name="toggle_portfolio_div"),

]