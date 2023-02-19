"""finance_majordomo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from finance_majordomo import views
from finance_majordomo.users.views import LoginUser, logout_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),

    path("users/", include("finance_majordomo.users.urls")),
    path("stocks/", include("finance_majordomo.stocks.urls")),
    path("transactions/", include("finance_majordomo.transactions.urls")),

    path("login/", LoginUser.as_view(), name="login"),
    path("logout/", logout_user, name="logout")
]
