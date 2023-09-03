from django.urls import path
from finance_majordomo.search import views

urlpatterns = [
    path('', views.Search.as_view(), name='search')

]