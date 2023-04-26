from django.urls import path
from finance_majordomo.dividends import views

urlpatterns = [
    path('', views.Dividends.as_view(), name='dividends'),
    path('my/', views.UsersDividends.as_view(), name='users_dividends'),

]