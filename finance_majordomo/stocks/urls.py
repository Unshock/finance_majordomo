from django.urls import path
from finance_majordomo.stocks import views

urlpatterns = [
    path('', views.Stocks.as_view(), name='stocks'),
    path('my/', views.UsersStocks.as_view(), name='users_stocks'),
    path('add/', views.AddStock.as_view(), name='add_stock'),
    path('<int:pk>/delete/', views.DeleteStock.as_view(), name='delete_stock'),

]