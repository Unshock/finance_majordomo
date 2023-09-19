# Generated by Django 4.2 on 2023-09-18 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_portfolio_is_current"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSettings",
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
                ("show_ticker", models.BooleanField(default=True)),
                ("show_name", models.BooleanField(default=True)),
                ("show_currency", models.BooleanField(default=True)),
                ("show_quantity", models.BooleanField(default=True)),
                ("show_purchase_price", models.BooleanField(default=True)),
                ("show_current_price", models.BooleanField(default=True)),
                ("show_dividends_received", models.BooleanField(default=True)),
                ("show_money_result_without_divs", models.BooleanField(default=True)),
                ("show_money_result_with_divs", models.BooleanField(default=True)),
                ("show_percent_result", models.BooleanField(default=True)),
                ("show_rate_of_return", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]