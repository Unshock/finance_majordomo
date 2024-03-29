# Generated by Django 4.2 on 2023-11-22 17:10

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_remove_user_fields_to_display_and_more"),
        ("stocks", "0010_dividend_dividendsofuser_dividend_users_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creation date"
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("BUY", "Buy"), ("SELL", "Sell")],
                        max_length=4,
                        validators=[django.core.validators.MinLengthValidator(1)],
                        verbose_name="Transaction type",
                    ),
                ),
                (
                    "date",
                    models.DateField(max_length=10, verbose_name="Transaction date"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=8, verbose_name="Transaction price"
                    ),
                ),
                (
                    "accrued_interest",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        max_digits=8,
                        null=True,
                        verbose_name="Accrued Interest",
                    ),
                ),
                (
                    "fee",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        max_digits=8,
                        null=True,
                        verbose_name="Transaction fee",
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        verbose_name="Transaction quantity",
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stocks.asset",
                        verbose_name="Asset",
                    ),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.portfolio",
                        verbose_name="Transaction portfolio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Транзакция",
                "verbose_name_plural": "Транзакции",
                "ordering": ["creation_date", "asset", "portfolio"],
            },
        ),
    ]
