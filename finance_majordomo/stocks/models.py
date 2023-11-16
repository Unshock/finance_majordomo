from django.db import models
from django.core.validators import MinLengthValidator
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from ..transactions.services.transaction_calculation_services import \
    get_purchase_price
from ..users.models import User, Portfolio


class Asset(models.Model):
    asset_types = [
        ('stocks', 'stocks'),
        ('bonds', 'bonds'),
        ('currencies', 'currencies'),
        ('funds', 'funds')
    ]

    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")

    asset_type = models.CharField(max_length=20,
                                  choices=asset_types,
                                  verbose_name='Тип актива')

    secid = models.CharField(
        max_length=30,
        verbose_name="ID инструмента",
        unique=True
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Имя акции"
    )

    isin = models.CharField(
        max_length=100,
        verbose_name="ISIN",
        blank=True,
        unique=True
    )

    currency = models.CharField(
        max_length=10,
        verbose_name="Валюта номинала",
        blank=True
    )

    issuedate = models.DateField(
        verbose_name="Дата начала торгов",
        blank=True,
        null=True
    )

    latname = models.CharField(
        max_length=100,
        verbose_name="Английское наименование",
        blank=True
    )

    isqualifiedinvestors = models.BooleanField(
        verbose_name="Бумаги для квалифицированных инвесторов",
        blank=True
    )

    morningsession = models.BooleanField(
        verbose_name="Допуск к утренней дополнительной торговой сессии",
        blank=True
    )

    eveningsession = models.BooleanField(
        verbose_name="Допуск к вечерней дополнительной торговой сессии",
        blank=True
    )

    typename = models.CharField(
        max_length=100,
        verbose_name="Вид/категория ценной бумаги",
        blank=True
    )

    group = models.CharField(
        max_length=100,
        verbose_name="Код типа инструмента",
        blank=True
    )

    type = models.CharField(
        max_length=100,
        verbose_name="Тип бумаги",
        blank=True
    )

    groupname = models.CharField(
        max_length=100,
        verbose_name="Тип инструмента",
        blank=True
    )

    primary_boardid = models.CharField(
        max_length=100,
        verbose_name="Основной режим торгов",
        blank=True
    )

    portfolios = models.ManyToManyField(
        Portfolio,
        through='AssetOfPortfolio',
        through_fields=('asset', 'portfolio'),
        related_name='asset',
    )

    users = models.ManyToManyField(
        User,
        through='AssetsOfUser',
        through_fields=('asset', 'user'),
        related_name='asset1'
    )

    latest_accrual_update = models.DateField(
        verbose_name='Дата последнего обновления информации о начислениях',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.latname

    def get_delete_url(self):
        return reverse("delete_asset", kwargs={'pk': self.pk})

    def get_related_object(self):
        if self.group == "stock_shares":
            return getattr(self, 'stock')
        elif self.group == "stock_bonds":
            return getattr(self, 'bond')


class Stock(Asset):
    latest_dividend_update = models.DateField(
        verbose_name='Дата последнего обновления информации о дивидендах',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.latname

    def get_delete_url(self):
        return reverse("delete_stock", kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['creation_date', 'secid', 'name']


class StocksOfUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Акции пользователя"
        verbose_name_plural = "Акции пользователей"
        ordering = ['stock']


class Bond(Asset):
    startdatemoex = models.DateField(
        verbose_name="Дата начала торгов на MOEX",
        blank=True
    )
    buybackdate = models.DateField(
        verbose_name="Дата байбека",
        blank=True,
        null=True
    )
    matdate = models.DateField(
        verbose_name="Дата погашения",
        blank=True
    )
    couponpercent = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Текущий процент",
        blank=True,
        null=True
    )
    couponfrequency = models.IntegerField(
        verbose_name="Частота выплаты купона в год",
        blank=True
    )
    couponvalue = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Текущий купон",
        blank=True,
        null=True
    )
    days_to_redemption = models.IntegerField(
        verbose_name="Дней до погашения",
        blank=True,
        null=True
    )
    latest_coupon_update = models.DateField(
        verbose_name='Дата последнего обновления информации о купонах',
        blank=True,
        null=True
    )

    face_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Номинал",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.latname

    def get_delete_url(self):
        return reverse("delete_stock", kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Облигация"
        verbose_name_plural = "Облигации"
        ordering = ['creation_date', 'secid', 'name']


class BondOfUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    bond = models.ForeignKey(
        Bond,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Облигации пользователя"
        verbose_name_plural = "Облигации пользователей"
        ordering = ['bond']


class ProdCalendar(models.Model):
    date_status_choice = [
        ('0', 'Working'),
        ('1', 'Nonworking'),
    ]

    date = models.DateField(
        max_length=10,
        verbose_name='Дата'
    )

    date_status = models.CharField(
        max_length=10,
        choices=date_status_choice,
        verbose_name='Статус дня'
    )

    class Meta:
        ordering = ['date', 'date_status']


class AssetsHistoricalData(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    tradedate = models.DateField()
    numtrades = models.IntegerField(null=True)
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    open = models.DecimalField(max_digits=13, decimal_places=5, null=True)
    low = models.DecimalField(max_digits=13, decimal_places=5, null=True)
    high = models.DecimalField(max_digits=13, decimal_places=5, null=True)
    legalcloseprice = models.DecimalField(max_digits=13, decimal_places=5)
    waprice = models.DecimalField(max_digits=13, decimal_places=5, null=True)
    close = models.DecimalField(max_digits=13, decimal_places=5, null=True)
    volume = models.IntegerField(null=True)

    waval = models.DecimalField(max_digits=13, decimal_places=5, null=True)
    trendclspr = models.DecimalField(max_digits=7, decimal_places=3, null=True)

    couponpercent = models.DecimalField(max_digits=13, decimal_places=5,
                                        null=True)
    couponvalue = models.DecimalField(max_digits=13, decimal_places=5,
                                      null=True)
    yieldclose = models.DecimalField(max_digits=13, decimal_places=5, null=True)

    is_closed = models.BooleanField(blank=False)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['asset', 'tradedate']


# class SharesHistoricalData(models.Model):
#     share = models.ForeignKey(Stock, on_delete=models.CASCADE)
# 
#     tradedate = models.DateField()
#     numtrades = models.IntegerField(null=True)
#     value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
#     open = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     low = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     high = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     legalcloseprice = models.DecimalField(max_digits=13, decimal_places=5)
#     waprice = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     close = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     volume = models.IntegerField(null=True)
# 
#     waval = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     trendclspr = models.DecimalField(max_digits=7, decimal_places=3, null=True)
# 
#     is_closed = models.BooleanField(blank=False)
#     update_time = models.DateTimeField(blank=True, null=True)
# 
#     class Meta:
#         unique_together = ['share', 'tradedate']


# class BondsHistoricalData(models.Model):
#     bond = models.ForeignKey(Bond, on_delete=models.CASCADE)
# 
#     tradedate = models.DateField()
#     numtrades = models.IntegerField(null=True)
#     value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
#     open = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     low = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     high = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     legalcloseprice = models.DecimalField(max_digits=13, decimal_places=5)
#     waprice = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     close = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     volume = models.IntegerField(null=True)
# 
#     couponpercent = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     couponvalue = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     yieldclose = models.DecimalField(max_digits=13, decimal_places=5, null=True)
# 
# 
#     #waval = models.DecimalField(max_digits=13, decimal_places=5, null=True)
#     #trendclspr = models.DecimalField(max_digits=7, decimal_places=3, null=True)
# 
#     is_closed = models.BooleanField(blank=False)
#     update_time = models.DateTimeField(blank=True, null=True)
# 
#     class Meta:
#         unique_together = ['bond', 'tradedate']


class AssetOfPortfolio(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE
    )

    #def get_purchase_price(self):
    #    return get_purchase_price(self.portfolio.id, self.asset.id)

    class Meta:
        verbose_name = "Объекты портфеля"
        verbose_name_plural = "Объекты портфеля"
        ordering = ['portfolio']


class AssetsOfUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Активы пользователя"
        verbose_name_plural = "Активы пользователей"
        ordering = ['user']
