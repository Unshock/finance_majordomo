from django.urls import path
from finance_majordomo.dividends import views

urlpatterns = [
    path('', views.Dividends.as_view(), name='dividends'),
    path('my/', views.UsersDividends.as_view(), name='users_dividends'),
    path("add_dividend/<int:pk_dividend>/", views.AddDivToUser.as_view(),
         name="add_div_to_user"),
    path("remove_dividend/<int:pk_dividend>/", views.RemoveDivFromUser.as_view(),
         name="remove_div_from_user"),
]