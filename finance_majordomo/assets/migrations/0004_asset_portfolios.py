# Generated by Django 4.2 on 2023-09-16 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_portfolio_is_current"),
        ("assets", "0003_assetofportfolio"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="portfolios",
            field=models.ManyToManyField(
                related_name="asset",
                through="assets.AssetOfPortfolio",
                to="users.portfolio",
            ),
        ),
    ]