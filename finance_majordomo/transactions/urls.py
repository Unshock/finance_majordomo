from django.urls import path
from finance_majordomo.transactions import views


urlpatterns = [
    path("", views.TransactionList.as_view(), name="transactions"),
    path("my/", views.UsersTransactionList.as_view(), name="user_transactions"),
    path("create/", views.AddTransaction.as_view(), name="add_transaction"),
    #path("create/<int:asset_id>/", views.AddTransaction.as_view(), name="add_transaction"),
    #path("<int:user_id>/add_transaction/<int:stock_id>", views.AddTransaction.as_view(), name="add_transaction"),
    path('<int:pk>/delete/', views.DeleteTransaction.as_view(), name='delete_transaction'),
]
