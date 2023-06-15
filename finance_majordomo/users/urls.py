from django.urls import path
from finance_majordomo.users import views


urlpatterns = [
    path("", views.UserList.as_view(), name="users"),
    #path("<int:pk>/delete/", views.DeleteUser.as_view(), name="delete_user"),
    #path("<int:pk>/update/", views.UpdateUser.as_view(), name="update_user"),
    path("set_fields/", views.SetFieldsToDisplay.as_view(), name="set_fields"),
    path("create/", views.CreateUser.as_view(), name="create_user"),
    path("add_stock/<int:pk_stock>/", views.AddStockToUser.as_view(), name="add_stock_to_user"),
    #path("<int:user_id>/add_transaction/<int:stock_id>", views.AddTransaction.as_view(), name="add_transaction"),
]